# Research Methodology / 研究方法

Prospective methodology for studying Chinese social-media opinion of Fukui
prefecture and the greater Hokuriku region. Written **before** data
collection so that sampling and analysis decisions are fixed in advance.

本文档在数据采集**之前**确定抽样与分析方法，以便提前固定标准。
所有数字（样本量、组数）来自实际采集的数据，因此本文档不包含示例计数。

---

## 1. Data sources / 数据来源

| Source | What | How collected |
|---|---|---|
| Xiaohongshu (小红书) | Posts/notes mentioning 福井 / Hokuriku destinations | Manual logged-in scrape — `docs/手动运行数据抓取指南.md` |
| Douyin (抖音) | Videos mentioning the same destinations | Same procedure |
| MLIT / JTA | 宿泊旅行統計調査, 訪日外国人消費動向調査 | Official downloads into `data/raw/mlit/`, hand-extracted tables into `data/raw/jta/` with source URL + table number recorded |
| Fukui open data | People-flow, surveys, trend reports | `data/raw/fukui-kanko-*`, `data/raw/opendata` |

All analysis inputs load through `src/data_loading.load_research_data`
(see `docs/adr/0001`). Findings may only be derived from Real Data as
defined in `CONTEXT.md`.

For the Chinese social-media run, Xiaohongshu notes and Douyin comments are
combined only after normalization into `data/processed/chinese_social_run_data.csv`.
The shared analysis text column is `text_for_analysis`; `platform` and
`unit_type` remain required interpretation fields. Douyin comments are not
converted into Xiaohongshu `body_text`, because they are comment-level audience
responses rather than note-level author text. Full decision log:
`docs/chinese_social_media_run_method.md`.

## 2. Sample selection / 样本选择

Decide and record **before** sampling:

1. **Inclusion criteria / 入选标准** — engagement thresholds (e.g.
   likes ≥ X, comments ≥ Y) or content-completeness criteria (minimum
   length, topical relevance keywords). Pick one, write the actual numbers
   here when collection starts, and do not change them mid-study.
2. **Time window / 时间范围** — fixed calendar range, stated in the report.
3. **Sampling frame / 总体池** — the full set of scraped posts meeting the
   criteria. Report its actual size (a row count from the real CSV, not an
   estimate).
4. **Stratified sampling / 分层抽样** — if sampling by theme, allocate
   strata proportional to observed theme frequency in the frame, and report
   the observed (not target) allocation.

## 3. Theme classification / 主题分类

Themes are assigned by the classification step
(`src/analysis/xhs_fukui_analysis.py`) and recorded per review in
`data/processed/`. The theme taxonomy and any keyword lists must be frozen
and documented before scoring sentiment.

## 4. Statistical tests / 统计检验

The same theme grouping legitimately feeds two different tests:

- **Chi-square goodness-of-fit** — tests whether sample counts across
  themes deviate from a uniform (or otherwise specified) expected
  distribution. Input: per-theme counts. H0: themes are equally frequent.
- **One-way ANOVA** — tests whether mean sentiment (emotion score) differs
  across themes. Input: per-review scores grouped by theme.
  H0: all theme means are equal. Check normality and homogeneity of
  variance assumptions; fall back to Kruskal–Wallis if violated.
- **Event-impact comparison** — t-test (or Mann-Whitney) of event months vs
  non-event months on the real MLIT monthly series built by
  `src/analysis/build_china_time_series.py`.

These run via `python3 -m src.analysis.statistical_analysis` with explicit
input files (`docs/adr/0002`).

## 5. Hypotheses / 假设

State each hypothesis with its test, direction, and significance level
(α = 0.05 unless justified otherwise) in the report **before** running the
test on real data.

## 6. Reporting / 报告

- Every figure traces to a file under `data/raw/` or `data/processed/` and
  ultimately to a named external source.
- Negative and null results are reported, not dropped.
- If a planned analysis cannot run because data is missing, the report
  states this explicitly.
