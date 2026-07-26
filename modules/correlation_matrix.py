"""Cross-asset return correlation view."""

from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from data.equities import ASSET_BASKET, date_years_ago, fetch_prices
from utils.formatting import calculate_returns
from utils.theme import ACCENT, CORRELATION_COLORSCALE, apply_theme


def _correlation_takeaway(matrix: pd.DataFrame) -> str:
    if len(matrix) < 2:
        return "Choose at least two assets to calculate correlations."
    upper = matrix.where(np.triu(np.ones(matrix.shape), k=1).astype(bool)).stack().dropna()
    if upper.empty:
        return "There is not enough overlapping return history to compare the selected assets."
    strongest = upper.idxmax()
    weakest = upper.idxmin()
    return (
        f"The tightest relationship is **{strongest[0]} / {strongest[1]}** ({upper.max():+.2f}); "
        f"the weakest is **{weakest[0]} / {weakest[1]}** ({upper.min():+.2f})."
    )


def render() -> None:
    st.subheader("Cross-asset correlation")
    st.caption("Daily-return correlations reveal diversification relationships rather than price-level co-movement.")

    controls, _ = st.columns([3, 2])
    with controls:
        assets = st.multiselect(
            "Asset basket",
            options=list(ASSET_BASKET),
            default=list(ASSET_BASKET),
            format_func=lambda ticker: f"{ticker} — {ASSET_BASKET[ticker]}",
            key="correlation_assets",
        )
    with _:
        window = st.selectbox("Rolling window", [30, 90, 180, 365], index=1, format_func=lambda days: f"{days} days")

    if len(assets) < 2:
        st.info("Select at least two assets to build the correlation matrix.")
        return

    with st.spinner("Loading cross-asset prices…"):
        prices, failed = fetch_prices(tuple(assets), date_years_ago(3))
    for ticker in failed:
        st.warning(f"{ticker} price data is unavailable right now; it is excluded from this view.", icon="⚠️")

    returns = calculate_returns(prices.reindex(columns=assets)).dropna(how="all")
    available = [ticker for ticker in assets if ticker in returns and returns[ticker].notna().sum() > window]
    if len(available) < 2:
        st.error("Not enough return history is available for the selected window.")
        return

    matrix = returns[available].tail(window).corr()
    st.info(_correlation_takeaway(matrix), icon="💡")
    text = [[f"{value:.2f}" if pd.notna(value) else "—" for value in row] for row in matrix.to_numpy()]
    figure = go.Figure(
        go.Heatmap(
            z=matrix.to_numpy(),
            x=matrix.columns,
            y=matrix.index,
            text=text,
            texttemplate="%{text}",
            textfont={"size": 12},
            zmin=-1,
            zmax=1,
            zmid=0,
            colorscale=CORRELATION_COLORSCALE,
            colorbar={"title": "Correlation"},
            hovertemplate="%{y} / %{x}: %{z:.2f}<extra></extra>",
        )
    )
    apply_theme(figure, height=560, title=f"{window}-day daily-return correlation")
    figure.update_yaxes(autorange="reversed")
    st.plotly_chart(figure, use_container_width=True, config={"displaylogo": False})

    st.markdown("#### Inspect a relationship over time")
    pair_left, pair_right = st.columns(2)
    with pair_left:
        first = st.selectbox("First asset", available, index=0, key="corr_first")
    with pair_right:
        second_options = [ticker for ticker in available if ticker != first]
        second = st.selectbox("Second asset", second_options, index=0, key="corr_second")

    rolling = returns[first].rolling(window).corr(returns[second]).dropna()
    if rolling.empty:
        st.info("The selected pair does not have sufficient overlapping data for this rolling window.")
    else:
        line = go.Figure(go.Scatter(x=rolling.index, y=rolling, mode="lines", line={"color": ACCENT, "width": 2}))
        apply_theme(line, height=310, title=f"{window}-day rolling correlation: {first} vs. {second}")
        line.update_yaxes(range=[-1, 1], title="Correlation")
        line.update_xaxes(title=None)
        st.plotly_chart(line, use_container_width=True, config={"displaylogo": False})

    st.download_button(
        "Download daily returns (CSV)",
        returns[available].to_csv().encode("utf-8"),
        "marketpulse-daily-returns.csv",
        "text/csv",
    )
