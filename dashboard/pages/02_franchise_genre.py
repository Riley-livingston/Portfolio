import plotly.express as px
import streamlit as st

from dashboard.queries import franchise_stats, genre_stats

st.header("Franchise & Genre Deep Dive")

try:
    franchises = franchise_stats()
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Titles by Franchise")
        fig = px.bar(
            franchises,
            x="franchise",
            y="titles",
            color="franchise",
            text="titles",
        )
        fig.update_layout(showlegend=False, height=400, xaxis_title="", yaxis_title="Titles")
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Avg Runtime by Franchise (min)")
        runtime_df = franchises[franchises["avg_runtime_minutes"].notna()]
        fig2 = px.bar(
            runtime_df,
            x="franchise",
            y="avg_runtime_minutes",
            color="franchise",
        )
        fig2.update_layout(showlegend=False, height=400, xaxis_title="", yaxis_title="Minutes")
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Original vs Licensed by Franchise")
    melt_df = franchises.melt(
        id_vars=["franchise"],
        value_vars=["originals", "licensed"],
        var_name="type",
        value_name="count",
    )
    fig3 = px.bar(melt_df, x="franchise", y="count", color="type", barmode="stack")
    fig3.update_layout(height=400, xaxis_title="", yaxis_title="Titles")
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Franchise Detail Table")
    st.dataframe(franchises, use_container_width=True, hide_index=True)
except Exception as exc:
    st.error(f"Could not load franchise data: {exc}")
