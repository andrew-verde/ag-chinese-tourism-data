#!/usr/bin/env python3
"""Download Xiaohongshu Kanazawa search note results to a CSV file.

Requires playwright:
    python3 -m pip install -r requirements.txt
    playwright install chromium

Run:
    python3 xhs_kanazawa_reviews.py --output kanazawa_xhs_reviews.csv
"""
import argparse
import time
import urllib.parse
from pathlib import Path

from pipeline_io import UnsafeWriteError, safe_write_csv


FIELDNAMES = ['note_id', 'title', 'note_url', 'author', 'author_url']
KEY_FIELDS = ['note_id', 'note_url']


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


def save_csv(rows, output_path: Path, *, replace=False, allow_shrink=False, allow_empty=False):
    return safe_write_csv(
        rows,
        output_path,
        FIELDNAMES,
        key_fields=KEY_FIELDS,
        merge_existing=not replace,
        allow_empty=allow_empty,
        allow_shrink=allow_shrink,
    )


def main():
    parser = argparse.ArgumentParser(description='Scrape Xiaohongshu Kanazawa search notes.')
    parser.add_argument('--keyword', default='金泽旅游', help='Search keyword to query on Xiaohongshu')
    parser.add_argument('--output', default='kanazawa_xhs_reviews.csv', help='CSV output file path')
    parser.add_argument('--scrolls', type=int, default=16, help='Number of scroll steps to load more results')
    parser.add_argument('--delay', type=float, default=1.8, help='Seconds to wait after each scroll')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--replace', action='store_true', help='Replace the output instead of merging with existing rows')
    parser.add_argument('--allow-shrink', action='store_true', help='Allow an intentional replace that writes fewer rows than the existing CSV')
    parser.add_argument('--allow-empty', action='store_true', help='Allow writing an intentionally empty CSV')
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
            total_rows, backup_path = save_csv(
                notes,
                Path(args.output),
                replace=args.replace,
                allow_shrink=args.allow_shrink,
                allow_empty=args.allow_empty,
            )
            if backup_path:
                print(f'Backed up previous output to {backup_path}')
            print(f'Saved {total_rows} total rows to {args.output}')

        except UnsafeWriteError as e:
            raise SystemExit(str(e)) from e
        except Exception as e:
            raise SystemExit(f'Error: {e}') from e
        finally:
            browser.close()


if __name__ == '__main__':
    main()
