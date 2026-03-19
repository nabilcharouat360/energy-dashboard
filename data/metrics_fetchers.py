"""
Data fetchers for the Commodities Metrics page.

Each public function returns (summary_dict, DataFrame) where summary_dict
contains the headline values for the metric card and DataFrame holds the
full series for charting.
"""
from __future__ import annotations

import pandas as pd
import requests
import yfinance as yf
from datetime import datetime, timedelta


# ══════════════════════════════════════════════════════════════════
# 1. EU Gas Storage — GIE AGSI API
# ══════════════════════════════════════════════════════════════════

def fetch_eu_gas_storage(api_key: str, region: str = "eu", size: int = 300):
    """
    Fetch EU gas-storage data from GIE AGSI.

    Returns
    -------
    summary : dict   {"storage_pct": float, "net_flow": float}
    df      : DataFrame with columns [gasInStorage, full, injection,
              withdrawal, injection-withdrawal], indexed by gasDayStart.
    """
    url = f"https://agsi.gie.eu/api?type={region}"
    headers = {"x-key": api_key}
    params = {"size": size}

    resp = requests.get(url, headers=headers, params=params, timeout=15)
    resp.raise_for_status()

    records = resp.json().get("data", [])
    if not records:
        return {"storage_pct": None, "net_flow": None}, pd.DataFrame()

    df = pd.DataFrame(records)
    df = df[["gasDayStart", "gasInStorage", "full", "injection", "withdrawal"]].copy()

    for col in ["gasInStorage", "full", "injection", "withdrawal"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["injection-withdrawal"] = df["injection"] - df["withdrawal"]
    df["gasDayStart"] = pd.to_datetime(df["gasDayStart"])
    df.set_index("gasDayStart", inplace=True)
    df.sort_index(inplace=True)

    summary = {
        "storage_pct": df["full"].iloc[-1] if not df.empty else None,
        "net_flow": df["injection-withdrawal"].iloc[-1] if not df.empty else None,
    }
    return summary, df


# ══════════════════════════════════════════════════════════════════
# 2. Day-Ahead Electricity Prices — SMARD API
# ══════════════════════════════════════════════════════════════════

def fetch_electricity_prices(
    filter_id: str = "4169",
    region: str = "DE-LU",
    resolution: str = "hour",
):
    """
    Fetch the most-recent electricity-price block from SMARD.

    Returns
    -------
    summary : dict   {"latest_price": float}
    df      : DataFrame [Price_EUR_MWh] indexed by Timestamp
    """
    # Step 1 — get timestamps index
    index_url = (
        f"https://www.smard.de/app/chart_data/{filter_id}/{region}"
        f"/index_{resolution}.json"
    )
    ts_list = requests.get(index_url, timeout=15).json().get("timestamps", [])
    if not ts_list:
        return {"latest_price": None}, pd.DataFrame()

    # Step 2 — latest data block
    latest_ts = ts_list[-1]
    data_url = (
        f"https://www.smard.de/app/chart_data/{filter_id}/{region}"
        f"/{filter_id}_{region}_{resolution}_{latest_ts}.json"
    )
    series = requests.get(data_url, timeout=15).json().get("series", [])

    df = pd.DataFrame(series, columns=["Timestamp", "Price_EUR_MWh"])
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], unit="ms")
    df["Timestamp"] = df["Timestamp"] + pd.Timedelta(hours=1)
    df.set_index("Timestamp", inplace=True)
    df.dropna(subset=["Price_EUR_MWh"], inplace=True)

    summary = {
        "latest_price": df["Price_EUR_MWh"].iloc[-1] if not df.empty else None,
    }
    return summary, df


# ══════════════════════════════════════════════════════════════════
# 3. TTF Futures — yfinance
# ══════════════════════════════════════════════════════════════════

def fetch_ttf_futures(period: str = "12mo"):
    """
    Fetch TTF Natural Gas futures from Yahoo Finance.

    Returns
    -------
    summary : dict   {"latest_price": float}
    df      : DataFrame with OHLCV columns, date-only index.
    """
    ticker = yf.Ticker("TTF=F")
    df = ticker.history(period=period)
    if df.empty:
        return {"latest_price": None}, pd.DataFrame()

    df.index = df.index.normalize()
    df.index = df.index.strftime("%Y-%m-%d")
    df.index = pd.to_datetime(df.index)

    summary = {"latest_price": df["Open"].iloc[-1] if not df.empty else None}
    return summary, df


# ══════════════════════════════════════════════════════════════════
# 4. EU Carbon Futures — CSV Upload
# ══════════════════════════════════════════════════════════════════

def load_carbon_futures(uploaded_file) -> tuple[dict, pd.DataFrame]:
    """
    Parse an uploaded Carbon Emissions Futures CSV.

    Expects columns: Date, Price (and optionally Open, High, Low, Vol.).

    Returns
    -------
    summary : dict   {"latest_price": float}
    df      : DataFrame indexed by Date with at least a Price column.
    """
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)

    # Try to coerce Price
    if "Price" in df.columns:
        df["Price"] = pd.to_numeric(
            df["Price"].astype(str).str.replace(",", ""), errors="coerce"
        )
    summary = {"latest_price": df["Price"].iloc[-1] if "Price" in df.columns else None}
    return summary, df


# ══════════════════════════════════════════════════════════════════
# 5. TTF-JKM Spread — 3 CSV Uploads
# ══════════════════════════════════════════════════════════════════

def _read_price_csv(uploaded_file) -> pd.DataFrame:
    """Read a generic CSV with Date + Price columns."""
    df = pd.read_csv(uploaded_file)
    df.columns = [c.strip() for c in df.columns]
    df["Date"] = pd.to_datetime(df["Date"])
    df.set_index("Date", inplace=True)
    df.sort_index(inplace=True)
    if "Price" in df.columns:
        df["Price"] = pd.to_numeric(
            df["Price"].astype(str).str.replace(",", ""), errors="coerce"
        )
    return df


def compute_ttf_jkm_spread(ttf_file, jkm_file, eurusd_file):
    """
    Compute TTF-JKM price spread (in €/MWh).

    - JKM prices are in $/MMBtu → convert to €/MWh using EURUSD rate.
    - Spread = TTF_Price − JKM_in_EUR.

    Returns
    -------
    summary : dict   {"latest_spread": float}
    df      : DataFrame with TTF_Price, JKM_Price, EURUSD, jkm_eur, TTF-JKM.
    """
    df_ttf = _read_price_csv(ttf_file)
    df_jkm = _read_price_csv(jkm_file)
    df_fx = _read_price_csv(eurusd_file)

    df = pd.DataFrame({
        "TTF_Price": df_ttf["Price"],
        "JKM_Price": df_jkm["Price"],
        "EURUSD": df_fx["Price"],
    }).dropna()

    df["jkm_eur"] = (df["JKM_Price"] * 3.412) / df["EURUSD"]
    df["TTF-JKM"] = df["TTF_Price"] - df["jkm_eur"]

    summary = {"latest_spread": df["TTF-JKM"].iloc[-1] if not df.empty else None}
    return summary, df


# ══════════════════════════════════════════════════════════════════
# 6. Solar & Wind Forecast — ENTSO-E
# ══════════════════════════════════════════════════════════════════

def fetch_solar_wind_forecast(api_key: str, country: str = "DE_LU", start=None, end=None):
    """
    Fetch day-ahead solar & wind generation forecast from ENTSO-E.

    Returns
    -------
    summary : dict   {"solar": float, "wind_on": float, "wind_off": float, "total": float}
    df      : DataFrame with Solar, Wind Onshore, Wind Offshore, Total Energy.
    """
    from entsoe import EntsoePandasClient

    client = EntsoePandasClient(api_key=api_key)

    if start is None:
        start = pd.Timestamp(datetime.now().date(), tz="Europe/Brussels")
    else:
        start = pd.Timestamp(start, tz="Europe/Brussels")
    if end is None:
        end = start + pd.Timedelta(days=2)
    else:
        end = pd.Timestamp(end, tz="Europe/Brussels")

    df = client.query_wind_and_solar_forecast(country, start=start, end=end)

    if "Solar" not in df.columns:
        df["Solar"] = 0
    if "Wind Onshore" not in df.columns:
        df["Wind Onshore"] = 0
    if "Wind Offshore" not in df.columns:
        df["Wind Offshore"] = 0

    df["Total Energy"] = df["Solar"] + df["Wind Onshore"] + df["Wind Offshore"]

    summary = {
        "solar": df["Solar"].iloc[-1] if not df.empty else None,
        "wind_on": df["Wind Onshore"].iloc[-1] if not df.empty else None,
        "wind_off": df["Wind Offshore"].iloc[-1] if not df.empty else None,
        "total": df["Total Energy"].iloc[-1] if not df.empty else None,
    }
    return summary, df


# ══════════════════════════════════════════════════════════════════
# 7. Market Briefing — computed from other metrics
# ══════════════════════════════════════════════════════════════════

def generate_market_briefing(
    storage_pct, net_flow, ttf_price, carbon_price, spread
) -> str:
    briefing_0 = """
    ### ⚡ Energy Market Daily
    /!\ Please upload the CSVs to display the corresponding briefing as per their analysis.
    """

    if storage_pct is None or net_flow is None or ttf_price is None or carbon_price is None or spread is None:
        return briefing_0

    """
    Generate a dynamic energy-market briefing based on current metric values.
    """
    briefing_1 = f"""
    ### ⚡ Energy Market Daily
    - Gas: EU Storage levels are at {storage_pct}%, with the Net flow being at {net_flow} GWh.
    - TTF-JKM Spread: The TTF-JKM Spread is {spread} EUR/MWh.
    - Futures Markets : TTF futures are currently trading at {ttf_price} EUR/MWh, while Carbon futures are at {carbon_price} €/tCO₂.
    - Market Briefing : The Natural Gas Net Flow of {net_flow} GWh signals a possible move towards market improvement. The positive TTF-JKM spread indicates a potential future increase in European LNG imports, due to better arbitrage opportunities in Europe for LNG suppliers.
    """

    briefing_2 = f"""
    ### ⚡ Energy Market Daily
    - Gas: EU Storage levels are at {storage_pct}%, with the Net flow being at {net_flow} GWh.
    - TTF-JKM Spread: The TTF-JKM Spread is {spread} EUR/MWh.
    - Futures Markets : TTF futures are currently trading at {ttf_price} EUR/MWh, while Carbon futures are at {carbon_price} €/tCO₂.
    - Market Briefing : The Natural Gas Net Flow of {net_flow} GWh shows a struggle for improvement from the market. The positive TTF-JKM spread indicates a potential future increase in European LNG imports, due to better arbitrage opportunities in Europe for LNG suppliers.
    """

    briefing_3 = f"""
    ### ⚡ Energy Market Daily
    - Gas: EU Storage levels are at {storage_pct}%, with the Net flow being at {net_flow} GWh.
    - TTF-JKM Spread: The TTF-JKM Spread is {spread} EUR/MWh.
    - Futures Markets : TTF futures are currently trading at {ttf_price} EUR/MWh, while Carbon futures are at {carbon_price} €/tCO₂.
    - Market Briefing : The Natural Gas Net Flow of {net_flow} GWh signals a possible move towards market improvement. The negative TTF-JKM spread indicates a potential tightening in European LNG supplies, due to better arbitrage opportunities in Asia for LNG suppliers.
    """

    briefing_4 = f"""
    ### ⚡ Energy Market Daily
    - Gas: EU Storage levels are at {storage_pct}%, with the Net flow being at {net_flow} GWh.
    - TTF-JKM Spread: The TTF-JKM Spread is {spread} EUR/MWh.
    - Futures Markets : TTF futures are currently trading at {ttf_price} EUR/MWh, while Carbon futures are at {carbon_price} €/tCO₂.
    - Market Briefing : The Natural Gas Net Flow of {net_flow} GWh shows a struggle for improvement from the market. The negative TTF-JKM spread indicates a potential tightening in European LNG supplies, due to better arbitrage opportunities in Asia for LNG suppliers.
    """
    if net_flow > 0 and spread > 0:
        return briefing_1
    elif net_flow < 0 and spread > 0:
        return briefing_2
    elif net_flow > 0 and spread < 0:
        return briefing_3
    elif net_flow < 0 and spread < 0:
        return briefing_4

    return ""