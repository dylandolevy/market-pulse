"""Resilient yfinance access plus price-derived market calculations."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date

import pandas as pd
import streamlit as st
import yfinance as yf

from utils.formatting import start_of_year

SECTOR_ETFS: dict[str, str] = {
    "XLK": "Technology",
    "XLF": "Financials",
    "XLE": "Energy",
    "XLV": "Health Care",
    "XLY": "Consumer Discretionary",
    "XLP": "Consumer Staples",
    "XLI": "Industrials",
    "XLB": "Materials",
    "XLU": "Utilities",
    "XLRE": "Real Estate",
    "XLC": "Communication Services",
}

ASSET_BASKET: dict[str, str] = {
    "SPY": "US Equities",
    "EFA": "Intl. Developed Equities",
    "EEM": "Emerging Markets",
    "TLT": "Long Treasuries",
    "AGG": "Aggregate Bonds",
    "GLD": "Gold",
    "DBC": "Broad Commodities",
    "UUP": "US Dollar",
    "BTC-USD": "Bitcoin",
}


def _normalise_close(raw: pd.DataFrame, tickers: Sequence[str]) -> pd.DataFrame:
    """Extract close prices from either yfinance's single or multi-index result."""
    if raw.empty:
        return pd.DataFrame(columns=list(tickers), dtype=float)

    if isinstance(raw.columns, pd.MultiIndex):
        level_zero = raw.columns.get_level_values(0)
        if "Close" in level_zero:
            close = raw["Close"].copy()
        elif "Adj Close" in level_zero:
            close = raw["Adj Close"].copy()
        else:
            return pd.DataFrame(columns=list(tickers), dtype=float)
    elif "Close" in raw.columns:
        close = raw[["Close"]].copy()
        close.columns = [tickers[0]] if len(tickers) == 1 else close.columns
    elif "Adj Close" in raw.columns:
        close = raw[["Adj Close"]].copy()
        close.columns = [tickers[0]] if len(tickers) == 1 else close.columns
    else:
        return pd.DataFrame(columns=list(tickers), dtype=float)

    close = close.reindex(columns=list(tickers))
    close.index = pd.to_datetime(close.index).tz_localize(None)
    return close.sort_index().apply(pd.to_numeric, errors="coerce")


@st.cache_data(ttl=3600, show_spinner=False)
def fetch_prices(
    tickers: tuple[str, ...], start: str, end: str | None = None
) -> tuple[pd.DataFrame, tuple[str, ...]]:
    """Fetch adjusted daily close prices, returning unavailable tickers separately."""
    try:
        raw = yf.download(
            list(tickers), start=start, end=end, auto_adjust=True, progress=False, threads=True
        )
    except Exception:
        return pd.DataFrame(columns=list(tickers), dtype=float), tuple(tickers)

    prices = _normalise_close(raw, tickers)
    failed = tuple(ticker for ticker in tickers if ticker not in prices or prices[ticker].dropna().empty)
    return prices.dropna(how="all"), failed


def calculate_period_returns(
    prices: pd.DataFrame,
    timeframes: Mapping[str, int | None] | None = None,
) -> pd.DataFrame:
    """Compute returns from the latest close for trading-day periods and calendar YTD."""
    frame = prices.dropna(how="all").sort_index()
    if frame.empty:
        return pd.DataFrame(columns=list((timeframes or {}).keys()), dtype=float)

    windows = timeframes or {"1D": 1, "1W": 5, "1M": 21, "3M": 63, "YTD": None, "1Y": 252}
    latest = frame.iloc[-1]
    result: dict[str, pd.Series] = {}

    for label, sessions in windows.items():
        if label == "YTD":
            eligible = frame.loc[frame.index <= start_of_year(frame.index[-1])]
            base = eligible.iloc[-1] if not eligible.empty else frame.iloc[0]
        else:
            position = max(0, len(frame) - 1 - int(sessions or 0))
            base = frame.iloc[position]
        result[label] = latest.div(base).sub(1).where(base.notna() & latest.notna())

    return pd.DataFrame(result)


def monthly_prices(prices: pd.DataFrame) -> pd.DataFrame:
    """Align daily ETF data to month-end macro observations."""
    if prices.empty:
        return prices.copy()
    return prices.resample("ME").last().dropna(how="all")


def date_years_ago(years: int) -> str:
    """Produce a stable ISO date for a yfinance start argument."""
    today = date.today()
    return date(today.year - years, today.month, today.day).isoformat()
