"""FRED access with explicit missing-key and request-failure states."""

from __future__ import annotations

import os
from collections.abc import Iterable

import pandas as pd
import requests
import streamlit as st
from dotenv import load_dotenv

FRED_ENDPOINT = "https://api.stlouisfed.org/fred/series/observations"
MACRO_SERIES: dict[str, str] = {
    "FEDFUNDS": "Federal Funds Rate",
    "CPIAUCSL": "CPI (All Urban Consumers)",
    "UNRATE": "Unemployment Rate",
    "DGS10": "10-Year Treasury Yield",
}

load_dotenv()


def get_fred_api_key() -> str | None:
    """Look in Streamlit secrets first, then local dotenv environment variables."""
    try:
        key = st.secrets.get("FRED_API_KEY")
    except Exception:
        key = None
    return key or os.getenv("FRED_API_KEY")


@st.cache_data(ttl=21600, show_spinner=False)
def fetch_fred_series(
    series_id: str, api_key: str, observation_start: str
) -> tuple[pd.Series, str | None]:
    """Retrieve one FRED series, preserving a UI-safe error message on failure."""
    try:
        response = requests.get(
            FRED_ENDPOINT,
            params={
                "series_id": series_id,
                "api_key": api_key,
                "file_type": "json",
                "observation_start": observation_start,
            },
            timeout=15,
        )
        response.raise_for_status()
        observations = response.json().get("observations", [])
    except (requests.RequestException, ValueError, AttributeError):
        return pd.Series(dtype=float, name=series_id), "FRED request failed. Please try again later."

    if not observations:
        return pd.Series(dtype=float, name=series_id), "FRED returned no observations for this series."

    frame = pd.DataFrame(observations)
    if not {"date", "value"}.issubset(frame.columns):
        return pd.Series(dtype=float, name=series_id), "FRED returned an unexpected response."
    values = pd.to_numeric(frame["value"].replace(".", pd.NA), errors="coerce")
    series = pd.Series(values.to_numpy(), index=pd.to_datetime(frame["date"]), name=series_id).dropna()
    if series.empty:
        return series, "FRED returned no numeric observations for this series."
    return series.sort_index(), None


def transform_macro_series(series_id: str, values: pd.Series) -> pd.Series:
    """Convert CPI to YoY inflation while leaving rate series in their reported units."""
    cleaned = pd.to_numeric(values, errors="coerce").dropna().sort_index()
    if series_id == "CPIAUCSL":
        return cleaned.pct_change(12, fill_method=None).mul(100).rename("CPI YoY")
    return cleaned.rename(series_id)


def fetch_macro_bundle(
    series_ids: Iterable[str], api_key: str, observation_start: str
) -> tuple[dict[str, pd.Series], dict[str, str]]:
    """Fetch several series, retaining successful data when one request fails."""
    data: dict[str, pd.Series] = {}
    errors: dict[str, str] = {}
    for series_id in series_ids:
        series, error = fetch_fred_series(series_id, api_key, observation_start)
        if error:
            errors[series_id] = error
        else:
            data[series_id] = transform_macro_series(series_id, series)
    return data, errors
