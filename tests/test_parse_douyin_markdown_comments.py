from src.analysis.parse_douyin_markdown_comments import parse_comments_from_lines


def test_parse_plain_export_comment_block():
    rows, stats = parse_comments_from_lines(
        [
            "DY NOTE DATA\n",
            "分享\n",
            "回复\n",
            "一路长庄头像\n",
            "一路长庄\n",
            "下个月就要去神户住几天，考虑下是不是要去福井。。。。\n",
            "1月前·上海\n",
            "2\n",
        ]
    )

    assert stats == {"parsed_rows": 1, "skipped_blocks": 0}
    assert rows[0]["source_record_id"] == "comment_000001"
    assert rows[0]["douyin_post_id"] == ""
    assert rows[0]["author"] == "一路长庄"
    assert rows[0]["comment_text"] == "下个月就要去神户住几天，考虑下是不是要去福井。。。。"
    assert rows[0]["relative_time"] == "1月前"
    assert rows[0]["ip_location"] == "上海"
    assert rows[0]["like_count"] == "2"
    assert "post_id_unavailable_in_export" in rows[0]["parse_notes"]


def test_parse_docs_export_author_marker_and_interaction():
    rows, stats = parse_comments_from_lines(
        [
            "分享\n",
            "￼\n",
            "回复\n",
            "￼\n",
            "Juunae\n",
            "作者\n",
            "...\n",
            "谢谢你宝宝\n",
            "作者赞过\n",
            "10月前·福建\n",
            "0\n",
        ]
    )

    assert stats["parsed_rows"] == 1
    assert rows[0]["author"] == "Juunae"
    assert rows[0]["author_is_post_author"] == "true"
    assert rows[0]["comment_text"] == "谢谢你宝宝"
    assert rows[0]["author_interaction"] == "作者赞过"


def test_skips_blocks_without_comment_text():
    rows, stats = parse_comments_from_lines(
        [
            "分享\n",
            "回复\n",
            "Juunae\n",
            "作者\n",
            "...\n",
            "10月前·福建\n",
            "0\n",
        ]
    )

    assert rows == []
    assert stats == {"parsed_rows": 0, "skipped_blocks": 1}
