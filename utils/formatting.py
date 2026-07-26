"""Small, testable presentation and calculation helpers."""

from __future__ import annotations

from datetime import date

import numpy as np
import pandas as pd


def format_percent(value: float | int | None, decimals: int = 1) -> str:
    """Format a decimal return, retaining a helpful sign for positive values."""
    if value is None or pd.isna(value) or not np.isfinite(value):
        return "—"
    return f"{value:+.{decimals}%}"


def format_value(value: float | int | None, decimals: int = 2) -> str:
    """Format a numerical macro value without exposing NaNs to the UI."""
    if value is None or pd.isna(value) or not np.isfinite(value):
        return "—"
    return f"{value:,.{decimals}f}"


def calculate_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Return daily percentage changes after dropping entirely empty observations."""
    if prices.empty:
        return pd.DataFrame(index=prices.index, columns=prices.columns, dtype=float)
    return prices.sort_index().pct_change(fill_method=None).dropna(how="all")


def start_of_year(as_of: pd.Timestamp | None = None) -> pd.Timestamp:
    """Return the first calendar day of the selected observation's year."""
    timestamp = pd.Timestamp(as_of or date.today())
    return pd.Timestamp(year=timestamp.year, month=1, day=1)
