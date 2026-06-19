import pandas as pd
import pytest

from src.analysis.statistical_analysis import require_columns


def test_require_columns_reports_missing_and_available_columns():
    df = pd.DataFrame({"Month": ["2024-01"], "Visitor_Count": [1]})

    with pytest.raises(ValueError) as excinfo:
        require_columns(df, "data/processed/fukui_china_time_series.csv", ("month", "visitors", "is_event_month"))

    message = str(excinfo.value)
    assert "lacks required column(s): 'month', 'visitors', 'is_event_month'" in message
    assert "Available columns: Month, Visitor_Count" in message
