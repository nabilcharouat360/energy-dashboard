"""
Candlestick chart builder using Plotly.

Produces a single figure with:
  - Main pane   : candlestick + overlay indicators (SMA, EMA, Bollinger, Ichimoku)
  - Sub-panes   : one per subplot indicator (RSI, MACD, Stochastic, etc.)
"""
from __future__ import annotations

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd

from config import COLORS


# ───────── helpers to decide which sub-pane an indicator belongs to ─────────

_SUBPLOT_COLUMNS = {
    "RSI":        ["RSI"],
    "MACD":       ["MACD", "MACD_Signal", "MACD_Hist"],
    "Stochastic": ["Stoch_K", "Stoch_D"],
    "Williams %R": ["Williams_R"],
    "ATR":        ["ATR"],
    "OBV":        ["OBV"],
}

_OVERLAY_COLUMNS = {
    "SMA":       lambda df: [c for c in df.columns if c.startswith("SMA_")],
    "EMA":       lambda df: [c for c in df.columns if c.startswith("EMA_")],
    "Bollinger": lambda df: [c for c in df.columns if c.startswith("BB_")],
    "Ichimoku":  lambda df: [c for c in df.columns if c.startswith("Ichimoku_")],
}


def _detect_subplots(df: pd.DataFrame) -> list[str]:
    """Return list of subplot indicator names present in *df*."""
    found: list[str] = []
    for name, cols in _SUBPLOT_COLUMNS.items():
        if any(c in df.columns for c in cols):
            found.append(name)
    return found


# ───────────────────────── main builder ────────────────────────────

def build_candlestick(df: pd.DataFrame) -> go.Figure:
    """
    Build a Plotly figure with candlestick chart, overlays, and
    dynamically generated subplots for secondary indicators.
    """
    subplot_names = _detect_subplots(df)
    n_subplots = 1 + len(subplot_names)          # main + each indicator

    # Proportional row heights: main chart gets most space
    row_heights = [0.55] + [0.45 / max(len(subplot_names), 1)] * len(subplot_names)
    if not subplot_names:
        row_heights = [1.0]

    titles = [""] + subplot_names
    fig = make_subplots(
        rows=n_subplots, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
        subplot_titles=titles,
    )

    # ── Candlestick ──
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df["Open"], high=df["High"],
            low=df["Low"], close=df["Close"],
            increasing_line_color=COLORS["accent_green"],
            decreasing_line_color=COLORS["accent_red"],
            name="Price",
        ),
        row=1, col=1,
    )

    # ── Overlay indicators ──
    palette = ["#4DA3FF", "#FF8C00", "#A855F7", "#22D3EE", "#F472B6", "#34D399"]
    color_idx = 0

    for group_name, col_fn in _OVERLAY_COLUMNS.items():
        cols = col_fn(df)
        for col in cols:
            if col not in df.columns:
                continue
            # Ichimoku cloud fill
            if col == "Ichimoku_B" and "Ichimoku_A" in df.columns:
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=df["Ichimoku_A"],
                        line=dict(width=0), showlegend=False,
                        hoverinfo="skip",
                    ),
                    row=1, col=1,
                )
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=df["Ichimoku_B"],
                        fill="tonexty",
                        fillcolor="rgba(77,163,255,0.10)",
                        line=dict(width=0),
                        name="Ichimoku Cloud",
                    ),
                    row=1, col=1,
                )
                continue
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df[col],
                    mode="lines",
                    line=dict(width=1.2, color=palette[color_idx % len(palette)]),
                    name=col,
                ),
                row=1, col=1,
            )
            color_idx += 1

    # ── Subplot indicators ──
    for i, name in enumerate(subplot_names, start=2):
        cols = _SUBPLOT_COLUMNS[name]
        for col in cols:
            if col not in df.columns:
                continue
            if col == "MACD_Hist":
                colours = [
                    COLORS["accent_green"] if v >= 0 else COLORS["accent_red"]
                    for v in df[col]
                ]
                fig.add_trace(
                    go.Bar(x=df.index, y=df[col], marker_color=colours, name=col, showlegend=False),
                    row=i, col=1,
                )
            else:
                fig.add_trace(
                    go.Scatter(
                        x=df.index, y=df[col],
                        mode="lines", line=dict(width=1.2),
                        name=col,
                    ),
                    row=i, col=1,
                )
        # Reference lines for RSI / Stochastic
        if name == "RSI":
            for lvl in (30, 70):
                fig.add_hline(y=lvl, line_dash="dot", line_color=COLORS["text_secondary"],
                              opacity=0.5, row=i, col=1)
        if name == "Stochastic":
            for lvl in (20, 80):
                fig.add_hline(y=lvl, line_dash="dot", line_color=COLORS["text_secondary"],
                              opacity=0.5, row=i, col=1)

    # ── Layout ──
    height = 500 + 180 * len(subplot_names)
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor=COLORS["bg_dark"],
        plot_bgcolor="#141720",
        height=height,
        margin=dict(l=50, r=20, t=30, b=30),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.01,
            xanchor="left", x=0, font=dict(size=11),
        ),
        xaxis_rangeslider_visible=False,
        hovermode="x unified",
    )

    fig.update_xaxes(gridcolor="#1F2333")
    fig.update_yaxes(gridcolor="#1F2333")

    return fig
