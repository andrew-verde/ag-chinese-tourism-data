"""Single gateway for reading research data into analysis code.

Why this module exists
======================
Analysis must run only on collected data. This loader keeps test and
example data structurally separate from research data
(see docs/adr/0001 and docs/adr/0002):

* Analysis code must load every dataset through ``load_research_data``.
* Synthetic data may only live under ``tests/fixtures/`` — and this
  loader refuses to read anything from that directory.
* Empty datasets are refused: a CSV with headers but no rows means the
  collection step has not actually run yet, and analysing it would
  produce meaningless results.

中文说明: 所有分析脚本必须通过 ``load_research_data`` 读取数据。
``tests/fixtures/`` 目录下的合成数据永远不能进入分析；
空文件（只有表头、没有数据行）会被拒绝，因为这说明数据采集还没有真正完成。
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REPO_ROOT = Path(__file__).resolve().parents[1]
FIXTURES_DIR = REPO_ROOT / "tests" / "fixtures"
RAW_DIR = REPO_ROOT / "data" / "raw"
PROCESSED_DIR = REPO_ROOT / "data" / "processed"


class SyntheticDataError(RuntimeError):
    """Raised when analysis code tries to load synthetic/fixture data."""


class EmptyDataError(RuntimeError):
    """Raised when a dataset exists but contains no data rows."""


class MissingDataError(FileNotFoundError):
    """Raised when a dataset has not been collected yet."""


def _check_path(path: Path) -> Path:
    path = Path(path).resolve()

    try:
        path.relative_to(FIXTURES_DIR)
    except ValueError:
        pass
    else:
        raise SyntheticDataError(
            f"{path} is under tests/fixtures/ — synthetic data must never feed a finding. "
            "Point the analysis at a real dataset under data/raw/ or data/processed/."
        )

    if "simulated" in path.name.lower() or "mock" in path.name.lower():
        raise SyntheticDataError(
            f"{path} looks like synthetic data (name contains 'simulated'/'mock'). "
            "Synthetic data belongs under tests/fixtures/ and cannot be analysed."
        )

    if not path.exists():
        raise MissingDataError(
            f"{path} does not exist. Run the corresponding collection step first — "
            "see docs/手动运行数据抓取指南.md for the manual scrape procedure."
        )
    return path


def load_research_data(path: str | Path, *, loader: str = "csv", **read_kwargs) -> pd.DataFrame:
    """Load a Real Data file for analysis.

    Parameters
    ----------
    path:
        File under ``data/raw/`` or ``data/processed/``.
    loader:
        ``"csv"`` (default) or ``"excel"``.
    read_kwargs:
        Passed through to :func:`pandas.read_csv` / :func:`pandas.read_excel`.
    """
    path = _check_path(Path(path))

    if loader == "csv":
        df = pd.read_csv(path, **read_kwargs)
    elif loader == "excel":
        df = pd.read_excel(path, **read_kwargs)
    else:
        raise ValueError(f"Unknown loader {loader!r}; use 'csv' or 'excel'.")

    if df.empty:
        raise EmptyDataError(
            f"{path} contains no data rows. The collection step has not produced data yet — "
            "refusing to analyse an empty dataset."
        )
    return df
