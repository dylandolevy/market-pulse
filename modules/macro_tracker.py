"""Macro indicators compared with equity performance."""

from __future__ import annotations

from datetime import date

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from data.equities import fetch_prices, monthly_prices
from data.macro import MACRO_SERIES, fetch_macro_bundle, get_fred_api_key
from utils.formatting import format_percent, format_value
from utils.theme import ACCENT, MUTED, apply_theme


def _macro_takeaway(aligned: pd.DataFrame, macro_label: str) -> str:
    if len(aligned) < 13:
        return "Not enough aligned monthly observations are available to produce a 12-month comparison."
    latest, year_ago = aligned.iloc[-1], aligned.iloc[-13]
    macro_change = latest["macro"] - year_ago["macro"]
    spy_return = latest["SPY"] / year_ago["SPY"] - 1
    direction = "higher" if macro_change >= 0 else "lower"
    return (
        f"Over the last 12 months, **{macro_label}** is {direction} by "
        f"{format_value(abs(macro_change))} points while **SPY** returned {format_percent(spy_return)}."
    )


def render() -> None:
    st.subheader("Macro vs. equities")
    st.caption("Compare the policy and economic backdrop with the S&P 500 on a monthly, like-for-like basis.")
    api_key = get_fred_api_key()
    if not api_key:
        st.info(
            "Add a free `FRED_API_KEY` to `.env` for local use (or Streamlit secrets in deployment) to enable this tab. "
            "Get a key from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html).",
            icon="ℹ️",
        )
        return

    selected = st.selectbox(
        "Macro indicator",
        options=list(MACRO_SERIES),
        format_func=lambda series_id: MACRO_SERIES[series_id],
        key="macro_indicator",
    )
    start = f"{date.today().year - 15}-01-01"
    with st.spinner("Loading macro and equity history…"):
        macro_data, errors = fetch_macro_bundle(MACRO_SERIES.keys(), api_key, start)
        prices, failures = fetch_prices(("SPY",), start)
    for series_id, error in errors.items():
        st.warning(f"{MACRO_SERIES[series_id]}: {error}", icon="⚠️")
    if failures or prices.empty:
        st.warning("SPY price data is unavailable right now; the macro comparison cannot be calculated.", icon="⚠️")
        return
    if selected not in macro_data:
        st.info("The chosen macro series is not currently available. Choose another indicator or try again later.")
        return

    macro_monthly = macro_data[selected].resample("ME").last().rename("macro")
    spy_monthly = monthly_prices(prices)["SPY"]
    aligned = pd.concat([macro_monthly, spy_monthly], axis=1).dropna().sort_index()
    if aligned.empty:
        st.error("No overlapping monthly observations were available for this comparison.")
        return

    min_date, max_date = aligned.index.min().date(), aligned.index.max().date()
    default_start = max(min_date, date(max_date.year - 10, max_date.month, 1))
    selection = st.slider(
        "Date range", min_value=min_date, max_value=max_date, value=(default_start, max_date), format="MMM YYYY"
    )
    filtered = aligned.loc[str(selection[0]) : str(selection[1])]
    if filtered.empty:
        st.info("No observations fall within the selected range.")
        return

    label = "CPI inflation (YoY %)" if selected == "CPIAUCSL" else MACRO_SERIES[selected]
    st.info(_macro_takeaway(filtered, label), icon="💡")
    figure = make_subplots(specs=[[{"secondary_y": True}]])
    figure.add_trace(
        go.Scatter(x=filtered.index, y=filtered["macro"], name=label, line={"color": ACCENT, "width": 2.5}),
        secondary_y=False,
    )
    figure.add_trace(
        go.Scatter(x=filtered.index, y=filtered["SPY"], name="SPY", line={"color": MUTED, "width": 2}),
        secondary_y=True,
    )
    apply_theme(figure, height=470, title=f"{label} and S&P 500")
    figure.update_yaxes(title_text=label, secondary_y=False)
    figure.update_yaxes(title_text="SPY adjusted close", secondary_y=True)
    figure.update_layout(legend={"orientation": "h", "y": 1.12, "x": 0})
    st.plotly_chart(figure, use_container_width=True, config={"displaylogo": False})

    st.download_button(
        "Download aligned monthly data (CSV)",
        filtered.to_csv().encode("utf-8"),
        "marketpulse-macro-vs-spy.csv",
        "text/csv",
    )
