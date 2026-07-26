# MarketPulse

**A cross-asset financial analytics dashboard that turns market, sector, and macro data into an investment-ready read in under 30 seconds.**

MarketPulse is a portfolio project for analysts and investors who need a concise answer to three practical questions: where is market leadership, which diversification relationships are holding, and what macro backdrop is equities trading through? It prioritizes computed takeaways and inspectable relationships over a crowded set of charts.

<!-- TODO: add screenshot -->

> Screenshot placeholder: run the app locally with live data, then add a current screenshot or GIF here. No image has been fabricated for this repository.

## Features

- **Sector Performance** — ranks all 11 SPDR sector ETFs across 1D, 1W, 1M, 3M, YTD, and 1Y returns in an interactive heatmap, with a dynamically generated leadership takeaway.
- **Cross-Asset Correlation** — calculates correlations on daily returns for a customizable basket of equities, bonds, commodities, the dollar, gold, and Bitcoin. Inspect any pair’s rolling correlation over time.
- **Macro vs. Equities** — overlays the fed funds rate, CPI inflation, unemployment, or 10-year yield with SPY on an aligned monthly basis. It handles a missing FRED key gracefully rather than failing the dashboard.
- **Decision-ready exports** — download the current sector-return, daily-return, or aligned macro datasets as CSV.

## Tech stack

- Python, Streamlit, Plotly
- pandas and NumPy for transformations
- yfinance for market prices and the FRED API for macroeconomic series
- pytest for deterministic unit tests of data transforms and mocked FRED access

## Setup and run

```bash
git clone <repo-url>
cd market-pulse
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # then add your FRED API key
streamlit run app.py
```

The Sector Performance and Cross-Asset Correlation tabs work without a FRED key. To enable Macro vs. Equities, request a free key from [FRED](https://fred.stlouisfed.org/docs/api/api_key.html), then set `FRED_API_KEY` in your local `.env` file.

Run the unit suite with:

```bash
pytest -q
```

## Deploy to Streamlit Community Cloud

1. Push this repository to GitHub and create an app from `app.py` in [Streamlit Community Cloud](https://share.streamlit.io/).
2. Add `FRED_API_KEY` under **Advanced settings → Secrets**:

   ```toml
   FRED_API_KEY = "your_key_here"
   ```

3. Deploy. The app reads Streamlit secrets first, then falls back to `.env` for local development.

## Live demo

[Live demo](#) — deployment link placeholder.

## License

Released under the [MIT License](LICENSE).
