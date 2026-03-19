"""
Page 3 — AI Chatbot

Gemini-powered chatbot specialising in European energy commodity analysis.
Provides insights on the metrics displayed in the Commodities Metrics page.
"""
from __future__ import annotations

import streamlit as st

# System prompt giving the LLM deep context about the dashboard
SYSTEM_PROMPT = """\
You are an expert energy-market analyst embedded in a European Commodities Dashboard.
You specialise in natural gas, electricity, carbon emissions, and LNG markets.

The dashboard you are part of displays the following live metrics:
1. **EU Gas Storage** — % full and daily injection/withdrawal net flow, sourced from the GIE AGSI API (https://agsi.gie.eu). Configurable by region (EU, DE, FR, IT, NL, ES, AT, BE).
2. **Day-Ahead Electricity Prices** — hourly prices from the SMARD API (https://smard.de) for the DE-LU market.
3. **TTF Natural Gas Futures** — prices fetched via Yahoo Finance (ticker TTF=F), representing Dutch Title Transfer Facility futures in €/MWh.
4. **EU Carbon Futures** — EUA (EU Allowance) prices in €/tCO₂, loaded from a CSV of historical data.
5. **TTF-JKM Spread** — the price difference between European TTF and Asian JKM LNG benchmarks, converted to €/MWh using the EUR/USD exchange rate. A positive spread signals European arbitrage attractiveness.
6. **Solar & Wind Generation Forecast** — day-ahead renewable generation forecasts from ENTSO-E for Solar, Wind Onshore, and Wind Offshore.
7. **Market Briefing** — an auto-generated summary combining gas net flow signals and TTF-JKM spread implications.

When answering questions:
- Provide concise, data-driven responses.
- Explain how the metrics relate to each other (e.g., gas storage vs TTF prices, renewables impact on electricity prices).
- If asked about data sources, explain the APIs and how data is collected.
- Use bullet points and bold text for clarity.
- If you don't know something specific, say so rather than guessing.
"""


def render():
    st.markdown("## 🤖 AI Market Analyst")
    st.markdown(
        "<p style='color:#8B8D97;margin-top:-10px;'>"
        "Ask questions about European energy commodities, metrics, and market dynamics.</p>",
        unsafe_allow_html=True,
    )

    # ── Sidebar: API key ──────────────────────────────────────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 🔑 Gemini API Key")
        api_key = st.text_input(
            "Enter your Google Gemini API key",
            type="password",
            help="Get a key at https://aistudio.google.com/apikey",
            label_visibility="collapsed",
        )
        model_name = st.selectbox(
            "Model",
            ["gemini-2.0-flash", "gemini-2.5-flash-preview-05-20", "gemini-2.5-pro-preview-05-06"],
            index=0,
        )

    if not api_key:
        st.info(
            "👈 Enter your **Google Gemini API key** in the sidebar to start chatting.\n\n"
            "You can get a free key at [Google AI Studio](https://aistudio.google.com/apikey)."
        )
        return

    # ── Initialise Gemini client ──────────────────────────────────
    try:
        from google import genai
        client = genai.Client(api_key=api_key)
    except Exception as e:
        st.error(f"Failed to initialise Gemini: {e}")
        return

    # ── Chat history in session state ─────────────────────────────
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    # Render existing messages
    for msg in st.session_state.chat_messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Chat input ────────────────────────────────────────────────
    if prompt := st.chat_input("Ask about commodity metrics, data sources, or market outlook…"):
        # Show user message
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Build contents list for Gemini
        contents = []
        for msg in st.session_state.chat_messages:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})

        # Get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking…"):
                try:
                    response = client.models.generate_content(
                        model=model_name,
                        contents=contents,
                        config={
                            "system_instruction": SYSTEM_PROMPT,
                        },
                    )
                    reply = response.text
                except Exception as e:
                    reply = f"⚠️ Error from Gemini API: {e}"

                st.markdown(reply)

        st.session_state.chat_messages.append({"role": "assistant", "content": reply})
