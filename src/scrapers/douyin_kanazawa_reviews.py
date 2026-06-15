#!/usr/bin/env python3
"""Download Douyin destination search video results to a CSV file.

Requires playwright:
    python3 -m pip install -r requirements.txt
    playwright install chromium

Run:
    python3 -m src.scrapers.douyin_kanazawa_reviews --destination kanazawa
    python3 -m src.scrapers.douyin_kanazawa_reviews --destination fukui
"""
import argparse
import time
import urllib.parse
from pathlib import Path

from src.pipeline_io import UnsafeWriteError, safe_write_csv


FIELDNAMES = ['video_id', 'title', 'video_url', 'author']
KEY_FIELDS = ['video_id', 'video_url']
DESTINATION_PRESETS = {
    'kanazawa': {
        'output': 'data/raw/social/kanazawa_douyin_reviews.csv',
        'keywords': [
            '金泽旅游',
            '金泽旅行',
            '金泽美食',
            '石川旅游',
            '石川旅行',
            '石川县旅游',
            '金沢旅行',
        ],
    },
    'fukui': {
        'output': 'data/raw/social/fukui_douyin_reviews.csv',
        'keywords': [
            '福井',
            '福井旅游',
            '福井旅行',
            '福井美食',
            '福井温泉',
            '福井景点',
            '永平寺',
            '东寻坊',
            '越前',
        ],
    },
}


def make_search_url(keyword: str) -> str:
    encoded = urllib.parse.quote(keyword)
    return f"https://www.douyin.com/search/{encoded}"


def collect_videos(page):
    return page.evaluate(
        r"""
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


def merge_video_records(existing, new_videos):
    for video in new_videos:
        key = video.get('video_id') or video.get('video_url')
        if key:
            existing[key] = video


def scroll_to_load(page, iterations=12, delay=1.5, no_growth_limit=4):
    videos_by_key = {}
    merge_video_records(videos_by_key, collect_videos(page))
    previous_count = len(videos_by_key)
    no_growth_count = 0

    for scroll_number in range(iterations):
        page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
        time.sleep(delay)
        merge_video_records(videos_by_key, collect_videos(page))
        current_count = len(videos_by_key)
        if current_count <= previous_count:
            no_growth_count += 1
        else:
            no_growth_count = 0
            previous_count = current_count

        if no_growth_count >= no_growth_limit:
            print(f'Stopping after {scroll_number + 1} scrolls with no new videos in the last {no_growth_limit} scrolls.')
            break

    return list(videos_by_key.values())


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


def parse_keywords(values: list[str]) -> list[str]:
    keywords = []
    seen = set()
    for value in values:
        for keyword in value.split(','):
            keyword = keyword.strip()
            if keyword and keyword not in seen:
                seen.add(keyword)
                keywords.append(keyword)
    return keywords


def main():
    parser = argparse.ArgumentParser(description='Scrape Douyin destination search videos.')
    parser.add_argument(
        '--destination',
        choices=sorted(DESTINATION_PRESETS),
        default='kanazawa',
        help='Destination keyword preset and default output path',
    )
    parser.add_argument(
        '--keyword',
        action='append',
        help='Search keyword to query on Douyin. Repeat or pass comma-separated values. Defaults to the destination preset.',
    )
    parser.add_argument('--output', help='CSV output file path. Defaults to the destination preset output.')
    parser.add_argument('--scrolls', type=int, default=16, help='Number of scroll steps to load more results')
    parser.add_argument('--delay', type=float, default=1.8, help='Seconds to wait after each scroll')
    parser.add_argument('--no-growth-limit', type=int, default=4, help='Stop a keyword after this many consecutive scrolls add no new videos')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--replace', action='store_true', help='Replace the output instead of merging with existing rows')
    parser.add_argument('--allow-shrink', action='store_true', help='Allow an intentional replace that writes fewer rows than the existing CSV')
    parser.add_argument('--allow-empty', action='store_true', help='Allow writing an intentionally empty CSV')
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    preset = DESTINATION_PRESETS[args.destination]
    keywords = parse_keywords(args.keyword or preset['keywords'])
    if not keywords:
        raise SystemExit('At least one non-empty keyword is required.')
    output_path = Path(args.output or preset['output'])
    print(f'Collecting {len(keywords)} Douyin keyword(s) for {args.destination}: {", ".join(keywords)}')

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=args.headless)
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        )
        page = context.new_page()

        try:
            videos_by_key = {}
            for keyword in keywords:
                search_url = make_search_url(keyword)
                print(f'Opening search: {search_url}')
                page.goto(search_url, timeout=60000)
                time.sleep(5)  # Wait for initial load

                keyword_videos = scroll_to_load(
                    page,
                    iterations=args.scrolls,
                    delay=args.delay,
                    no_growth_limit=args.no_growth_limit,
                )
                before_count = len(videos_by_key)
                merge_video_records(videos_by_key, keyword_videos)
                added_count = len(videos_by_key) - before_count
                print(f'Keyword "{keyword}" collected {len(keyword_videos)} visible/loaded videos, {added_count} new to this run')

            videos = list(videos_by_key.values())
            print(f'Found {len(videos)} unique videos')
            total_rows, backup_path = save_csv(
                videos,
                output_path,
                replace=args.replace,
                allow_shrink=args.allow_shrink,
                allow_empty=args.allow_empty,
            )
            if backup_path:
                print(f'Backed up previous output to {backup_path}')
            print(f'Saved {total_rows} total rows to {output_path}')

        except UnsafeWriteError as e:
            raise SystemExit(str(e)) from e
        except Exception as e:
            raise SystemExit(f'Error: {e}') from e
        finally:
            browser.close()


if __name__ == '__main__':
    main()
