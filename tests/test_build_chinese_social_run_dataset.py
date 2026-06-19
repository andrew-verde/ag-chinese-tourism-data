import csv

from src.analysis import build_chinese_social_run_dataset as builder


def write_csv(path, fieldnames, rows):
    with path.open("w", encoding="utf-8", newline="") as output:
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_build_rows_keeps_xhs_notes_and_douyin_comments_separate(tmp_path):
    xhs_path = tmp_path / "xhs.csv"
    douyin_path = tmp_path / "douyin.csv"
    write_csv(
        xhs_path,
        ["note_id", "title", "body_text", "content", "author", "note_url", "theme", "fan_score", "travel_score"],
        [
            {
                "note_id": "n1",
                "title": "标题",
                "body_text": "正文",
                "content": "正文",
                "author": "xhs author",
                "note_url": "https://example.test/n1",
                "theme": "travel",
                "fan_score": "0",
                "travel_score": "1",
            }
        ],
    )
    write_csv(
        douyin_path,
        ["source_record_id", "author", "comment_text", "like_count", "relative_time", "ip_location"],
        [
            {
                "source_record_id": "comment_000001",
                "author": "douyin author",
                "comment_text": "评论",
                "like_count": "3",
                "relative_time": "2月前",
                "ip_location": "福建",
            }
        ],
    )

    rows = builder.build_rows(xhs_path, douyin_path)

    assert [row["platform"] for row in rows] == ["xiaohongshu", "douyin"]
    assert [row["unit_type"] for row in rows] == ["note", "comment"]
    assert rows[0]["text_for_analysis"] == "正文"
    assert rows[1]["text_for_analysis"] == "评论"
    assert rows[1]["body_text"] == ""
    assert rows[1]["provenance_notes"] == "douyin_markdown_comment_kept_as_comment_not_xhs_body_text"


def test_build_manifest_includes_codebook_as_method_input(tmp_path):
    rows = [
        {"platform": "xiaohongshu"},
        {"platform": "douyin"},
        {"platform": "douyin"},
    ]

    manifest = builder.build_manifest(
        xhs_path=tmp_path / "xhs.csv",
        douyin_path=tmp_path / "douyin.csv",
        codebook_path=tmp_path / "codebook.csv",
        output_path=tmp_path / "combined.csv",
        rows=rows,
        codebook_rows=268,
    )

    by_name = {row["input_name"]: row for row in manifest}
    assert by_name["xiaohongshu_analysis"]["rows"] == "1"
    assert by_name["douyin_comments"]["rows"] == "2"
    assert by_name["reviewed_codebook"]["included_in_run"] == "true"
    assert by_name["reviewed_codebook"]["rows"] == "268"
