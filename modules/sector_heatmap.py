"""Sector leadership view."""

from __future__ import annotations

import numpy as np
import plotly.graph_objects as go
import streamlit as st

from data.equities import SECTOR_ETFS, calculate_period_returns, date_years_ago, fetch_prices
from utils.formatting import format_percent
from utils.theme import RETURN_COLORSCALE, apply_theme

TIMEFRAMES = {"1D": 1, "1W": 5, "1M": 21, "3M": 63, "YTD": None, "1Y": 252}


def _takeaway(returns, timeframe: str) -> str:
    column = returns[timeframe].dropna()
    if column.empty:
        return "Not enough price history is available to rank sectors yet."
    leader, laggard = column.idxmax(), column.idxmin()
    return (
        f"**{SECTOR_ETFS[leader]} ({leader})** leads over **{timeframe}** "
        f"at {format_percent(column[leader])}; **{SECTOR_ETFS[laggard]} ({laggard})** "
        f"lags at {format_percent(column[laggard])}."
    )


def render() -> None:
    st.subheader("Sector performance")
    st.caption("Relative leadership across the 11 S&P 500 sector ETFs, based on adjusted close prices.")

    selected = st.multiselect(
        "Timeframes", options=list(TIMEFRAMES), default=list(TIMEFRAMES), key="sector_timeframes"
    )
    if not selected:
        st.info("Select at least one timeframe to view sector leadership.")
        return

    with st.spinner("Loading sector ETF prices…"):
        prices, failed = fetch_prices(tuple(SECTOR_ETFS), date_years_ago(2))
    for ticker in failed:
        st.warning(f"{ticker} price data is unavailable right now; it is excluded from this view.", icon="⚠️")
    if prices.empty:
        st.error("No sector price data was returned. Check your connection and try again.")
        return

    returns = calculate_period_returns(prices, {label: TIMEFRAMES[label] for label in selected})
    returns = returns.reindex([ticker for ticker in SECTOR_ETFS if ticker in returns.index])
    focus = "1M" if "1M" in selected else selected[0]
    st.info(_takeaway(returns, focus), icon="💡")

    labels = [f"{SECTOR_ETFS[ticker]} · {ticker}" for ticker in returns.index]
    values = returns[selected].to_numpy(dtype=float)
    bound = max(0.03, min(0.35, float(np.nanmax(np.abs(values))) if np.isfinite(values).any() else 0.03))
    cell_text = [[format_percent(value) for value in row] for row in values]
    figure = go.Figure(
        go.Heatmap(
            z=values,
            x=selected,
            y=labels,
            text=cell_text,
            texttemplate="%{text}",
            textfont={"size": 13},
            colorscale=RETURN_COLORSCALE,
            zmid=0,
            zmin=-bound,
            zmax=bound,
            colorbar={"title": "Return", "tickformat": ".0%"},
            hovertemplate="%{y}<br>%{x}: %{z:+.2%}<extra></extra>",
        )
    )
    apply_theme(figure, height=510, title="Sector return heatmap")
    figure.update_xaxes(side="top")
    figure.update_yaxes(autorange="reversed")
    st.plotly_chart(figure, use_container_width=True, config={"displaylogo": False})

    export = returns[selected].rename(index=SECTOR_ETFS).rename_axis("Sector")
    st.download_button(
        "Download sector returns (CSV)",
        export.to_csv().encode("utf-8"),
        "marketpulse-sector-returns.csv",
        "text/csv",
    )
