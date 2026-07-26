"""MarketPulse: a decision-useful cross-asset market dashboard."""

from __future__ import annotations

import streamlit as st

from modules import correlation_matrix, macro_tracker, sector_heatmap

st.set_page_config(page_title="MarketPulse", page_icon="📈", layout="wide", initial_sidebar_state="collapsed")

st.title("MarketPulse")
st.markdown("**Cross-asset market intelligence for the first 30 seconds of an investment conversation.**")
st.caption("Data is sourced from Yahoo Finance and FRED. ETF prices are cached for one hour; macro data for six hours.")

sector_tab, correlation_tab, macro_tab = st.tabs(
    ["Sector Performance", "Cross-Asset Correlation", "Macro vs. Equities"]
)
with sector_tab:
    sector_heatmap.render()
with correlation_tab:
    correlation_matrix.render()
with macro_tab:
    macro_tracker.render()
