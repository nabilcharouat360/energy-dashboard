"""
European Commodities Dashboard — Entry Point
==============================================
Run with:  streamlit run app.py
"""
import streamlit as st
from pathlib import Path

# ── Page config (must be first Streamlit call) ────────────────────
st.set_page_config(
    page_title="EU Commodities Dashboard",
    page_icon="🛢️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Inject custom CSS ────────────────────────────────────────────
css_path = Path(__file__).parent / "styles" / "theme.css"
if css_path.exists():
    st.markdown(f"<style>{css_path.read_text()}</style>", unsafe_allow_html=True)

# ── Sidebar header & navigation ──────────────────────────────────
with st.sidebar:
    st.markdown(
        "<h2 style='margin-bottom:2px;'>🛢️ EU Commodities</h2>"
        "<p style='color:#8B8D97;font-size:13px;margin-top:0;'>"
        "Dashboard · v1.0</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["📈 Technical Analysis", "🏭 Commodities Metrics", "🤖 AI Analyst"],
        label_visibility="collapsed",
    )

# ── Route to selected page ───────────────────────────────────────
if page == "📈 Technical Analysis":
    from pages.technical_analysis import render
    render()
elif page == "🏭 Commodities Metrics":
    from pages.commodities_metrics import render
    render()
elif page == "🤖 AI Analyst":
    from pages.ai_chatbot import render
    render()
