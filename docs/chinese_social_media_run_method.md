# Chinese Social-Media Run Method

This document records the data-handling choices for adding manually parsed
Douyin comments to the existing Xiaohongshu analysis suite.

## Decision summary

1. Keep Xiaohongshu and Douyin as separate platforms.
2. Keep Xiaohongshu notes and Douyin comments as separate units of analysis.
3. Do not paste or relabel Douyin comments as Xiaohongshu `body_text`.
4. Combine both sources only into a shared downstream field,
   `text_for_analysis`, with `platform` and `unit_type` preserved.
5. Treat `docs/codebooks/chinese_reviewed_codebook_template.csv` as a method
   input, not as observation data.

Reason: Xiaohongshu `body_text` is note-level author text. Douyin parsed data
is comment-section reader text. Combining them under one source-specific field
would hide a real platform/unit difference and make later interpretation too
easy to overstate. A shared `text_for_analysis` column gives the analysis suite
one text field while keeping provenance visible.

## Inputs

| Input | Role |
|---|---|
| `data/processed/fukui_xhs_analysis.csv` | Xiaohongshu note rows, including existing theme/fan/travel classification |
| `data/processed/fukui_douyin_comments_from_md.csv` | parsed Douyin comment rows from the manual Markdown handoff |
| `docs/codebooks/chinese_reviewed_codebook_template.csv` | reviewed keyword/codebook source for future coding rules |

## Output files

Run:

```bash
python3 -m src.analysis.build_chinese_social_run_dataset
```

Outputs:

| Output | Meaning |
|---|---|
| `data/processed/chinese_social_run_data.csv` | combined run dataset, one row per XHS note or Douyin comment |
| `data/processed/chinese_social_run_manifest.csv` | run manifest showing XHS, Douyin, codebook, and combined output row counts |

`chinese_social_run_data.csv` contains:

- `platform`: `xiaohongshu` or `douyin`
- `unit_type`: `note` or `comment`
- `text_for_analysis`: shared text column for coding/scoring
- `title`, `body_text`, `comment_text`: original source-specific text fields
- `source_file`, `source_record_id`, `provenance_notes`: audit fields

## Method limits

- Douyin Markdown is not a platform-native export. The parser does not invent
  missing post IDs or comment IDs.
- Douyin comment rows may show audience reaction to tourism content, not author
  trip reports.
- Any platform comparison must stratify or report by `platform` and `unit_type`;
  do not treat all rows as interchangeable posts.
