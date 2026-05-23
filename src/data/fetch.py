"""
src/data/fetch.py

Pull historical price data and macro indicators.
Run directly: python -m src.data.fetch
"""

import yfinance as yf
import pandas as pd
import pandas_datareader.data as web
from datetime import datetime
import os

# ── Config ────────────────────────────────────────────────────────────────────

START_DATE = "2005-01-01"
END_DATE   = datetime.today().strftime("%Y-%m-%d")

# Core assets for the portfolio universe
EQUITY_TICKERS = ["SPY", "QQQ", "IWM", "EFA", "EEM"]
BOND_TICKERS   = ["TLT", "IEF", "HYG", "LQD"]
MACRO_TICKERS  = ["GLD", "USO", "DBC"]   # gold, oil, commodities
VIX_TICKER     = "^VIX"

# FRED series for macro regime indicators
FRED_SERIES = {
    "yield_curve": "T10Y2Y",       # 10Y - 2Y spread (inversion = recession signal)
    "credit_spread": "BAMLH0A0HYM2", # HY spread
    "fed_funds": "FEDFUNDS",
}

RAW_DIR = "data/raw"


# ── Helpers ───────────────────────────────────────────────────────────────────

def download_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Fetch adjusted closing prices for a list of tickers."""
    print(f"Fetching: {tickers}")
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, progress=False)

    # yfinance returns MultiIndex if >1 ticker
    if isinstance(raw.columns, pd.MultiIndex):
        prices = raw["Close"]
    else:
        prices = raw[["Close"]].rename(columns={"Close": tickers[0]})

    prices.index = pd.to_datetime(prices.index)
    return prices.dropna(how="all")


def download_fred(series_dict: dict[str, str], start: str, end: str) -> pd.DataFrame:
    """Fetch macro time series from FRED."""
    frames = {}
    for label, series_id in series_dict.items():
        print(f"  FRED: {label} ({series_id})")
        try:
            s = web.DataReader(series_id, "fred", start, end)
            frames[label] = s[series_id]
        except Exception as e:
            print(f"  WARNING: could not fetch {series_id}: {e}")
    return pd.DataFrame(frames)


def save(df: pd.DataFrame, filename: str) -> None:
    os.makedirs(RAW_DIR, exist_ok=True)
    path = os.path.join(RAW_DIR, filename)
    df.to_csv(path)
    print(f"  Saved → {path}  ({len(df)} rows)")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    print("\n=== Fetching price data ===")
    all_tickers = EQUITY_TICKERS + BOND_TICKERS + MACRO_TICKERS + [VIX_TICKER]
    prices = download_prices(all_tickers, START_DATE, END_DATE)
    save(prices, "prices.csv")

    print("\n=== Fetching macro indicators (FRED) ===")
    macro = download_fred(FRED_SERIES, START_DATE, END_DATE)
    save(macro, "macro_indicators.csv")

    print("\nDone.")


if __name__ == "__main__":
    main()
