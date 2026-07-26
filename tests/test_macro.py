from unittest.mock import Mock, patch

import pandas as pd

from data.macro import fetch_fred_series, transform_macro_series


def test_transform_macro_series_converts_cpi_to_year_over_year():
    index = pd.date_range("2024-01-01", periods=13, freq="MS")
    values = pd.Series(range(100, 113), index=index, dtype=float)

    actual = transform_macro_series("CPIAUCSL", values)

    assert actual.name == "CPI YoY"
    assert round(actual.iloc[-1], 2) == 12.0


@patch("data.macro.requests.get")
def test_fetch_fred_series_parses_observations_without_live_network(mock_get):
    response = Mock()
    response.json.return_value = {
        "observations": [{"date": "2025-01-01", "value": "4.25"}, {"date": "2025-02-01", "value": "."}]
    }
    mock_get.return_value = response
    fetch_fred_series.clear()

    values, error = fetch_fred_series("FEDFUNDS", "test-key", "2025-01-01")

    assert error is None
    assert isinstance(values, pd.Series)
    assert values.iloc[0] == 4.25
    assert len(values) == 1
