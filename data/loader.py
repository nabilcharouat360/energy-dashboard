"""
Data loading utilities.
  - Yahoo Finance download
  - CSV file upload parsing
"""
import pandas as pd
import yfinance as yf
import streamlit as st


@st.cache_data(ttl=900, show_spinner=False)
def load_from_yfinance(ticker: str, start, end) -> pd.DataFrame:
    """Download OHLCV data from Yahoo Finance and return a clean DataFrame."""
    raw = yf.download(ticker, start=start, end=end, progress=False, auto_adjust=True)
    if raw.empty:
        return pd.DataFrame()

    # Flatten MultiIndex columns if present
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    df = raw[["Open", "High", "Low", "Close", "Volume"]].copy()
    df.index = pd.to_datetime(df.index)
    df.index.name = "Date"
    df.dropna(inplace=True)
    return df


def load_from_csv(uploaded_file) -> pd.DataFrame:
    """
    Parse an uploaded CSV into a standardised OHLCV DataFrame.

    Expected columns (case-insensitive): Date, Open, High, Low, Close, Volume.
    Volume is optional — filled with 0 if missing.
    """
    df = pd.read_csv(uploaded_file)

    # Normalise column names
    df.columns = [c.strip().title() for c in df.columns]

    required = {"Open", "High", "Low", "Close"}
    if not required.issubset(set(df.columns)):
        missing = required - set(df.columns)
        raise ValueError(
            f"CSV is missing required columns: {', '.join(missing)}. "
            f"Expected: Date, Open, High, Low, Close (and optionally Volume)."
        )

    # Parse date
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"], dayfirst=False)
        df.set_index("Date", inplace=True)
    elif "Datetime" in df.columns:
        df["Datetime"] = pd.to_datetime(df["Datetime"])
        df.set_index("Datetime", inplace=True)
        df.index.name = "Date"
    else:
        df.index = pd.to_datetime(df.index)
        df.index.name = "Date"

    if "Volume" not in df.columns:
        df["Volume"] = 0

    df = df[["Open", "High", "Low", "Close", "Volume"]]
    df.sort_index(inplace=True)
    df.dropna(inplace=True)
    return df
