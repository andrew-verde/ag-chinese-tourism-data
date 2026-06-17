#!/usr/bin/env python3
"""Manual-assisted Xiaohongshu note body capture.

This tool opens a logged-in Chromium session and waits while a person manually
opens a Xiaohongshu note. It never clicks search results or navigates through
results on its own. Press Enter in the terminal to capture the currently visible
note into CSV.
"""

from __future__ import annotations

import argparse
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.pipeline_io import UnsafeWriteError, safe_write_csv


FIELDNAMES = [
    "note_id",
    "title",
    "body_text",
    "content",
    "note_url",
    "author",
    "author_url",
    "posted_at",
    "captured_at",
    "source_url",
]
KEY_FIELDS = ["note_id", "note_url"]
DEFAULT_OUTPUT = "data/raw/social/fukui_xhs_reviews.csv"
DEFAULT_START_URL = "https://www.xiaohongshu.com"
DEFAULT_PROFILE_DIR = ".browser-profiles/xhs-manual"


def normalize_text(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def extract_note_id(url: str) -> str:
    patterns = [
        r"/(?:explore|discovery/item|search_result)/([0-9a-zA-Z]+)",
        r"[?&]note_id=([0-9a-zA-Z]+)",
        r"[?&]xsec_token=([^&]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return ""


def clean_title(title: str) -> str:
    title = normalize_text(title)
    for suffix in (" - 小红书", "_小红书", " | 小红书"):
        if title.endswith(suffix):
            title = title[: -len(suffix)].strip()
    return title


def row_from_capture(capture: dict[str, Any], captured_at: str | None = None) -> dict[str, str]:
    note_url = normalize_text(capture.get("note_url"))
    body_text = normalize_text(capture.get("body_text"))
    if not body_text:
        raise ValueError(
            "No visible Xiaohongshu body text found on current page. "
            "Open an individual note, expand text if needed, then capture again."
        )

    title = clean_title(capture.get("title", ""))
    return {
        "note_id": normalize_text(capture.get("note_id")) or extract_note_id(note_url),
        "title": title,
        "body_text": body_text,
        "content": body_text,
        "note_url": note_url,
        "author": normalize_text(capture.get("author")),
        "author_url": normalize_text(capture.get("author_url")),
        "posted_at": normalize_text(capture.get("posted_at")),
        "captured_at": captured_at or utc_now_iso(),
        "source_url": note_url,
    }


def capture_current_note(page) -> dict[str, str]:
    capture = page.evaluate(
        r"""
        () => {
          const normalize = (value) => String(value || '').replace(/\s+/g, ' ').trim();
          const isVisible = (el) => {
            if (!el) return false;
            const style = window.getComputedStyle(el);
            const rect = el.getBoundingClientRect();
            return style.visibility !== 'hidden' &&
              style.display !== 'none' &&
              rect.width > 0 &&
              rect.height > 0;
          };
          const firstText = (selectors) => {
            for (const selector of selectors) {
              for (const el of document.querySelectorAll(selector)) {
                if (!isVisible(el)) continue;
                const text = normalize(el.innerText || el.textContent);
                if (text) return text;
              }
            }
            return '';
          };
          const firstHref = (selectors) => {
            for (const selector of selectors) {
              for (const el of document.querySelectorAll(selector)) {
                if (!isVisible(el)) continue;
                const href = el.getAttribute('href');
                if (href) return new URL(href, location.origin).href;
              }
            }
            return '';
          };
          const meta = (selector) => normalize(document.querySelector(selector)?.content);

          const body = firstText([
            '#detail-desc .note-text',
            '#detail-desc',
            '.note-content .desc',
            '.note-content',
            '.note-detail .desc',
            '.note-detail',
            '[class*="note-content"]',
            '[class*="detail-desc"]',
            '[class*="desc"]'
          ]);
          const title = firstText([
            '#detail-title',
            '.note-content .title',
            '.note-detail .title',
            '[class*="title"] h1',
            'h1'
          ]) || meta('meta[property="og:title"]') || document.title;
          const author = firstText([
            'a[href*="/user/profile/"] .name',
            'a[href*="/user/profile/"]',
            '[class*="author"] [class*="name"]',
            '[class*="user"] [class*="name"]'
          ]);
          const postedAt = firstText([
            '.date',
            '[class*="date"]',
            '[class*="time"]'
          ]);

          return {
            note_url: location.href,
            note_id: '',
            title,
            body_text: body,
            author,
            author_url: firstHref(['a[href*="/user/profile/"]']),
            posted_at: postedAt
          };
        }
        """
    )
    return row_from_capture(capture)


def save_csv(rows: list[dict[str, str]], output_path: Path, *, replace=False, allow_shrink=False):
    return safe_write_csv(
        rows,
        output_path,
        FIELDNAMES,
        key_fields=KEY_FIELDS,
        merge_existing=not replace,
        allow_empty=False,
        allow_shrink=allow_shrink,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Open a browser for manual Xiaohongshu note selection, then capture visible note body text."
    )
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="CSV output path")
    parser.add_argument("--start-url", default=DEFAULT_START_URL, help="Initial page opened in the browser")
    parser.add_argument("--profile-dir", default=DEFAULT_PROFILE_DIR, help="Persistent Chromium profile dir for login")
    parser.add_argument("--headless", action="store_true", help="Run browser headless. Not recommended for manual login.")
    parser.add_argument("--once", action="store_true", help="Capture one note, then exit")
    parser.add_argument("--replace", action="store_true", help="Replace output instead of merging with existing rows")
    parser.add_argument(
        "--allow-shrink",
        action="store_true",
        help="Allow an intentional replace that writes fewer rows than existing CSV",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    from playwright.sync_api import sync_playwright

    profile_dir = Path(args.profile_dir)
    profile_dir.mkdir(parents=True, exist_ok=True)
    output_path = Path(args.output)

    with sync_playwright() as playwright:
        context = playwright.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=args.headless,
            viewport={"width": 1400, "height": 950},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
            ),
        )
        page = context.pages[0] if context.pages else context.new_page()
        if args.start_url:
            page.goto(args.start_url, wait_until="domcontentloaded", timeout=60000)

        print("Browser ready. Manually open a Xiaohongshu note. Script will not click search results.")
        print("Press Enter here to capture current visible note. Type q then Enter to quit.")
        try:
            while True:
                command = input("capture> ").strip().lower()
                if command in {"q", "quit", "exit"}:
                    break

                row = capture_current_note(page)
                if not (row["note_id"] or row["note_url"]):
                    raise SystemExit("Cannot identify note_id or note_url for current page. Open a note page first.")

                try:
                    total_rows, backup_path = save_csv(
                        [row],
                        output_path,
                        replace=args.replace,
                        allow_shrink=args.allow_shrink,
                    )
                except UnsafeWriteError as exc:
                    raise SystemExit(str(exc)) from exc

                if backup_path:
                    print(f"Backed up previous output to {backup_path}")
                print(f"Captured note {row['note_id'] or row['note_url']} with {len(row['body_text'])} body chars.")
                print(f"Saved {total_rows} total rows to {output_path}")
                if args.once:
                    break
        finally:
            context.close()


if __name__ == "__main__":
    main()
