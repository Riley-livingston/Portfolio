"""Disney+ Catalog Analytics Dashboard."""

import streamlit as st

st.set_page_config(
    page_title="Disney+ Catalog Analytics",
    page_icon="✨",
    layout="wide",
)

pages = [
    st.Page(
        "pages/01_exploratory_data_analysis.py",
        title="Exploratory Data Analysis",
        icon="🔬",
        default=True,
    ),
    st.Page(
        "pages/02_catalog_insights.py",
        title="Catalog Insights",
        icon="📊",
    ),
]

st.navigation(pages).run()
