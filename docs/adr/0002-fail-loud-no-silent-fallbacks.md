# 0002 — Pipeline steps fail loud; no silent fallbacks to generated data

Date: 2026-06-12
Status: Accepted

## Context

An earlier version of the time-series builder fell back to writing a
generated 24-month series when MLIT Excel parsing failed, signalled only by
a console line, with an output filename nearly identical to the real one.
Plotting code likewise loaded the generated file whenever the real one was
missing, and some analysis scripts ran on built-in example values by
default. Each fallback was individually visible, but together they let
generated values flow into results without any step refusing to proceed.

## Decision

A pipeline step either produces Real Data output or raises/exits with an
error that says what input is missing and how to collect it. Specifically:

1. No code path may substitute generated, demo, or "typical pattern" values
   when real input is absent or unparseable.
2. Analysis CLIs have no default demo mode; they require explicit input
   files and error out otherwise.
3. Numbers never live in code. Scripts load every figure from a data file
   whose source (document URL, table number) is recorded alongside it.

## Consequences

* `src/analysis/build_china_time_series.py` exits with an error when MLIT
  parsing fails instead of writing a simulated series.
* `statistical_analysis.py`, `market_analysis_3prefectures.py`,
  `china_lodging_analysis_2024.py`, and `kanazawa_vs_fukui_analysis.py`
  take their inputs from data files with documented schemas.
* First runs fail until data is collected. That is intentional: a loud
  failure on day one is cheaper than re-checking published numbers later.
