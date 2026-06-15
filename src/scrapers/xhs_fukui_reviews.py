#!/usr/bin/env python3
"""Download Xiaohongshu Fukui search note results to a CSV file.

Requires playwright:
    python3 -m pip install -r requirements.txt
    playwright install chromium

Run:
    python3 xhs_fukui_reviews.py --output fukui_xhs_reviews.csv
"""
import argparse
import time
import urllib.parse
from pathlib import Path

from src.pipeline_io import UnsafeWriteError, safe_write_csv


FIELDNAMES = ['note_id', 'title', 'note_url', 'author', 'author_url']
KEY_FIELDS = ['note_id', 'note_url']
DEFAULT_KEYWORDS = [
    '福井',
    '福井旅游',
    '福井旅行',
    '福井美食',
    '福井温泉',
    '福井景点',
    '永平寺',
    '东寻坊',
    '越前',
]


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


def merge_note_records(existing, new_notes):
    for note in new_notes:
        key = note.get('note_url') or note.get('note_id')
        if key:
            existing[key] = note


def scroll_to_load(page, iterations=12, delay=1.5, no_growth_limit=4):
    notes_by_key = {}
    merge_note_records(notes_by_key, collect_notes(page))
    previous_count = len(notes_by_key)
    no_growth_count = 0

    for scroll_number in range(iterations):
        page.evaluate('window.scrollBy(0, document.body.scrollHeight)')
        time.sleep(delay)
        merge_note_records(notes_by_key, collect_notes(page))
        current_count = len(notes_by_key)
        if current_count <= previous_count:
            no_growth_count += 1
        else:
            no_growth_count = 0
            previous_count = current_count

        if no_growth_count >= no_growth_limit:
            print(f'Stopping after {scroll_number + 1} scrolls with no new notes in the last {no_growth_limit} scrolls.')
            break

    return list(notes_by_key.values())


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
    parser = argparse.ArgumentParser(description='Scrape Xiaohongshu Fukui search notes.')
    parser.add_argument(
        '--keyword',
        action='append',
        help='Search keyword to query on Xiaohongshu. Repeat or pass comma-separated values. Defaults to a Fukui keyword set.',
    )
    parser.add_argument('--output', default='data/raw/social/fukui_xhs_reviews.csv', help='CSV output file path')
    parser.add_argument('--scrolls', type=int, default=16, help='Number of scroll steps to load more results')
    parser.add_argument('--delay', type=float, default=1.8, help='Seconds to wait after each scroll')
    parser.add_argument('--no-growth-limit', type=int, default=4, help='Stop only after this many consecutive scrolls add no new notes')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--replace', action='store_true', help='Replace the output instead of merging with existing rows')
    parser.add_argument('--allow-shrink', action='store_true', help='Allow an intentional replace that writes fewer rows than the existing CSV')
    parser.add_argument('--allow-empty', action='store_true', help='Allow writing an intentionally empty CSV')
    args = parser.parse_args()

    from playwright.sync_api import sync_playwright

    keywords = parse_keywords(args.keyword or DEFAULT_KEYWORDS)
    if not keywords:
        raise SystemExit('At least one non-empty keyword is required.')
    print(f'Collecting {len(keywords)} search keyword(s): {", ".join(keywords)}')

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=args.headless)
        page = browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36'
        )
        notes_by_key = {}
        for keyword in keywords:
            search_url = make_search_url(keyword)
            print(f'Opening search: {search_url}')
            page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_selector('a[href^="/search_result/"]', timeout=20000)
            time.sleep(2)

            keyword_notes = scroll_to_load(
                page,
                iterations=args.scrolls,
                delay=args.delay,
                no_growth_limit=args.no_growth_limit,
            )
            before_count = len(notes_by_key)
            merge_note_records(notes_by_key, keyword_notes)
            added_count = len(notes_by_key) - before_count
            print(f'Keyword "{keyword}" collected {len(keyword_notes)} visible/loaded notes, {added_count} new to this run')
        browser.close()

    if not notes_by_key and not args.allow_empty:
        raise SystemExit(
            'No notes were found. It may require a logged-in session or a different search path. '
            'Existing output was left unchanged.'
        )

    rows = list(notes_by_key.values())
    print(f'Collected {len(rows)} note records')
    try:
        total_rows, backup_path = save_csv(
            rows,
            Path(args.output),
            replace=args.replace,
            allow_shrink=args.allow_shrink,
            allow_empty=args.allow_empty,
        )
    except UnsafeWriteError as exc:
        raise SystemExit(str(exc)) from exc
    if backup_path:
        print(f'Backed up previous output to {backup_path}')
    print(f'Saved {total_rows} total rows to {args.output}')


if __name__ == '__main__':
    main()
