# CONTEXT

Glossary of terms for the Fukui/Hokuriku Chinese social-media tourism research project. Terms here are canonical; code, docs, and reports must use them consistently.

## Terms

### Real Data
Records actually collected from an external source — a scraped Xiaohongshu/Douyin post, an MLIT spreadsheet, a prefecture open-data file. Always traceable to a source.

### Synthetic Data
Any values produced by generation rather than collection: simulated series, example rows, demonstration values. Synthetic Data may exist only as test fixtures and must never feed a Finding.

### Finding
A claim in a report, slide, or analysis output presented as true about the world (e.g. "Chinese visitor interest in Fukui rose after the Shinkansen extension"). Findings may be derived only from Real Data.

### Test Fixture
The only legitimate home for Synthetic Data: generators and generated files under `tests/fixtures/`, used to exercise pipeline code. The data loader refuses fixture paths, so fixtures can never feed a Finding.

### Upstream Archive
The original repository (`xzolynn/tourism-data`), kept unmodified for reference. This fork carries no Findings or datasets from it; comparisons cite the Upstream Archive explicitly.
