# 🛢️ European Commodities Dashboard

An interactive Streamlit dashboard for analysing European energy commodities — natural gas, electricity, carbon emissions, and their interplay with oil and LNG markets.

---

## Features

### 📈 Page 1 — Technical Analysis

Perform professional-grade technical analysis on any commodity price series.

| Capability | Details |
|---|---|
| **Data sources** | Yahoo Finance (pre-configured tickers: TTF, Brent, WTI, Henry Hub, EUA Carbon, EDF) **or** CSV upload |
| **Overlay indicators** | SMA (20/50), EMA (20/50), Bollinger Bands, Ichimoku Cloud |
| **Subplot indicators** | RSI, MACD, Stochastic Oscillator, Williams %R, ATR, OBV |
| **Chart** | Interactive Plotly candlestick with zoom, pan, and hover |
| **Quick stats** | Close, High, Low, Volume with daily delta |

### 🏭 Page 2 — Commodities Metrics

Live market metrics fetched from real APIs, with interactive parameter controls and detailed charts.

| Metric | Source | Configurable Parameters |
|---|---|---|
| **EU Gas Storage** (% full + net flow) | GIE AGSI API | Region (EU, DE, FR, IT…), history length |
| **Day-Ahead Electricity Prices** | SMARD API | Market type, region (DE-LU, AT) |
| **TTF Natural Gas Futures** | Yahoo Finance | Period (1 month – 5 years) |
| **EU Carbon Futures** | CSV upload | — |
| **TTF-JKM Spread** | CSV upload (3 files) | — |
| **Solar & Wind Generation Forecast** | ENTSO-E API | Country, forecast date range |
| **Market Briefing** | Auto-generated | Computed from the above metrics |

Each metric is displayed as a **summary card** at the top, with an **expandable chart section** below for detailed analysis.

### 🤖 Page 3 — AI Market Analyst

A Gemini-powered chatbot specialising in European energy market analysis.

| Capability | Details |
|---|---|
| **LLM** | Google Gemini (selectable: 2.0 Flash, 2.5 Flash, 2.5 Pro) |
| **Domain knowledge** | Pre-loaded system prompt covering all 7 dashboard metrics, data sources, and market relationships |
| **Chat interface** | Streamlit native `st.chat_input` / `st.chat_message` with full conversation history |
| **API key** | Enter your own Gemini key in the sidebar (free at [AI Studio](https://aistudio.google.com/apikey)) |

---

## Project Structure

```
energy-dashboard/
├── app.py                           # Streamlit entry point & page router
├── config.py                        # Tickers, API keys, indicator catalogue, colour palette
├── requirements.txt                 # Python dependencies
├── metrics.py                       # Original notebook logic (reference)
│
├── data/
│   ├── loader.py                    # yfinance download + CSV upload parser
│   └── metrics_fetchers.py          # One function per metric (GIE, SMARD, ENTSO-E…)
│
├── analysis/
│   └── indicators.py                # 10 TA indicators wrapping the `ta` library
│
├── charts/
│   └── candlestick.py               # Plotly candlestick builder with overlays & subplots
│
├── pages/
│   ├── technical_analysis.py        # Page 1 — interactive technical analysis
│   ├── commodities_metrics.py       # Page 2 — live metrics, cards & charts
│   └── ai_chatbot.py                # Page 3 — Gemini-powered AI analyst
│
└── styles/
    └── theme.css                    # Custom dark theme (Inter font, styled scrollbars)
```

---

## Getting Started

### Prerequisites

- **Python 3.10+** installed
- **pip** package manager

### 1. Install dependencies

```bash
cd energy-dashboard
pip install -r requirements.txt
```

This installs: `streamlit`, `yfinance`, `ta`, `plotly`, `pandas`, `entsoe-py`, `google-genai`.

### 2. Launch the dashboard

```bash
streamlit run app.py
```

The app opens automatically in your browser at [http://localhost:8501](http://localhost:8501). (The port might sometimes be 8503 if a process is already running on 8501, please check the command line to be sure).

### 3. Using the dashboard

**Technical Analysis (Page 1)**
1. Select **Yahoo Finance** or **CSV Upload** in the sidebar.
2. Choose a commodity and date range (or upload your OHLCV CSV).
3. Pick overlay and subplot indicators from the sidebar multiselects.
4. The candlestick chart updates automatically.

**Commodities Metrics (Page 2)**
1. Switch to **🏭 Commodities Metrics** in the sidebar navigation.
2. Adjust API parameters (region, period, dates) in the sidebar — charts refresh on change.
3. Expand any metric section to view its detailed chart.
4. For CSV-based metrics (Carbon Futures, TTF-JKM Spread), upload the required files via the sidebar.

**AI Analyst (Page 3)**
1. Switch to **🤖 AI Analyst** in the sidebar navigation.
2. Enter your **Google Gemini API key** in the sidebar.
3. Choose a model (Gemini 2.0 Flash is fastest; 2.5 Pro is most capable).
4. Ask questions about metrics, data sources, market dynamics, or spreads.

---

## API Keys

The dashboard uses two external APIs with keys pre-configured in `config.py`:

| API | Purpose | Key location |
|---|---|---|
| **GIE AGSI** | EU gas storage levels | `config.py → GIE_AGSI_API_KEY` |
| **ENTSO-E** | Solar & wind generation forecast | `config.py → ENTSOE_API_KEY` |
| **Google Gemini** | AI chatbot | Entered in sidebar at runtime |

GIE AGSI and ENTSO-E keys can be overridden at runtime via the **🔑 API Keys** section in the sidebar.

---

## CSV File Formats

For the CSV-based metrics, the expected file format is:

| File | Required Columns |
|---|---|
| Carbon Emissions Futures | `Date`, `Price` |
| TTF Historical | `Date`, `Price` |
| JKM Historical | `Date`, `Price` |
| EURUSD Historical | `Date`, `Price` |

> **Note:** Example files matching these formats are provided in the `examples/` folder of this project. These datasets are typically sourced from [Investing.com](https://www.investing.com/).

---

## Tech Stack

| Component | Technology |
|---|---|
| UI Framework | [Streamlit](https://streamlit.io/) |
| Charting | [Plotly](https://plotly.com/python/) |
| Technical Analysis | [ta](https://github.com/bukosabino/ta) |
| Market Data | [yfinance](https://github.com/ranaroussi/yfinance) |
| Energy Data | [entsoe-py](https://github.com/EnergieID/entsoe-py), GIE AGSI, SMARD |
| AI / LLM | [Google Gemini](https://ai.google.dev/) via `google-genai` |
