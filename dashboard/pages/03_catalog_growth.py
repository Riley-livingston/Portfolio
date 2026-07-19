import plotly.express as px
import streamlit as st

from dashboard.queries import catalog_growth, freshness_data, release_decade

st.header("Catalog Growth & Freshness")

try:
    growth = catalog_growth()
    decades = release_decade()
    freshness = freshness_data()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Titles Added Over Time")
        if not growth.empty:
            fig = px.line(growth, x="month_added", y="titles_added", markers=True)
            fig.update_layout(height=350, xaxis_title="Month", yaxis_title="Titles Added")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No date_added values available.")

    with col2:
        st.subheader("Release Decade Distribution")
        fig2 = px.bar(decades, x="release_decade", y="title_count", text="title_count")
        fig2.update_layout(height=350, xaxis_title="Decade", yaxis_title="Titles")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Freshness: Release Year vs Catalog Add Date")
    if not freshness.empty and freshness["months_release_to_catalog"].notna().any():
        fig3 = px.scatter(
            freshness,
            x="release_year",
            y="date_added",
            color="franchise",
            hover_data=["title"],
            size_max=12,
        )
        fig3.update_layout(height=450, xaxis_title="Release Year", yaxis_title="Date Added to Disney+")
        st.plotly_chart(fig3, use_container_width=True)
    else:
        st.info("Insufficient date_added data for freshness scatter.")

    st.subheader("Recently Added Titles")
    st.dataframe(freshness.head(20), use_container_width=True, hide_index=True)
except Exception as exc:
    st.error(f"Could not load growth data: {exc}")
