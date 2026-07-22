"""Catalog Insights — treemap, heatmap, decades, and quality views."""

import streamlit as st

from dashboard.insights import (
    fig_catalog_treemap,
    fig_franchise_genre_heatmap,
    fig_franchise_imdb_quality,
    fig_release_decades,
)
from dashboard.queries import (
    franchise_genre_matrix,
    franchise_stats,
    imdb_ratings_scatter,
    release_decade,
)
from dashboard.theme import inject_styles

inject_styles()

st.title("Catalog Insights")
st.markdown(
    '<p class="eda-caption">Four views of catalog strategy: composition, genre positioning, '
    "release-era depth, and which franchises earn the highest average IMDb scores.</p>",
    unsafe_allow_html=True,
)

try:
    franchises = franchise_stats()
    matrix = franchise_genre_matrix()
    decades = release_decade()
    ratings = imdb_ratings_scatter()

    st.plotly_chart(fig_catalog_treemap(franchises), use_container_width=True)
    top = franchises.iloc[0]
    st.markdown(
        f'<div class="eda-insight"><b>Takeaway:</b> <b>{top["franchise"]}</b> is the single largest block '
        f"({int(top['titles']):,} titles). The treemap shows how concentrated the US catalog is by IP pillar.</div>",
        unsafe_allow_html=True,
    )

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_franchise_genre_heatmap(matrix), use_container_width=True)
        if not matrix.empty:
            peak = matrix.sort_values("title_count", ascending=False).iloc[0]
            st.markdown(
                f'<div class="eda-insight"><b>Takeaway:</b> Strongest overlap is '
                f"<b>{peak['franchise']}</b> × <b>{peak['genre']}</b> "
                f"({int(peak['title_count']):,} titles).</div>",
                unsafe_allow_html=True,
            )

    with col2:
        st.plotly_chart(fig_release_decades(decades), use_container_width=True)
        if not decades.empty:
            peak_decade = decades.sort_values("title_count", ascending=False).iloc[0]
            label = f"{int(peak_decade['release_decade'])}s"
            st.markdown(
                f'<div class="eda-insight"><b>Takeaway:</b> Most titles originally released in the '
                f"<b>{label}</b> ({int(peak_decade['title_count']):,}) — deep vault, not just new drops.</div>",
                unsafe_allow_html=True,
            )

    st.markdown("---")
    quality_fig, quality_agg = fig_franchise_imdb_quality(ratings)
    st.plotly_chart(quality_fig, use_container_width=True)
    if not quality_agg.empty:
        catalog_avg = float(ratings["imdb_rating"].mean())
        best = quality_agg.sort_values("avg_rating", ascending=False).iloc[0]
        above_avg = int((quality_agg["avg_rating"] >= catalog_avg).sum())
        st.markdown(
            f'<div class="eda-insight"><b>Takeaway:</b> Catalog average is <b>{catalog_avg:.1f}</b> / 10 across '
            f"<b>{len(quality_agg)}</b> largest franchise groups by volume. "
            f"<b>{best['franchise']}</b> scores highest at <b>{best['avg_rating']:.1f}</b> "
            f"({int(best['titles']):,} titles). {above_avg} groups beat the average (green bars). "
            f"Hover any bar for exact scores.</div>",
            unsafe_allow_html=True,
        )

except Exception as exc:
    st.warning(f"Connect Postgres and run `make load && make views`. ({exc})")
