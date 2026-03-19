"""
Page 2 — Commodities Metrics

Live market metrics with interactive controls, summary cards, and charts.
Data sourced from GIE AGSI, SMARD, yfinance, ENTSO-E, and CSV uploads.
"""
from __future__ import annotations

import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

from config import (
    COLORS,
    METRIC_CARDS,
    GIE_AGSI_API_KEY,
    ENTSOE_API_KEY,
    GIE_REGIONS,
    SMARD_FILTERS,
    SMARD_REGIONS,
    ENTSOE_COUNTRIES,
    TTF_PERIODS,
)
from data.metrics_fetchers import (
    fetch_eu_gas_storage,
    fetch_electricity_prices,
    fetch_ttf_futures,
    load_carbon_futures,
    compute_ttf_jkm_spread,
    fetch_solar_wind_forecast,
    generate_market_briefing,
)


# ─────────────────────── Styled card HTML ─────────────────────────

def _card(icon: str, title: str, value: str, unit: str, accent: str) -> str:
    return f"""
    <div style="
        background: {COLORS['card_bg']};
        border: 1px solid {COLORS['card_border']};
        border-left: 4px solid {accent};
        border-radius: 12px;
        padding: 18px 16px;
        min-height: 120px;
        display: flex; flex-direction: column;
        justify-content: space-between;
    ">
        <p style="margin:0;font-size:12px;font-weight:600;
           color:{COLORS['text_secondary']};letter-spacing:.5px;
           text-transform:uppercase;">{icon} {title}</p>
        <div>
            <span style="font-size:26px;font-weight:700;
                  color:{COLORS['text_primary']};">{value}</span>
            <span style="font-size:13px;color:{COLORS['text_secondary']};
                  margin-left:4px;">{unit}</span>
        </div>
    </div>
    """


ACCENTS = [
    COLORS["accent_blue"], COLORS["accent_green"],
    COLORS["accent_orange"], COLORS["accent_red"],
    COLORS["accent_purple"], COLORS["accent_blue"],
    COLORS["accent_orange"], COLORS["accent_green"],
]


# ─────────────────────── Dark Plotly helper ───────────────────────

def _dark_layout(fig, title: str, xlab: str, ylab: str):
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["bg_dark"],
        plot_bgcolor="#141720",
        title=dict(text=title, x=0.5, font=dict(size=18)),
        xaxis_title=xlab,
        yaxis_title=ylab,
        margin=dict(l=50, r=20, t=50, b=40),
        height=380,
    )
    fig.update_xaxes(gridcolor="#1F2333")
    fig.update_yaxes(gridcolor="#1F2333")
    return fig


# ═══════════════════════════ RENDER ═══════════════════════════════

def render():
    st.markdown("## 🏭 Commodities Metrics")
    st.markdown(
        "<p style='color:#8B8D97;margin-top:-10px;'>"
        "Live market indicators for European energy commodities.</p>",
        unsafe_allow_html=True,
    )

    # ── Sidebar controls ──────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("### ⚙️ Metrics Parameters")

        # API Keys
        with st.expander("🔑 API Keys", expanded=False):
            gie_key = st.text_input("GIE AGSI Key", value=GIE_AGSI_API_KEY, type="password")
            entsoe_key = st.text_input("ENTSO-E Key", value=ENTSOE_API_KEY, type="password")

        # Gas Storage
        st.markdown("**🔵 Gas Storage**")
        gie_region_label = st.selectbox("Region", list(GIE_REGIONS.keys()), index=0)
        gie_region = GIE_REGIONS[gie_region_label]
        gie_size = st.slider("History (days)", 30, 300, 300)

        # Electricity
        st.markdown("**⚡ Electricity**")
        smard_filter_label = st.selectbox("Market", list(SMARD_FILTERS.keys()), index=0)
        smard_filter = SMARD_FILTERS[smard_filter_label]
        smard_region_label = st.selectbox("Elec Region", list(SMARD_REGIONS.keys()), index=0)
        smard_region = SMARD_REGIONS[smard_region_label]

        # TTF Futures
        st.markdown("**🔥 TTF Futures**")
        ttf_period_label = st.selectbox("Period", list(TTF_PERIODS.keys()), index=3)
        ttf_period = TTF_PERIODS[ttf_period_label]

        # Solar & Wind
        st.markdown("**☀️ Solar & Wind**")
        entsoe_country_label = st.selectbox("Country", list(ENTSOE_COUNTRIES.keys()), index=0)
        entsoe_country = ENTSOE_COUNTRIES[entsoe_country_label]
        sw_start = st.date_input("Forecast start", datetime.now().date())
        sw_end = st.date_input("Forecast end", datetime.now().date() + timedelta(days=2))

        # CSV Uploads
        st.markdown("---")
        st.markdown("### 📂 CSV Data Uploads")
        carbon_csv = st.file_uploader("Carbon Futures CSV", type=["csv"], key="carbon")
        st.caption("TTF-JKM Spread requires 3 CSVs:")
        ttf_hist_csv = st.file_uploader("TTF Historical CSV", type=["csv"], key="ttf_hist")
        jkm_csv = st.file_uploader("JKM Historical CSV", type=["csv"], key="jkm")
        eurusd_csv = st.file_uploader("EURUSD Historical CSV", type=["csv"], key="eurusd")

    # ── Fetch all metrics ─────────────────────────────────────────
    values: dict = {}  # key → display value string
    data: dict = {}    # key → DataFrame (for charts)

    # 1 — Gas Storage
    try:
        gas_sum, gas_df = fetch_eu_gas_storage(gie_key, gie_region, gie_size)
        values["gas_storage"] = f"{gas_sum['storage_pct']:.1f}" if gas_sum["storage_pct"] is not None else "—"
        values["gas_net_flow"] = f"{gas_sum['net_flow']:+.1f}" if gas_sum["net_flow"] is not None else "—"
        data["gas_storage"] = gas_df
    except Exception as e:
        values["gas_storage"] = "err"
        values["gas_net_flow"] = "err"
        data["gas_storage"] = pd.DataFrame()
        st.toast(f"Gas Storage: {e}", icon="⚠️")

    # 2 — Electricity
    try:
        elec_sum, elec_df = fetch_electricity_prices(smard_filter, smard_region)
        values["elec_price"] = f"{elec_sum['latest_price']:.2f}" if elec_sum["latest_price"] is not None else "—"
        data["elec_price"] = elec_df
    except Exception as e:
        values["elec_price"] = "err"
        data["elec_price"] = pd.DataFrame()
        st.toast(f"Electricity: {e}", icon="⚠️")

    # 3 — TTF Futures
    try:
        ttf_sum, ttf_df = fetch_ttf_futures(ttf_period)
        values["ttf_futures"] = f"{ttf_sum['latest_price']:.2f}" if ttf_sum["latest_price"] is not None else "—"
        data["ttf_futures"] = ttf_df
    except Exception as e:
        values["ttf_futures"] = "err"
        data["ttf_futures"] = pd.DataFrame()
        st.toast(f"TTF Futures: {e}", icon="⚠️")

    # 4 — Carbon Futures (CSV)
    if carbon_csv is not None:
        try:
            carb_sum, carb_df = load_carbon_futures(carbon_csv)
            values["carbon_price"] = f"{carb_sum['latest_price']:.2f}" if carb_sum["latest_price"] is not None else "—"
            data["carbon_price"] = carb_df
        except Exception as e:
            values["carbon_price"] = "err"
            data["carbon_price"] = pd.DataFrame()
            st.toast(f"Carbon: {e}", icon="⚠️")
    else:
        values["carbon_price"] = "📂"
        data["carbon_price"] = pd.DataFrame()

    # 5 — TTF-JKM Spread (3 CSVs)
    if all([ttf_hist_csv, jkm_csv, eurusd_csv]):
        try:
            spread_sum, spread_df = compute_ttf_jkm_spread(ttf_hist_csv, jkm_csv, eurusd_csv)
            values["ttf_jkm_spread"] = f"{spread_sum['latest_spread']:+.2f}" if spread_sum["latest_spread"] is not None else "—"
            data["ttf_jkm_spread"] = spread_df
        except Exception as e:
            values["ttf_jkm_spread"] = "err"
            data["ttf_jkm_spread"] = pd.DataFrame()
            st.toast(f"Spread: {e}", icon="⚠️")
    else:
        values["ttf_jkm_spread"] = "📂"
        data["ttf_jkm_spread"] = pd.DataFrame()

    # 6 — Solar & Wind
    try:
        sw_sum, sw_df = fetch_solar_wind_forecast(entsoe_key, entsoe_country, sw_start, sw_end)
        values["solar_wind"] = f"{sw_sum['total']:,.0f}" if sw_sum["total"] is not None else "—"
        data["solar_wind"] = sw_df
    except Exception as e:
        values["solar_wind"] = "err"
        data["solar_wind"] = pd.DataFrame()
        st.toast(f"Solar/Wind: {e}", icon="⚠️")

    # 7 — Market Briefing
    briefing_text = generate_market_briefing(
        storage_pct=_safe_float(values.get("gas_storage")),
        net_flow=_safe_float(values.get("gas_net_flow")),
        ttf_price=_safe_float(values.get("ttf_futures")),
        carbon_price=_safe_float(values.get("carbon_price")),
        spread=_safe_float(values.get("ttf_jkm_spread")),
    )
    values["briefing"] = "✔"

    # ── Render summary cards (2 × 4 grid) ─────────────────────────
    for row_start in range(0, len(METRIC_CARDS), 4):
        cols = st.columns(4, gap="medium")
        for j, col in enumerate(cols):
            idx = row_start + j
            if idx >= len(METRIC_CARDS):
                break
            card = METRIC_CARDS[idx]
            val = values.get(card["key"], "—")
            col.markdown(
                _card(card["icon"], card["title"], val, card["unit"], ACCENTS[idx]),
                unsafe_allow_html=True,
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Detailed charts in expanders ──────────────────────────────

    # Gas Storage
    with st.expander("🔵 EU Gas Storage — detailed charts", expanded=False):
        df = data.get("gas_storage")
        if df is not None and not df.empty:
            c1, c2 = st.columns(2)
            with c1:
                fig = px.line(df, x=df.index, y="full")
                fig = _dark_layout(fig, "EU Gas Storage Levels (%)", "Date",
                                   "Storage Level (%)")
                st.plotly_chart(fig, width="stretch")
            with c2:
                fig = px.bar(df, x=df.index, y="injection-withdrawal")
                fig = _dark_layout(fig,
                                   "Gas Injection − Withdrawal (GWh/day)",
                                   "Date", "Net Flow (GWh)")
                st.plotly_chart(fig, width="stretch")
        else:
            st.info("No gas-storage data available.")

    # Electricity
    with st.expander("⚡ Day-Ahead Electricity Prices", expanded=False):
        df = data.get("elec_price")
        if df is not None and not df.empty:
            fig = px.line(df, x=df.index, y="Price_EUR_MWh")
            fig = _dark_layout(fig,
                               f"Day-Ahead Prices — {smard_region_label}",
                               "Date", "Price (€/MWh)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No electricity data available.")

    # TTF Futures
    with st.expander("🔥 TTF Natural Gas Futures", expanded=False):
        df = data.get("ttf_futures")
        if df is not None and not df.empty:
            fig = px.line(df, x=df.index, y="Open")
            fig = _dark_layout(fig, "TTF Futures Prices", "Date",
                               "Price (€/MWh)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No TTF data available.")

    # Carbon Futures
    with st.expander("🌿 EU Carbon Futures", expanded=False):
        df = data.get("carbon_price")
        if df is not None and not df.empty and "Price" in df.columns:
            fig = px.line(df, x=df.index, y="Price")
            fig = _dark_layout(fig, "EU Carbon Futures Prices", "Date",
                               "Price (€/tCO₂)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Upload **Carbon Emissions Futures Historical Data.csv** in the sidebar.")

    # TTF-JKM Spread
    with st.expander("🌊 TTF-JKM Spread", expanded=False):
        df = data.get("ttf_jkm_spread")
        if df is not None and not df.empty and "TTF-JKM" in df.columns:
            fig = px.area(df, x=df.index, y="TTF-JKM")
            fig = _dark_layout(fig, "TTF − JKM Price Spread", "Date",
                               "Spread (€/MWh)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("Upload all 3 CSV files (TTF hist, JKM hist, EURUSD hist) in the sidebar.")

    # Solar & Wind
    with st.expander("☀️ Solar & Wind Generation Forecast", expanded=False):
        df = data.get("solar_wind")
        if df is not None and not df.empty:
            plot_cols = [c for c in ["Solar", "Wind Onshore", "Wind Offshore", "Total Energy"] if c in df.columns]
            fig = px.line(df, x=df.index, y=plot_cols)
            fig = _dark_layout(fig,
                               f"Day-Ahead Forecast — {entsoe_country_label}",
                               "Date", "Generation (MW)")
            st.plotly_chart(fig, width="stretch")
        else:
            st.info("No solar/wind forecast data available.")

    # Market Briefing
    with st.expander("📰 Market Briefing", expanded=True):
        st.markdown(briefing_text)


# ─────────────────────── utility ──────────────────────────────────

def _safe_float(val: str | None) -> float | None:
    """Try converting a card display value back to float."""
    if val is None:
        return None
    try:
        return float(val.replace("+", "").replace(",", ""))
    except (ValueError, AttributeError):
        return None
