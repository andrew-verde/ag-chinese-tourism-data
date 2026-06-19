# Codebooks

- `chinese_reviewed_codebook_template.csv`: Chinese social-media NLP codebook
  reviewed by Lynn on 2026-06-18. It records source keyword, review decision,
  final keyword, code family, and bilingual labels for friction/theme coding.
  Use this as methodology evidence and as the source for future machine-readable
  analysis rules.

The combined Chinese social-media run records this file in
`data/processed/chinese_social_run_manifest.csv` as a method input. It is not
appended to the observation-level dataset because codebook rows are coding
rules, not social-media posts or comments.
