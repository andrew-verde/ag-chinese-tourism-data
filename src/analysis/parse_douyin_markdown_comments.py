#!/usr/bin/env python3
"""Parse manually exported Douyin comment Markdown into analysis-ready CSV.

The input file was exported from a Word/Google Docs handoff, not from Douyin's
DOM or API. That means true post IDs and comment IDs are not available. This
parser keeps academic provenance by assigning stable local row IDs and storing
raw source line spans instead of inventing platform identifiers.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path

from src.pipeline_io import UnsafeWriteError, safe_write_csv


DEFAULT_INPUT = "data/raw/social/fukui_douyin_posts_comments.md"
DEFAULT_OUTPUT = "data/processed/fukui_douyin_comments_from_md.csv"
KEY_FIELDS = ["source_record_id"]
FIELDNAMES = [
    "source_record_id",
    "douyin_post_id",
    "author",
    "author_is_post_author",
    "comment_text",
    "relative_time",
    "ip_location",
    "like_count",
    "author_interaction",
    "expanded_reply_marker",
    "source_start_line",
    "source_end_line",
    "source_block_text",
    "parse_confidence",
    "parse_notes",
]

NOISE_LINES = {
    "",
    "...",
    "DY NOTE DATA",
    "分享",
    "回复",
    "收起",
    "￼",
}
COMMENT_ACTION_LINES = {"分享", "回复", "收起"}
AUTHOR_INTERACTION_LINES = {"作者赞过", "作者回复过"}
TIME_RE = re.compile(
    r"^(?P<time>(刚刚|昨天|前天|\d+\s*(秒|分钟|小时|天|周|月|年)前))"
    r"(?:·(?P<location>[\u4e00-\u9fffA-Za-z0-9_ -]+))?$"
)
EXPANDED_REPLY_RE = re.compile(r"^展开(?:更多|\d+条回复)$")


def clean_line(line: str) -> str:
    """Normalize export artifacts while preserving user-visible text."""
    line = line.replace("\uFFFC", "")
    return re.sub(r"[\t \u3000]+", " ", line).strip()


def is_like_count(line: str) -> bool:
    return bool(re.fullmatch(r"\d+", line.strip()))


def is_avatar_label(line: str) -> bool:
    # Google Docs export preserves many Douyin avatar alt labels as "昵称头像".
    # Treat as UI chrome only when a separate author line follows.
    return len(line) > 2 and line.endswith("头像")


def is_metadata_line(line: str) -> bool:
    return bool(TIME_RE.match(line))


def split_time_location(line: str) -> tuple[str, str]:
    match = TIME_RE.match(line)
    if not match:
        return "", ""
    return match.group("time").replace(" ", ""), (match.group("location") or "").strip()


def previous_content_line(lines: list[str], index: int) -> str:
    """Return nearest meaningful line before a comment block."""
    for previous in range(index - 1, -1, -1):
        line = lines[previous]
        if line and line not in COMMENT_ACTION_LINES and not EXPANDED_REPLY_RE.match(line):
            return line
    return ""


def trim_author_tokens(lines: list[str]) -> tuple[str, bool, list[str]]:
    """Split author metadata from comment text inside one parsed block.

    Two export styles are present:
    1. old plain text: "avatar label / author / comment / time / likes";
    2. newer Docs export: "author / 作者? / ... / comment / time / likes".
    """
    cleaned = [line for line in lines if line not in NOISE_LINES]
    author_is_post_author = False
    if cleaned and is_avatar_label(cleaned[0]) and len(cleaned) >= 2:
        cleaned = cleaned[1:]
    if len(cleaned) >= 2 and cleaned[1] == "作者":
        author_is_post_author = True
        cleaned = [cleaned[0], *cleaned[2:]]
    if not cleaned:
        return "", author_is_post_author, []
    return cleaned[0], author_is_post_author, cleaned[1:]


def candidate_blocks(lines: list[str]) -> list[tuple[int, int, str, str, str, list[str]]]:
    """Find blocks ending in "time/location + like count" metadata.

    The parser walks from each metadata line backward to the prior share/reply
    boundary. This keeps source spans reproducible and avoids interpreting long
    free-text post captions as multiple comments.
    """
    blocks = []
    for time_index, line in enumerate(lines):
        if not is_metadata_line(line):
            continue
        next_index = time_index + 1
        while next_index < len(lines) and lines[next_index] == "":
            next_index += 1
        if next_index >= len(lines) or not is_like_count(lines[next_index]):
            continue

        start = time_index - 1
        while start >= 0 and lines[start] not in COMMENT_ACTION_LINES:
            start -= 1
        start += 1
        while start < time_index and (
            lines[start] in NOISE_LINES or EXPANDED_REPLY_RE.match(lines[start]) or lines[start] in COMMENT_ACTION_LINES
        ):
            start += 1
        if start >= time_index:
            continue

        relative_time, ip_location = split_time_location(line)
        blocks.append((start, next_index, relative_time, ip_location, lines[next_index], lines[start:time_index]))
    return blocks


def parse_comments_from_lines(raw_lines: list[str]) -> tuple[list[dict[str, str]], dict[str, int]]:
    lines = [clean_line(line) for line in raw_lines]
    rows: list[dict[str, str]] = []
    skipped_blocks = 0

    for block_index, (start, end, relative_time, ip_location, likes, block_lines) in enumerate(candidate_blocks(lines), 1):
        author, author_is_post_author, text_lines = trim_author_tokens(block_lines)
        interaction_lines = [line for line in text_lines if line in AUTHOR_INTERACTION_LINES]
        text_lines = [line for line in text_lines if line not in AUTHOR_INTERACTION_LINES]
        comment_text = "\n".join(line for line in text_lines if line and line not in NOISE_LINES).strip()

        if not author or not comment_text:
            skipped_blocks += 1
            continue

        previous_line = previous_content_line(lines, start)
        expanded_marker = previous_line if EXPANDED_REPLY_RE.match(previous_line) else ""
        parse_notes = [
            "post_id_unavailable_in_export",
            "local_record_id_not_platform_comment_id",
        ]
        if expanded_marker:
            parse_notes.append("reply_thread_marker_seen_before_block")

        rows.append(
            {
                "source_record_id": f"comment_{len(rows) + 1:06d}",
                "douyin_post_id": "",
                "author": author,
                "author_is_post_author": "true" if author_is_post_author else "false",
                "comment_text": comment_text,
                "relative_time": relative_time,
                "ip_location": ip_location,
                "like_count": likes,
                "author_interaction": ";".join(interaction_lines),
                "expanded_reply_marker": expanded_marker,
                "source_start_line": str(start + 1),
                "source_end_line": str(end + 1),
                "source_block_text": "\n".join(lines[start : end + 1]).strip(),
                "parse_confidence": "medium",
                "parse_notes": ";".join(parse_notes),
            }
        )

    return rows, {"parsed_rows": len(rows), "skipped_blocks": skipped_blocks}


def parse_comments(path: Path) -> tuple[list[dict[str, str]], dict[str, int]]:
    with path.open(encoding="utf-8") as input_file:
        return parse_comments_from_lines(input_file.readlines())


def save_csv(rows: list[dict[str, str]], output_path: Path, *, allow_shrink: bool = False) -> tuple[int, Path | None]:
    return safe_write_csv(
        rows,
        output_path,
        FIELDNAMES,
        key_fields=KEY_FIELDS,
        merge_existing=False,
        allow_empty=False,
        allow_shrink=allow_shrink,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Parse manually exported Douyin Markdown comments into CSV.")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Markdown file exported from Google Docs/Word")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="CSV output path for parsed comment units")
    parser.add_argument(
        "--allow-shrink",
        action="store_true",
        help="Allow overwriting an existing parsed CSV with fewer rows after source-format review",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.exists():
        raise SystemExit(f"Input file not found: {input_path}")

    rows, stats = parse_comments(input_path)
    total_rows, backup_path = save_csv(rows, Path(args.output), allow_shrink=args.allow_shrink)
    print(f"Parsed rows: {stats['parsed_rows']}")
    print(f"Skipped incomplete blocks: {stats['skipped_blocks']}")
    print(f"Wrote rows: {total_rows} to {args.output}")
    if backup_path:
        print(f"Backup written: {backup_path}")


if __name__ == "__main__":
    try:
        main()
    except UnsafeWriteError as error:
        raise SystemExit(str(error)) from error
