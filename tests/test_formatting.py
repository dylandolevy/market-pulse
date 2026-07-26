import numpy as np
import pandas as pd
import pytest

from utils.formatting import calculate_returns, format_percent, format_value, start_of_year


def test_format_percent_formats_sign_and_missing_values():
    assert format_percent(0.0125) == "+1.2%"
    assert format_percent(-0.01) == "-1.0%"
    assert format_percent(np.nan) == "—"


def test_format_value_and_start_of_year():
    assert format_value(1234.5) == "1,234.50"
    assert format_value(None) == "—"
    assert start_of_year(pd.Timestamp("2025-07-04")) == pd.Timestamp("2025-01-01")


def test_calculate_returns_uses_daily_changes_and_ignores_empty_rows():
    prices = pd.DataFrame(
        {"SPY": [100.0, 105.0, 110.0], "TLT": [50.0, 50.0, 55.0]},
        index=pd.date_range("2025-01-01", periods=3),
    )
    returns = calculate_returns(prices)
    assert returns.shape == (2, 2)
    assert returns.iloc[0, 0] == pytest.approx(0.05)
    assert returns.iloc[-1, 1] == pytest.approx(0.10)
