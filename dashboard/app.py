"""Disney+ Catalog Analytics Dashboard."""

import streamlit as st

st.set_page_config(
    page_title="Disney+ Catalog Analytics",
    page_icon="✨",
    layout="wide",
)

st.title("Disney+ Catalog Analytics")
st.markdown(
    """
    Production catalog pipeline: **scrape → validate → PostgreSQL → insights**.

    Use the sidebar to explore library composition, franchise depth, and catalog growth.
    """
)

try:
    from dashboard.queries import catalog_summary

    summary = catalog_summary()
    if not summary.empty:
        row = summary.iloc[0]
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("Total Titles", int(row["total_titles"]))
        c2.metric("Movies", int(row["movie_count"]))
        c3.metric("Series", int(row["series_count"]))
        c4.metric("Franchises", int(row["franchise_count"]))
        c5.metric("Disney+ Originals", int(row["original_count"]))
except Exception as exc:
    st.warning(f"Connect Postgres and run `make load && make views`. ({exc})")
