# Scraper output lands here. Real Data only — see CONTEXT.md and docs/adr/0001.

- `fukui_xhs_reviews.csv`: raw Xiaohongshu scraper output used as the
  title-only candidate list.
- `fukui_xhs_reviews_manual.xlsx`: manual review workbook copied from the Hokuriku
  sentiment project. It preserves scraper IDs/titles/URLs plus manually added
  `body_text` needed for analysis checks. This workbook is the XHS input for
  the current analysis run.
- `fukui_douyin_posts_comments.md`: manually pasted Douyin post/comment text
  exported from Google Drive as Markdown. This is not a platform-native export:
  it does not contain reliable Douyin post IDs or comment IDs.

## Douyin Markdown parsing

Convert the Markdown handoff into comment-level CSV with:

```bash
python3 -m src.analysis.parse_douyin_markdown_comments
```

Default output:

```text
data/processed/fukui_douyin_comments_from_md.csv
```

The parser treats each confidently detected comment as one unit of analysis. It
leaves `douyin_post_id` blank because the Word/Google Docs export does not
preserve post boundaries or platform IDs reliably enough for academic grouping.
Each row includes `source_start_line`, `source_end_line`, and
`source_block_text` so later sentiment analysis can audit exactly which source
lines produced each record.

## Combined analysis run

Do not copy Douyin comments into Xiaohongshu `body_text`. Xiaohongshu body text
is note-level author text; parsed Douyin rows are comment-level audience text.
For analysis, build a combined run dataset with:

```bash
python3 -m src.analysis.build_chinese_social_run_dataset --allow-shrink
```

Default outputs:

```text
data/processed/chinese_social_run_data.csv
data/processed/chinese_social_run_manifest.csv
```

The combined dataset uses `text_for_analysis` as the shared text field and keeps
`platform` plus `unit_type` so Xiaohongshu notes and Douyin comments remain
auditable separately.
