"""
Application-wide configuration constants.
"""
from datetime import date, timedelta

# ── Default date range ────────────────────────────────────────────
DEFAULT_START_DATE = date.today() - timedelta(days=365)
DEFAULT_END_DATE = date.today()

# ── Pre-configured Yahoo Finance tickers for European commodities ─
COMMODITY_TICKERS = {
    "TTF Natural Gas (Dutch)": "TTF=F",
    "Brent Crude Oil": "BZ=F",
    "WTI Crude Oil": "CL=F",
    "Henry Hub Natural Gas": "NG=F",
    "EUA Carbon Permits": "CFI2Z4.ICE",
    "EU Power (EDF proxy)": "EDF.PA",
}

# ── Technical indicator catalogue (grouped by category) ───────────
OVERLAY_INDICATORS = {
    "SMA (20)": "sma_20",
    "SMA (50)": "sma_50",
    "EMA (20)": "ema_20",
    "EMA (50)": "ema_50",
    "Bollinger Bands": "bbands",
    "Ichimoku Cloud": "ichimoku",
}

SUBPLOT_INDICATORS = {
    "RSI (14)": "rsi",
    "MACD": "macd",
    "Stochastic Oscillator": "stoch",
    "Williams %R": "willr",
    "ATR (14)": "atr",
    "OBV": "obv",
}

# ── Metrics placeholders (page 2) ─────────────────────────────────
METRIC_CARDS = [
    {"key": "gas_storage",   "title": "EU Gas Storage",             "unit": "% Full",   "icon": "🔵"},
    {"key": "gas_net_flow",  "title": "Gas Net Flow",               "unit": "GWh",      "icon": "🔄"},
    {"key": "elec_price",    "title": "Day-Ahead Electricity",      "unit": "€/MWh",    "icon": "⚡"},
    {"key": "ttf_futures",   "title": "TTF Futures",                "unit": "€/MWh",    "icon": "🔥"},
    {"key": "carbon_price",  "title": "EU Carbon Futures",          "unit": "€/tCO₂",   "icon": "🌿"},
    {"key": "ttf_jkm_spread","title": "TTF-JKM Spread",            "unit": "€/MWh",    "icon": "🌊"},
    {"key": "solar_wind",    "title": "Solar & Wind Forecast",      "unit": "MW",       "icon": "☀️"},
    {"key": "briefing",      "title": "Market Briefing",            "unit": "",         "icon": "📰"},
]

# ── API Configuration ─────────────────────────────────────────────
GIE_AGSI_API_KEY = "d0c9cee764f42468fa79a55eb38b41d8"
ENTSOE_API_KEY = "17f05ea0-a80f-4939-beb2-d1e5471a50d3"

# ── GIE AGSI Regions ─────────────────────────────────────────────
GIE_REGIONS = {
    "EU (All)": "eu",
    "Germany": "de",
    "France": "fr",
    "Italy": "it",
    "Netherlands": "nl",
    "Spain": "es",
    "Austria": "at",
    "Belgium": "be",
}

# ── SMARD (German Electricity Market) ────────────────────────────
SMARD_FILTERS = {
    "Day-Ahead Prices": "4169",
    "Intraday Prices": "5078",
}
SMARD_REGIONS = {
    "DE-LU (Germany-Luxembourg)": "DE-LU",
    "AT (Austria)": "AT",
}

# ── ENTSO-E Country Codes ────────────────────────────────────────
ENTSOE_COUNTRIES = {
    "DE-LU (Germany-Luxembourg)": "DE_LU",
    "FR (France)": "FR",
    "IT (Italy)": "IT_NORD",
    "ES (Spain)": "ES",
    "NL (Netherlands)": "NL",
}

# ── TTF Futures Periods ──────────────────────────────────────────
TTF_PERIODS = {
    "1 Month": "1mo",
    "3 Months": "3mo",
    "6 Months": "6mo",
    "1 Year": "1y",
    "2 Years": "2y",
    "5 Years": "5y",
}

# ── Colour palette ────────────────────────────────────────────────
COLORS = {
    "bg_dark": "#ffffff",
    "card_bg": "#1A1D26",
    "card_border": "#2D3340",
    "accent_green": "#00D26A",
    "accent_red": "#FF4B4B",
    "accent_blue": "#4DA3FF",
    "accent_orange": "#FF8C00",
    "accent_purple": "#A855F7",
    "text_primary": "#FAFAFA",
    "text_secondary": "#8B8D97",
}

