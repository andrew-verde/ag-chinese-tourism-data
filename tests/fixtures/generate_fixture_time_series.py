"""Generate a SYNTHETIC monthly time series for pipeline tests ONLY.

This is Synthetic Data (see CONTEXT.md). It exists so tests can exercise
time-series code without real data. The output lands inside tests/fixtures/
and src.data_loading refuses to load anything from this directory, so it
can never reach a finding.
"""

from pathlib import Path

import numpy as np
import pandas as pd

FIXTURES_DIR = Path(__file__).resolve().parent


def create_fixture_data(seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    months = pd.date_range(start='2022-07-01', periods=24, freq='MS')
    base_trend = np.linspace(1300, 1500, 24)
    noise = rng.normal(0, 30, 24)
    visitor_counts = (base_trend + noise).astype(int)
    event_indices = [10, 14, 19, 20, 22, 23]
    for i in event_indices:
        visitor_counts[i] = int(visitor_counts[i] * 1.27)

    return pd.DataFrame({
        'Month': months,
        'Visitor_Count': visitor_counts,
        'Is_Event_Month': [1 if i in event_indices else 0 for i in range(24)],
    })


if __name__ == '__main__':
    out = FIXTURES_DIR / 'fixture_time_series_simulated.csv'
    create_fixture_data().to_csv(out, index=False)
    print(f"Synthetic test fixture written to {out} — for tests only, never for analysis.")
