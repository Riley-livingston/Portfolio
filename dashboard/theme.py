"""Streamlit layout and shared chart styling."""

from __future__ import annotations

import plotly.graph_objects as go
import streamlit as st

NAVY = "#0c1116"
PANEL = "#161b22"
GRID = "#2d333b"
TEXT = "#e6edf3"
MUTED = "#8b949e"
ACCENT = "#0063e5"
ORIGINAL_COLOR = "#00c2cb"
LICENSED_COLOR = "#484f58"

# High-contrast palette for multi-series scatter on dark backgrounds (max visual separation)
SCATTER_PALETTE = [
    "#FF6B6B",  # coral
    "#4ECDC4",  # teal
    "#FFE066",  # gold
    "#A78BFA",  # violet
    "#60A5FA",  # sky blue
    "#F472B6",  # pink
    "#34D399",  # emerald
    "#FB923C",  # orange
    "#94A3B8",  # slate (Other / overflow groups)
]

def scatter_group_colors(groups: list[str]) -> dict[str, str]:
    """Map group labels to distinct scatter colors."""
    mapping: dict[str, str] = {}
    idx = 0
    for group in groups:
        if group == "Other groups":
            mapping[group] = SCATTER_PALETTE[-1]
        else:
            mapping[group] = SCATTER_PALETTE[idx % (len(SCATTER_PALETTE) - 1)]
            idx += 1
    return mapping


FRANCHISE_COLORS: dict[str, str] = {
    "Marvel": "#e62429",
    "StarWars": "#ffd700",
    "Pixar": "#0093ff",
    "Disney": "#0063e5",
    "NatGeo": "#ffcc00",
    "Star": "#ff6900",
    "ESPN": "#ff0033",
    "Hulu": "#1ce783",
    "Other": "#6e7681",
    "Pirates of the Caribbean": "#8b6914",
    "Indiana Jones": "#b8860b",
    "20th Century Studios": "#708090",
    "Disney Channel": "#7b68ee",
}


def franchise_color(name: str) -> str:
    if name in FRANCHISE_COLORS:
        return FRANCHISE_COLORS[name]
    hue = sum(ord(c) for c in name) % 360
    return f"hsl({hue}, 55%, 55%)"

BASE_LAYOUT = dict(
    paper_bgcolor=NAVY,
    plot_bgcolor=PANEL,
    font=dict(family="Inter, system-ui, sans-serif", color=TEXT, size=13),
    margin=dict(l=48, r=24, t=72, b=48),
    title=dict(font=dict(size=16, color=TEXT), x=0, xanchor="left"),
    legend=dict(
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
        font=dict(color=MUTED, size=12),
    ),
    hoverlabel=dict(bgcolor=PANEL, bordercolor=GRID, font_color=TEXT),
)

CUSTOM_CSS = """
<style>
    .stApp { background-color: #0c1116; }
    [data-testid="stMetricValue"] { font-size: 1.75rem; font-weight: 700; color: #e6edf3; }
    [data-testid="stMetricLabel"] {
        color: #8b949e;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.04em;
        white-space: normal !important;
        overflow: visible !important;
        text-overflow: clip !important;
        line-height: 1.25;
    }
    [data-testid="stMetricDelta"] { font-size: 0.8rem; }
    h1, h2, h3 { color: #e6edf3 !important; }
    .block-container { padding-top: 2rem; }
    .eda-caption { color: #8b949e; font-size: 0.95rem; margin-bottom: 1.25rem; line-height: 1.5; }
    .eda-insight { background: #161b22; border-left: 3px solid #0063e5; padding: 0.75rem 1rem; border-radius: 0 8px 8px 0; color: #c9d1d9; font-size: 0.9rem; margin-top: 0.5rem; }
</style>
"""


def inject_styles() -> None:
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


def metric_row(items: list[tuple[str, str | int, str | None]]) -> None:
    cols = st.columns(len(items))
    for col, (label, value, delta) in zip(cols, items):
        if delta:
            col.metric(label, value, delta=delta)
        else:
            col.metric(label, value)


def apply_plotly_theme(fig: go.Figure, title: str, height: int = 420) -> go.Figure:
    layout = {**BASE_LAYOUT, "height": height}
    layout["title"] = {**BASE_LAYOUT["title"], "text": title}
    fig.update_layout(**layout)
    fig.update_xaxes(
        showgrid=True,
        gridcolor=GRID,
        linecolor=GRID,
        zeroline=False,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=GRID,
        linecolor=GRID,
        zeroline=False,
        tickfont=dict(color=MUTED),
        title_font=dict(color=MUTED),
    )
    return fig
