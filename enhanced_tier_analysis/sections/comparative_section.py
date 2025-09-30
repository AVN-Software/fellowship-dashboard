# enhanced_tier_analysis/sections/comparative_section.py
import streamlit as st
import pandas as pd

from ..charts import comparative
from ..analysis import trends


def render_comparative_section(df: pd.DataFrame, segment_col: str, domain_colors: dict):
    """
    Render the Comparative Analysis section.
      1) Segment comparison chart
      2) Progression rate analysis
      3) Trend analysis (narrative + charts)
    """
    st.header("Comparative Analysis")

    if not segment_col or segment_col == "both":
        st.info("Please select a specific segment (School Level or Fellowship Year) to compare.")
        return

    # --- Chart 1: Segment Comparison ---
    st.subheader("Segment Comparison")
    comparative.create_segment_comparison_chart(df, segment_col, domain_colors)

    # --- Chart 2: Progression Rate Analysis ---
    st.subheader("Progression Rate Analysis")
    comparative.create_progression_rate_analysis(df, segment_col, domain_colors)

    # --- Narrative/Trends ---
    st.subheader("Trend Analysis")
    trends.analyze_trends(df, segment_col)
