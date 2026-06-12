# 0001 — Synthetic data may exist only under tests/fixtures/

Date: 2026-06-12
Status: Accepted

## Context

Earlier versions of this project did not structurally distinguish collected
data from generated example data: simulated series, demonstration values,
and sample rows lived alongside research datasets and could be loaded by
the same code paths. Without a clear boundary, generated values can end up
in analysis results without anyone noticing.

The original repository (`xzolynn/tourism-data`) is preserved unmodified
upstream for reference. This fork is a restructured template that starts
with no datasets or findings.

## Decision

1. Synthetic data (anything generated rather than collected) may exist only
   under `tests/fixtures/`, exclusively to exercise pipeline code.
2. All analysis code loads datasets through `src/data_loading.load_research_data`,
   which refuses paths under `tests/fixtures/`, filenames containing
   "simulated"/"mock", and CSVs with zero data rows.
3. No datasets or derived artifacts are carried over from upstream;
   data enters this repository only through the documented collection steps.
4. Enforcement is by documented path convention plus the loader gate — not
   provenance manifests or cryptographic checks.

## Consequences

* A header-only scrape file cannot be analysed — the loader raises an error
  pointing at the collection step instead.
* Adding a new dataset means putting it under `data/raw/` or `data/processed/`
  and loading it through the gateway; no extra bureaucracy.
* The gate is a convention, not tamper-proofing: it guards against
  accidental mixing of test and research data, which is the realistic
  failure mode. Manifest-based provenance was considered and rejected as
  disproportionate for a manually operated research pipeline.
