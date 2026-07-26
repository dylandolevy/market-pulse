import pandas as pd

from data.equities import _normalise_close, calculate_period_returns, monthly_prices


def test_normalise_close_extracts_multi_ticker_close_prices():
    index = pd.date_range("2025-01-01", periods=2)
    columns = pd.MultiIndex.from_product([["Close", "Volume"], ["SPY", "TLT"]])
    raw = pd.DataFrame([[100, 90, 1, 2], [105, 91, 1, 2]], index=index, columns=columns)

    actual = _normalise_close(raw, ("SPY", "TLT"))

    assert list(actual.columns) == ["SPY", "TLT"]
    assert actual.loc[index[-1], "SPY"] == 105


def test_calculate_period_returns_handles_ytd_and_trading_windows():
    index = pd.bdate_range("2025-01-02", periods=6)
    prices = pd.DataFrame({"XLK": [100, 101, 102, 103, 104, 105]}, index=index)

    actual = calculate_period_returns(prices, {"1D": 1, "1W": 5, "YTD": None})

    assert round(actual.loc["XLK", "1D"], 4) == round(105 / 104 - 1, 4)
    assert round(actual.loc["XLK", "1W"], 4) == 0.05
    assert round(actual.loc["XLK", "YTD"], 4) == 0.05


def test_monthly_prices_resamples_to_month_end():
    prices = pd.DataFrame(
        {"SPY": [100, 101, 102]}, index=pd.to_datetime(["2025-01-30", "2025-01-31", "2025-02-03"])
    )
    actual = monthly_prices(prices)
    assert list(actual.index.strftime("%Y-%m-%d")) == ["2025-01-31", "2025-02-28"]
    assert actual.iloc[0, 0] == 101
