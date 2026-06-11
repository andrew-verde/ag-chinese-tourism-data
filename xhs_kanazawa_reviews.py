#!/usr/bin/env python3
"""Download Xiaohongshu Kanazawa search note results to a CSV file.

Requires playwright:
    python3 -m pip install -r requirements.txt
    playwright install chromium

Run:
    python3 xhs_kanazawa_reviews.py --output kanazawa_xhs_reviews.csv
"""
import argparse
import csv
import shutil
import time
import urllib.parse
from pathlib import Path


def make_search_url(keyword: str) -> str:
    encoded = urllib.parse.quote(keyword)
    return f"https://www.xiaohongshu.com/search_result/?keyword={encoded}&source=web_search_result_notes&type=51"


def collect_notes(page):
    return page.evaluate(
        r"""
        () => {
          const normalize = (value) => value.replace(/\s+/g, ' ').trim();
          const anchors = Array.from(document.querySelectorAll('a[href^="/search_result/"]'));
          const seen = new Set();
          const items = [];

          for (const anchor of anchors) {
            const text = normalize(anchor.innerText || '');
            if (!text || text.length < 4) continue;
            if (/^\d+$/.test(text)) continue;

            const href = anchor.href;
            if (!href.includes('/search_result/')) continue;
            if (seen.has(href)) continue;
            seen.add(href);

            let container = anchor.parentElement;
            while (container && !container.querySelector('a[href^="/user/profile/"]')) {
              container = container.parentElement;
            }

            const authorAnchor = container ? container.querySelector('a[href^="/user/profile/"]') : null;
            const author = authorAnchor ? normalize(authorAnchor.innerText || '') : '';
            const author_url = authorAnchor ? new URL(authorAnchor.getAttribute('href'), location.origin).href : '';
            const note_id = href.split('/').pop().split('?')[0];

            items.push({
              title: text,
              note_url: href,
              note_id,
              author,
              author_url,
            });
          }

          return items;
        }
        """
    )


def scroll_to_load(page, iterations=12, delay=1.5):
    previous_count = 0
    for _ in range(iterations):
        page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
        time.sleep(delay)
        notes = collect_notes(page)
        if len(notes) == previous_count:
            break
        previous_count = len(notes)
    return notes


def save_csv(rows, output_path: Path):
    if not rows:
        print(f'No rows collected; leaving existing output unchanged: {output_path}')
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + '.tmp')
    backup_path = output_path.with_suffix(output_path.suffix + '.bak')

    with temp_path.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['note_id', 'title', 'note_url', 'author', 'author_url'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    if output_path.exists():
        shutil.copy2(output_path, backup_path)
        print(f'Backed up previous output to {backup_path}')
    temp_path.replace(output_path)
    return True


def main():
    parser = argparse.ArgumentParser(description='Scrape Xiaohongshu Kanazawa search notes.')
    parser.add_argument('--keyword', default='金泽旅游', help='Search keyword to query on Xiaohongshu')
    parser.add_argument('--output', default='kanazawa_xhs_reviews.csv', help='CSV output file path')
    parser.add_argument('--scrolls', type=int, default=16, help='Number of scroll steps to load more results')
    parser.add_argument('--delay', type=float, default=1.8, help='Seconds to wait after each scroll')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    search_url = make_search_url(args.keyword)
    print(f'Opening search: {search_url}')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()

        try:
            page.goto(search_url, timeout=60000)
            time.sleep(3)  # Wait for initial load

            print('Collecting notes...')
            notes = scroll_to_load(page, iterations=args.scrolls, delay=args.delay)

            print(f'Found {len(notes)} notes')
            if save_csv(notes, Path(args.output)):
                print(f'Saved to {args.output}')

        except Exception as e:
            print(f'Error: {e}')
        finally:
            browser.close()


if __name__ == '__main__':
    main()
