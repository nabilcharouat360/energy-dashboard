"""
Page 1 — Technical Analysis

Data source selection (Yahoo Finance / CSV upload), indicator picker,
and interactive Plotly candlestick chart.
"""
import streamlit as st

from config import (
    COMMODITY_TICKERS,
    DEFAULT_START_DATE,
    DEFAULT_END_DATE,
    OVERLAY_INDICATORS,
    SUBPLOT_INDICATORS,
)
from data.loader import load_from_yfinance, load_from_csv
from analysis.indicators import apply_indicators
from charts.candlestick import build_candlestick


def render():
    st.markdown("## 📈 Technical Analysis")
    st.markdown(
        "<p style='color:#8B8D97;margin-top:-10px;'>"
        "Analyse European commodity prices with professional-grade indicators.</p>",
        unsafe_allow_html=True,
    )

    # ── Sidebar data-source controls ──────────────────────────────
    with st.sidebar:
        st.markdown("### 📊 Data Source")
        source = st.radio(
            "Choose data source",
            ["Yahoo Finance", "CSV Upload"],
            horizontal=True,
            label_visibility="collapsed",
        )

        if source == "Yahoo Finance":
            ticker_label = st.selectbox("Commodity", list(COMMODITY_TICKERS.keys()))
            ticker = COMMODITY_TICKERS[ticker_label]
            col_s, col_e = st.columns(2)
            start = col_s.date_input("Start", DEFAULT_START_DATE)
            end = col_e.date_input("End", DEFAULT_END_DATE)
        else:
            uploaded = st.file_uploader(
                "Upload OHLCV CSV",
                type=["csv"],
                help="Columns: Date, Open, High, Low, Close (Volume optional)",
            )

        # ── Indicator controls ───────────────────────────────────
        st.markdown("---")
        st.markdown("### 🔧 Overlay Indicators")
        selected_overlays = st.multiselect(
            "Overlays",
            options=list(OVERLAY_INDICATORS.keys()),
            default=["SMA (20)"],
            label_visibility="collapsed",
        )
        st.markdown("### 📉 Subplot Indicators")
        selected_subplots = st.multiselect(
            "Subplots",
            options=list(SUBPLOT_INDICATORS.keys()),
            default=["RSI (14)"],
            label_visibility="collapsed",
        )

    # ── Load data ─────────────────────────────────────────────────
    df = None
    if source == "Yahoo Finance":
        with st.spinner("Downloading data from Yahoo Finance…"):
            df = load_from_yfinance(ticker, start, end)
        if df is not None and df.empty:
            st.warning(
                f"No data returned for **{ticker_label}** (`{ticker}`). "
                "Try a different ticker or date range."
            )
            return
    else:
        if uploaded is not None:
            try:
                df = load_from_csv(uploaded)
            except ValueError as exc:
                st.error(str(exc))
                return
        else:
            st.info("👆 Upload a CSV file using the sidebar to get started.")
            return

    if df is None or df.empty:
        return

    # ── Quick stats bar ───────────────────────────────────────────
    last = df.iloc[-1]
    prev = df.iloc[-2] if len(df) > 1 else last
    change = last["Close"] - prev["Close"]
    pct = (change / prev["Close"]) * 100 if prev["Close"] != 0 else 0

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Close", f"{last['Close']:.2f}", f"{change:+.2f} ({pct:+.1f}%)")
    m2.metric("High", f"{last['High']:.2f}")
    m3.metric("Low", f"{last['Low']:.2f}")
    m4.metric("Volume", f"{int(last['Volume']):,}")

    # ── Apply indicators ──────────────────────────────────────────
    indicator_keys = (
        [OVERLAY_INDICATORS[k] for k in selected_overlays]
        + [SUBPLOT_INDICATORS[k] for k in selected_subplots]
    )
    df = apply_indicators(df, indicator_keys)

    # ── Render chart ──────────────────────────────────────────────
    fig = build_candlestick(df)
    st.plotly_chart(fig, width="stretch")

    # ── Raw data expander ─────────────────────────────────────────
    with st.expander("📋 View raw data"):
        st.dataframe(df, width="stretch")
