import csv

import pytest

from src.scrapers import xhs_manual_note_capture


def test_row_from_capture_requires_body_text():
    with pytest.raises(ValueError, match="No visible Xiaohongshu body text found"):
        xhs_manual_note_capture.row_from_capture(
            {
                "note_url": "https://www.xiaohongshu.com/explore/abc123",
                "title": "福井旅行",
                "body_text": "",
            }
        )


def test_row_from_capture_adds_body_and_content_columns():
    row = xhs_manual_note_capture.row_from_capture(
        {
            "note_url": "https://www.xiaohongshu.com/explore/abc123?xsec_token=token",
            "title": "福井旅行 - 小红书",
            "body_text": " 永平寺 很 安静 ",
            "author": "tester",
        },
        captured_at="2026-06-17T00:00:00Z",
    )

    assert row["note_id"] == "abc123"
    assert row["title"] == "福井旅行"
    assert row["body_text"] == "永平寺 很 安静"
    assert row["content"] == "永平寺 很 安静"
    assert row["captured_at"] == "2026-06-17T00:00:00Z"


def test_save_csv_merges_existing_title_only_row_by_note_id(tmp_path):
    output = tmp_path / "xhs.csv"
    with output.open("w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["note_id", "title", "note_url", "author", "author_url"])
        writer.writeheader()
        writer.writerow(
            {
                "note_id": "abc123",
                "title": "old title",
                "note_url": "https://www.xiaohongshu.com/explore/abc123",
                "author": "",
                "author_url": "",
            }
        )

    rows = [
        xhs_manual_note_capture.row_from_capture(
            {
                "note_url": "https://www.xiaohongshu.com/explore/abc123",
                "title": "new title",
                "body_text": "full note body",
            },
            captured_at="2026-06-17T00:00:00Z",
        )
    ]

    total_rows, backup_path = xhs_manual_note_capture.save_csv(rows, output)

    assert total_rows == 1
    assert backup_path is not None
    with output.open(newline="", encoding="utf-8") as csvfile:
        saved_rows = list(csv.DictReader(csvfile))
    assert saved_rows[0]["title"] == "new title"
    assert saved_rows[0]["body_text"] == "full note body"
    assert saved_rows[0]["content"] == "full note body"
