import plotly.express as px
import streamlit as st

from dashboard.queries import catalog_summary, genre_stats, rating_stats

st.header("Library Overview")

try:
    summary = catalog_summary().iloc[0]
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Movies vs Series")
        fig = px.pie(
            names=["Movies", "Series"],
            values=[summary["movie_count"], summary["series_count"]],
            hole=0.4,
        )
        fig.update_layout(showlegend=True, height=350)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Content Ratings")
        ratings = rating_stats()
        fig2 = px.bar(ratings, x="content_rating", y="title_count", color="content_rating")
        fig2.update_layout(showlegend=False, height=350, xaxis_title="Rating", yaxis_title="Titles")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top Genres")
    genres = genre_stats()
    fig3 = px.bar(genres, x="title_count", y="genre", orientation="h", color="title_count")
    fig3.update_layout(showlegend=False, height=400, yaxis={"categoryorder": "total ascending"})
    st.plotly_chart(fig3, use_container_width=True)
except Exception as exc:
    st.error(f"Could not load overview data: {exc}")
