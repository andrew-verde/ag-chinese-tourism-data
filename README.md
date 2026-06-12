# tourism-data — Fukui / Hokuriku Chinese Social-Media Tourism Research

Research pipeline for studying Chinese opinion of Fukui prefecture and the
greater Hokuriku region, combining manually scraped Xiaohongshu / Douyin
content with official MLIT / JTA tourism statistics.

本仓库用于研究中国游客对福井县及北陆地区的看法：手动抓取小红书 / 抖音内容，
并结合日本国土交通省（MLIT / 観光庁）官方统计数据进行分析。

> **This repository starts with no datasets or findings.** It is a
> template structured so that test or example data stays strictly separate
> from research data. Read `docs/adr/0001` and `docs/adr/0002` before
> adding data.

## Data integrity rules / 数据真实性规则

1. **Findings come only from Real Data** — collected from an external
   source, never generated. Definitions: [CONTEXT.md](CONTEXT.md).
2. **Synthetic data lives only in `tests/fixtures/`.** The shared loader
   (`src/data_loading.py`) refuses to read fixtures, files named
   `*simulated*`/`*mock*`, and CSVs with zero data rows.
3. **No silent fallbacks.** Every pipeline step either produces real output
   or fails with an error telling you what to collect. No demo modes.
4. **Numbers never live in code.** Every figure loads from a file under
   `data/`, traceable to a named source (URL + table number).

## Repository layout

```
CONTEXT.md              Canonical glossary (Real Data, Synthetic Data, Finding…)
docs/
  METHODOLOGY.md        Sampling and statistical methodology (fixed before collection)
  手动运行数据抓取指南.md  Manual scrape procedure (Chinese, operational)
  adr/                  Architecture decision records
data/
  raw/                  Real Data as collected: mlit/, jta/, social/, opendata…
  processed/            Derived datasets built by src/analysis (regenerable)
src/
  scrapers/             Xiaohongshu / Douyin scrapers + MLIT downloader
  analysis/             Statistical and market analyses (real inputs required)
  viz/                  Figure generation (writes to outputs/, never committed)
  pipeline_io.py        Atomic, backed-up, merge-safe CSV writes
  data_loading.py       The integrity gate — all analysis reads go through here
tests/
  fixtures/             The ONLY home for synthetic data
outputs/                Generated figures (gitignored)
```

## Quick start / 快速开始

```bash
pip install -r requirements.txt
python -m playwright install chromium

# 1. Scrape (manual, logged-in browser session — see docs/手动运行数据抓取指南.md)
python3 run_fukui_pipeline.py

# 2. Build the MLIT monthly series
python3 -m src.analysis.build_china_time_series

# 3. Run statistics on collected data (no demo mode — requires real inputs)
python3 -m src.analysis.statistical_analysis --help

# Tests (includes the integrity-gate tests)
python3 -m pytest tests/
```

All commands run from the repository root.

## Relationship to upstream / 与原仓库的关系

Upstream (`xzolynn/tourism-data`) is an earlier iteration of this project,
kept unmodified for reference. Datasets, derived CSVs, and slides were not
carried over — collect data fresh through the procedures documented here.
When comparing results across the two repositories, cite which iteration
each number comes from.
