# enhanced_tier_analysis/sections/strategic_section.py
import streamlit as st
import pandas as pd

from ..charts import strategic


def render_strategic_section(df: pd.DataFrame, segment_col: str, domain_colors: dict):
    """
    Render the Strategic Analysis section.
      1) Strategic positioning chart
      2) Tier strength analysis
      3) Pattern analysis
      4) Strategic recommendations
    """
    st.header("Strategic Analysis")

    # --- Chart 1: Strategic Positioning ---
    st.subheader("Strategic Positioning")
    strategic.create_strategic_positioning_chart(df, segment_col, domain_colors)

    # --- Chart 2: Tier Strength Analysis ---
    st.subheader("Tier Strength Analysis")
    strategic.create_tier_strength_analysis(df, segment_col, domain_colors)

    # --- Chart 3: Pattern Analysis ---
    st.subheader("Pattern Analysis")
    strategic.create_pattern_analysis(df, segment_col, domain_colors)

    # --- Recommendations ---
    st.subheader("Strategic Recommendations")
    strategic.create_strategic_recommendations(df, segment_col, domain_colors)
