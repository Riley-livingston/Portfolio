"""Catalog insight charts — treemap, heatmap, decades, quality scatter."""

from __future__ import annotations

import pandas as pd
import plotly.graph_objects as go

from dashboard.theme import ACCENT, apply_plotly_theme, franchise_color

TOP_FRANCHISES = 12
TOP_GENRES = 10


def fig_catalog_treemap(franchises_df: pd.DataFrame, top_n: int = 20) -> go.Figure:
    """Block-size view of catalog share by franchise / IP group."""
    df = franchises_df.head(top_n).copy()
    if len(franchises_df) > top_n:
        rest = franchises_df.iloc[top_n:]
        other_row = pd.DataFrame(
            [{"franchise": "All other groups", "titles": int(rest["titles"].sum())}]
        )
        df = pd.concat([df, other_row], ignore_index=True)

    colors = [franchise_color(f) for f in df["franchise"]]

    fig = go.Figure(
        go.Treemap(
            labels=df["franchise"],
            parents=[""] * len(df),
            values=df["titles"],
            marker=dict(colors=colors, line=dict(width=2, color="#0c1116")),
            textinfo="label+value+percent parent",
            textfont=dict(size=13, color="#e6edf3"),
            hovertemplate="<b>%{label}</b><br>%{value:,} titles<br>%{percentParent:.1%} of catalog<extra></extra>",
        )
    )
    fig.update_layout(margin=dict(l=8, r=8, t=72, b=8))
    return apply_plotly_theme(fig, "Catalog composition at a glance", height=440)


def fig_franchise_genre_heatmap(matrix_df: pd.DataFrame) -> go.Figure:
    """Which genres each franchise owns — cell intensity = title count."""
    if matrix_df.empty:
        return apply_plotly_theme(go.Figure(), "Franchise × genre positioning", height=440)

    top_franchises = (
        matrix_df.groupby("franchise")["title_count"].sum().nlargest(TOP_FRANCHISES).index.tolist()
    )
    top_genres = (
        matrix_df.groupby("genre")["title_count"].sum().nlargest(TOP_GENRES).index.tolist()
    )
    df = matrix_df[
        matrix_df["franchise"].isin(top_franchises) & matrix_df["genre"].isin(top_genres)
    ]
    pivot = df.pivot_table(
        index="franchise",
        columns="genre",
        values="title_count",
        aggfunc="sum",
        fill_value=0,
    )
    pivot = pivot.loc[
        pivot.sum(axis=1).sort_values(ascending=False).index,
        pivot.sum(axis=0).sort_values(ascending=False).index,
    ]

    fig = go.Figure(
        go.Heatmap(
            z=pivot.values,
            x=pivot.columns.tolist(),
            y=pivot.index.tolist(),
            colorscale=[[0, "#161b22"], [0.35, "#1f6feb"], [1, "#00c2cb"]],
            hovertemplate="Franchise: %{y}<br>Genre: %{x}<br>Titles: %{z:,}<extra></extra>",
            xgap=2,
            ygap=2,
        )
    )
    fig.update_xaxes(side="bottom", tickangle=-40, automargin=True)
    fig.update_yaxes(automargin=True)
    fig.update_layout(coloraxis_showscale=False)
    fig = apply_plotly_theme(fig, "Where each brand plays — franchise × genre", height=500)
    fig.update_layout(margin=dict(l=140, r=24, t=72, b=130))
    return fig


def fig_release_decades(decades_df: pd.DataFrame) -> go.Figure:
    """Original release era — shows back-catalog depth."""
    df = decades_df.sort_values("release_decade").copy()
    df["decade_label"] = df["release_decade"].astype(int).astype(str) + "s"

    fig = go.Figure(
        go.Bar(
            x=df["decade_label"],
            y=df["title_count"],
            marker=dict(
                color=df["title_count"],
                colorscale=[[0, "#21262d"], [0.45, ACCENT], [1, "#58a6ff"]],
            ),
            text=df["title_count"],
            texttemplate="%{text:,}",
            textposition="outside",
            textfont=dict(size=10, color="#8b949e"),
            hovertemplate="<b>%{x}</b><br>%{y:,} titles<extra></extra>",
        )
    )
    fig.update_layout(coloraxis_showscale=False, showlegend=False)
    fig.update_xaxes(title="Original release decade")
    fig.update_yaxes(title="Titles", rangemode="tozero")
    return apply_plotly_theme(fig, "Library spans decades of releases", height=400)


def fig_franchise_imdb_quality(
    ratings_df: pd.DataFrame,
    top_n: int = 15,
) -> tuple[go.Figure, pd.DataFrame]:
    """Average IMDb for the largest franchises by volume, sorted by rating."""
    df = ratings_df.copy()
    if df.empty:
        return apply_plotly_theme(go.Figure(), "Average IMDb rating by franchise", height=420), df

    agg = (
        df.groupby("franchise", as_index=False)
        .agg(avg_rating=("imdb_rating", "mean"), titles=("imdb_rating", "count"))
        .nlargest(top_n, "titles")
        .sort_values("avg_rating", ascending=True)
    )
    catalog_avg = float(df["imdb_rating"].mean())
    bar_count = len(agg)
    height = max(440, 32 * bar_count + 120)

    colors = ["#34D399" if rating >= catalog_avg else "#64748b" for rating in agg["avg_rating"]]

    fig = go.Figure(
        go.Bar(
            y=agg["franchise"],
            x=agg["avg_rating"],
            orientation="h",
            marker=dict(color=colors),
            text=[f"{row.avg_rating:.1f} ({int(row.titles):,})" for row in agg.itertuples()],
            textposition="outside",
            textfont=dict(size=10, color="#c9d1d9"),
            hovertemplate=(
                "<b>%{y}</b><br>Avg IMDb: %{x:.2f}<br>"
                "Rated titles: %{customdata:,}<extra></extra>"
            ),
            customdata=agg["titles"],
        )
    )
    fig.add_vline(
        x=catalog_avg,
        line_width=2,
        line_dash="dash",
        line_color="#FFE066",
    )
    fig.add_annotation(
        x=catalog_avg,
        y=1.02,
        yref="paper",
        text=f"Catalog average · {catalog_avg:.1f}",
        showarrow=False,
        font=dict(size=12, color="#FFE066"),
        xanchor="center",
    )
    fig.update_xaxes(title="Average IMDb rating", range=[0, 10.5], dtick=1)
    fig.update_yaxes(title="", automargin=True, tickfont=dict(size=10))
    fig.update_layout(showlegend=False)
    fig = apply_plotly_theme(
        fig,
        f"Average IMDb rating — top {bar_count} franchises by catalog size",
        height=height,
    )
    fig.update_layout(margin=dict(l=8, r=64, t=80, b=48))
    return fig, agg
