#!/usr/bin/env python3
"""Build combined Chinese social-media run dataset.

Xiaohongshu notes and Douyin comments are different units of analysis. This
builder keeps platform and unit type explicit, then exposes one shared
``text_for_analysis`` column for downstream coding.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from src.data_loading import load_research_data
from src.pipeline_io import safe_write_csv


DEFAULT_XHS_INPUT = "data/processed/fukui_xhs_analysis.csv"
DEFAULT_DOUYIN_INPUT = "data/processed/fukui_douyin_comments_from_md.csv"
DEFAULT_CODEBOOK = "docs/codebooks/chinese_reviewed_codebook_template.csv"
DEFAULT_OUTPUT = "data/processed/chinese_social_run_data.csv"
DEFAULT_MANIFEST = "data/processed/chinese_social_run_manifest.csv"

FIELDNAMES = [
    "record_id",
    "platform",
    "unit_type",
    "text_for_analysis",
    "title",
    "body_text",
    "comment_text",
    "author",
    "source_url",
    "source_record_id",
    "theme",
    "fan_score",
    "travel_score",
    "like_count",
    "relative_time",
    "ip_location",
    "source_file",
    "provenance_notes",
]

MANIFEST_FIELDNAMES = ["input_name", "path", "rows", "included_in_run", "notes"]


def first_present(row: dict[str, object], fields: list[str]) -> str:
    for field in fields:
        value = row.get(field, "")
        if value is None:
            continue
        text = str(value).strip()
        if text:
            return text
    return ""


def read_codebook_rows(path: Path) -> int:
    if not path.exists():
        raise FileNotFoundError(f"Codebook not found: {path}")
    with path.open(encoding="utf-8-sig", newline="") as codebook_file:
        reader = csv.DictReader(codebook_file)
        return sum(1 for _ in reader)


def build_rows(xhs_path: Path, douyin_path: Path) -> list[dict[str, str]]:
    xhs = load_research_data(xhs_path).fillna("")
    douyin = load_research_data(douyin_path).fillna("")
    rows: list[dict[str, str]] = []

    for index, row in enumerate(xhs.to_dict("records"), 1):
        note_id = first_present(row, ["note_id"])
        text_for_analysis = first_present(row, ["body_text", "content", "title"])
        rows.append(
            {
                "record_id": f"xhs_{index:06d}",
                "platform": "xiaohongshu",
                "unit_type": "note",
                "text_for_analysis": text_for_analysis,
                "title": first_present(row, ["title"]),
                "body_text": first_present(row, ["body_text", "content"]),
                "comment_text": "",
                "author": first_present(row, ["author"]),
                "source_url": first_present(row, ["note_url"]),
                "source_record_id": note_id,
                "theme": first_present(row, ["theme"]),
                "fan_score": first_present(row, ["fan_score"]),
                "travel_score": first_present(row, ["travel_score"]),
                "like_count": "",
                "relative_time": "",
                "ip_location": "",
                "source_file": str(xhs_path),
                "provenance_notes": "xhs_note_text_uses_body_text_when_available_else_title",
            }
        )

    for index, row in enumerate(douyin.to_dict("records"), 1):
        source_record_id = first_present(row, ["source_record_id"])
        rows.append(
            {
                "record_id": f"douyin_{index:06d}",
                "platform": "douyin",
                "unit_type": "comment",
                "text_for_analysis": first_present(row, ["comment_text"]),
                "title": "",
                "body_text": "",
                "comment_text": first_present(row, ["comment_text"]),
                "author": first_present(row, ["author"]),
                "source_url": "",
                "source_record_id": source_record_id,
                "theme": "",
                "fan_score": "",
                "travel_score": "",
                "like_count": first_present(row, ["like_count"]),
                "relative_time": first_present(row, ["relative_time"]),
                "ip_location": first_present(row, ["ip_location"]),
                "source_file": str(douyin_path),
                "provenance_notes": "douyin_markdown_comment_kept_as_comment_not_xhs_body_text",
            }
        )

    if any(not row["text_for_analysis"] for row in rows):
        raise ValueError("Combined run dataset contains blank text_for_analysis")
    return rows


def build_manifest(
    *,
    xhs_path: Path,
    douyin_path: Path,
    codebook_path: Path,
    output_path: Path,
    rows: list[dict[str, str]],
    codebook_rows: int,
) -> list[dict[str, str]]:
    xhs_count = sum(1 for row in rows if row["platform"] == "xiaohongshu")
    douyin_count = sum(1 for row in rows if row["platform"] == "douyin")
    return [
        {
            "input_name": "xiaohongshu_analysis",
            "path": str(xhs_path),
            "rows": str(xhs_count),
            "included_in_run": "true",
            "notes": "one row per Xiaohongshu note; theme/fan/travel fields retained",
        },
        {
            "input_name": "douyin_comments",
            "path": str(douyin_path),
            "rows": str(douyin_count),
            "included_in_run": "true",
            "notes": "one row per parsed Douyin comment; source line spans retained in input CSV",
        },
        {
            "input_name": "reviewed_codebook",
            "path": str(codebook_path),
            "rows": str(codebook_rows),
            "included_in_run": "true",
            "notes": "method/codebook input; not appended as observation rows",
        },
        {
            "input_name": "combined_run_data",
            "path": str(output_path),
            "rows": str(len(rows)),
            "included_in_run": "true",
            "notes": "shared text_for_analysis with platform and unit_type preserved",
        },
    ]


def write_outputs(
    rows: list[dict[str, str]],
    manifest_rows: list[dict[str, str]],
    output_path: Path,
    manifest_path: Path,
    *,
    allow_shrink: bool,
) -> None:
    safe_write_csv(
        rows,
        output_path,
        FIELDNAMES,
        key_fields=["record_id"],
        merge_existing=False,
        allow_empty=False,
        allow_shrink=allow_shrink,
    )
    safe_write_csv(
        manifest_rows,
        manifest_path,
        MANIFEST_FIELDNAMES,
        key_fields=["input_name"],
        merge_existing=False,
        allow_empty=False,
        allow_shrink=True,
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Build combined Chinese social-media run dataset.")
    parser.add_argument("--xhs-input", default=DEFAULT_XHS_INPUT)
    parser.add_argument("--douyin-input", default=DEFAULT_DOUYIN_INPUT)
    parser.add_argument("--codebook", default=DEFAULT_CODEBOOK)
    parser.add_argument("--output", default=DEFAULT_OUTPUT)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST)
    parser.add_argument("--allow-shrink", action="store_true")
    args = parser.parse_args()

    xhs_path = Path(args.xhs_input)
    douyin_path = Path(args.douyin_input)
    codebook_path = Path(args.codebook)
    output_path = Path(args.output)
    manifest_path = Path(args.manifest)

    rows = build_rows(xhs_path, douyin_path)
    codebook_rows = read_codebook_rows(codebook_path)
    manifest_rows = build_manifest(
        xhs_path=xhs_path,
        douyin_path=douyin_path,
        codebook_path=codebook_path,
        output_path=output_path,
        rows=rows,
        codebook_rows=codebook_rows,
    )
    write_outputs(rows, manifest_rows, output_path, manifest_path, allow_shrink=args.allow_shrink)

    platform_counts: dict[str, int] = {}
    for row in rows:
        platform_counts[row["platform"]] = platform_counts.get(row["platform"], 0) + 1
    print(f"Wrote {len(rows)} rows to {output_path}")
    for platform, count in sorted(platform_counts.items()):
        print(f"{platform}: {count}")
    print(f"Codebook rows referenced: {codebook_rows}")
    print(f"Manifest written to {manifest_path}")


if __name__ == "__main__":
    main()
