"""Static catalog charts for the EDA dashboard."""

from __future__ import annotations

import plotly.graph_objects as go

from dashboard.theme import FRANCHISE_COLORS, LICENSED_COLOR, ORIGINAL_COLOR, apply_plotly_theme, franchise_color

TOP_N = 15


def fig_franchise_depth(franchises_df, top_n: int = TOP_N) -> go.Figure:
    """Top franchise/IP groups by catalog size."""
    df = franchises_df.head(top_n).sort_values("titles", ascending=True)
    colors = [franchise_color(f) for f in df["franchise"]]

    fig = go.Figure(
        go.Bar(
            y=df["franchise"],
            x=df["titles"],
            orientation="h",
            marker=dict(color=colors),
            text=df["titles"],
            texttemplate="%{text:,}",
            textposition="outside",
            textfont=dict(size=11, color="#8b949e"),
            hovertemplate="<b>%{y}</b><br>%{x:,} titles<extra></extra>",
        )
    )
    fig.update_xaxes(title="Titles in catalog", rangemode="tozero")
    fig.update_yaxes(title="")
    fig.update_layout(showlegend=False)
    return apply_plotly_theme(fig, f"Top {top_n} franchise & IP groups", height=420)


def fig_original_vs_licensed(franchises_df, top_n: int = TOP_N) -> go.Figure:
    """Exclusive originals vs licensed library for the largest groups."""
    df = franchises_df.head(top_n).sort_values("titles", ascending=False)

    fig = go.Figure(
        data=[
            go.Bar(
                name="Disney+ Original",
                x=df["franchise"],
                y=df["originals"],
                marker=dict(color=ORIGINAL_COLOR),
                hovertemplate="<b>%{x}</b><br>Originals: %{y:,}<extra></extra>",
            ),
            go.Bar(
                name="Licensed library",
                x=df["franchise"],
                y=df["licensed"],
                marker=dict(color=LICENSED_COLOR),
                hovertemplate="<b>%{x}</b><br>Licensed: %{y:,}<extra></extra>",
            ),
        ]
    )
    fig.update_layout(barmode="stack", xaxis_tickangle=-35)
    fig.update_yaxes(title="Titles", rangemode="tozero")
    return apply_plotly_theme(fig, "Original vs licensed mix (top groups)", height=420)


def fig_family_ratings(ratings_df) -> go.Figure:
    """Content rating distribution — reflects family-brand positioning."""
    import pandas as pd

    order = ["G", "PG", "PG-13", "R", "NR", "TV-Y", "TV-Y7", "TV-G", "TV-PG", "TV-14", "TV-MA", "Unknown"]
    df = ratings_df.copy()
    df["content_rating"] = df["content_rating"].astype(str)
    categories = [r for r in order if r in df["content_rating"].values]
    categories += [r for r in df["content_rating"] if r not in categories]
    df["content_rating"] = pd.Categorical(df["content_rating"], categories=categories, ordered=True)
    df = df.sort_values("content_rating")

    fig = go.Figure(
        go.Bar(
            x=df["content_rating"].astype(str),
            y=df["title_count"],
            marker=dict(color="#0063e5"),
            text=df["title_count"],
            texttemplate="%{text:,}",
            textposition="outside",
            textfont=dict(size=10, color="#8b949e"),
            hovertemplate="<b>%{x}</b><br>%{y:,} titles<extra></extra>",
        )
    )
    fig.update_xaxes(title="Rating")
    fig.update_yaxes(title="Titles", rangemode="tozero")
    fig.update_layout(showlegend=False)
    return apply_plotly_theme(fig, "Content ratings (audience positioning)", height=380)
