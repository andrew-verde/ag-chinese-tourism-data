#!/usr/bin/env python3
"""Download Douyin Kanazawa search video results to a CSV file.

Requires playwright:
    python3 -m pip install -r requirements.txt
    playwright install chromium

Run:
    python3 douyin_kanazawa_reviews.py --output kanazawa_douyin_reviews.csv
"""
import argparse
import csv
import shutil
import time
import urllib.parse
from pathlib import Path


def make_search_url(keyword: str) -> str:
    encoded = urllib.parse.quote(keyword)
    return f"https://www.douyin.com/search/{encoded}"


def collect_videos(page):
    return page.evaluate(
        """
        () => {
          const normalize = (value) => value.replace(/\s+/g, ' ').trim();
          const video_items = Array.from(document.querySelectorAll('[data-e2e="search-card-item"]'));
          const items = [];

          for (const item of video_items) {
            const title_elem = item.querySelector('[data-e2e="search-card-title"]');
            const title = title_elem ? normalize(title_elem.innerText || '') : '';

            const author_elem = item.querySelector('[data-e2e="search-card-user-name"]');
            const author = author_elem ? normalize(author_elem.innerText || '') : '';

            const link_elem = item.querySelector('a[href*="/video/"]');
            const video_url = link_elem ? new URL(link_elem.getAttribute('href'), location.origin).href : '';

            const video_id = video_url ? video_url.split('/video/')[1]?.split('?')[0] : '';

            if (title && video_url) {
              items.push({
                title: title,
                video_url: video_url,
                video_id: video_id,
                author: author,
              });
            }
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
        videos = collect_videos(page)
        if len(videos) == previous_count:
            break
        previous_count = len(videos)
    return videos


def save_csv(rows, output_path: Path):
    if not rows:
        print(f'No rows collected; leaving existing output unchanged: {output_path}')
        return False

    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp_path = output_path.with_suffix(output_path.suffix + '.tmp')
    backup_path = output_path.with_suffix(output_path.suffix + '.bak')

    with temp_path.open('w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=['video_id', 'title', 'video_url', 'author'])
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    if output_path.exists():
        shutil.copy2(output_path, backup_path)
        print(f'Backed up previous output to {backup_path}')
    temp_path.replace(output_path)
    return True


def main():
    parser = argparse.ArgumentParser(description='Scrape Douyin Kanazawa search videos.')
    parser.add_argument('--keyword', default='金泽旅游', help='Search keyword to query on Douyin')
    parser.add_argument('--output', default='kanazawa_douyin_reviews.csv', help='CSV output file path')
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
            time.sleep(5)  # Wait for initial load

            print('Collecting videos...')
            videos = scroll_to_load(page, iterations=args.scrolls, delay=args.delay)

            print(f'Found {len(videos)} videos')
            if save_csv(videos, Path(args.output)):
                print(f'Saved to {args.output}')

        except Exception as e:
            print(f'Error: {e}')
        finally:
            browser.close()


if __name__ == '__main__':
    main()
