"""Exploratory Data Analysis — catalog composition overview."""

import streamlit as st

from dashboard.eda import fig_family_ratings, fig_franchise_depth, fig_original_vs_licensed
from dashboard.queries import catalog_summary, franchise_stats, rating_stats
from dashboard.theme import inject_styles, metric_row

inject_styles()

st.title("Exploratory Data Analysis")
st.markdown(
    '<p class="eda-caption">Catalog composition for Disney+ US — franchise and IP depth, exclusive vs licensed mix, '
    "and audience ratings. See <b>Catalog Insights</b> for treemap, heatmap, and quality views.</p>",
    unsafe_allow_html=True,
)

try:
    summary = catalog_summary().iloc[0]
    total = int(summary["total_titles"])
    originals = int(summary["original_count"])

    metric_row(
        [
            ("Catalog titles", total, None),
            ("Disney+ originals", originals, None),
            ("Movies", int(summary["movie_count"]), None),
            ("Series", int(summary["series_count"]), None),
            ("IP groups", int(summary["franchise_count"]), None),
        ]
    )

    franchises = franchise_stats()
    other_row = franchises[franchises["franchise"] == "Other"]
    other_count = int(other_row["titles"].iloc[0]) if not other_row.empty else 0
    other_pct = f"{100 * other_count / max(total, 1):.1f}% ungrouped"

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_franchise_depth(franchises), use_container_width=True)
        leader = franchises.iloc[0]
        st.markdown(
            f'<div class="eda-insight"><b>Takeaway:</b> <b>{leader["franchise"]}</b> is the largest group '
            f"({int(leader['titles']):,} titles). {other_pct}.</div>",
            unsafe_allow_html=True,
        )

    with col2:
        st.plotly_chart(fig_original_vs_licensed(franchises), use_container_width=True)
        total_orig = int(franchises["originals"].sum())
        total_lic = int(franchises["licensed"].sum())
        st.markdown(
            f'<div class="eda-insight"><b>Takeaway:</b> {total_lic:,} licensed titles vs {total_orig:,} estimated '
            f"originals — exclusives are a strategic slice of a mostly library-driven catalog.</div>",
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.plotly_chart(fig_family_ratings(rating_stats()), use_container_width=True)
    ratings = rating_stats()
    top_rating = ratings.iloc[0]
    st.markdown(
        f'<div class="eda-insight"><b>Takeaway:</b> <b>{top_rating["content_rating"]}</b> is the most common rating '
        f"({int(top_rating['title_count']):,} titles), reflecting Disney+'s family-oriented positioning.</div>",
        unsafe_allow_html=True,
    )

except Exception as exc:
    st.warning(f"Connect Postgres and run `make load && make views`. ({exc})")
