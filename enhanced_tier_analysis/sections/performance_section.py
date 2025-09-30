import streamlit as st
import pandas as pd

from ..charts import performance


def render_performance_section(df: pd.DataFrame, segment_col: str, domain_colors: dict):
    """
    Render the Performance Trends section:
      1) Domain Performance Chart
      2) Tier Performance Chart
      3) Performance Heatmap
      4) Recovery Analysis
    """

    st.header("Performance Trends")

    if df is None or df.empty:
        st.warning("No data available for Performance Trends analysis.")
        return

    # --- Chart 1: Domain Performance ---
    st.subheader("Domain Performance Evolution")
    performance.create_domain_performance_chart(df, segment_col, domain_colors)

    # --- Chart 2: Tier Performance ---
    st.subheader("Tier Performance Trends")
    performance.create_tier_performance_chart(df, segment_col, domain_colors)

    # --- Chart 3: Performance Heatmap ---
    st.subheader("Performance Heatmap")
    performance.create_performance_heatmap(df, segment_col, domain_colors)

    # --- Chart 4: Recovery Analysis ---
    st.subheader("Recovery Analysis")
    performance.create_recovery_analysis(df, segment_col, domain_colors)

    # Optional: add narratives if you want
    _narrate_performance_trends(df)


def _narrate_performance_trends(df: pd.DataFrame):
    """Provide a narrative summary of the performance trends section."""
    if df is None or df.empty:
        return

    st.markdown("### Key Insights")
    st.markdown(
        """
        - **Domain Evolution**: Track how each domain’s average scores change across terms.  
        - **Tier Trends**: Compare progression across Tiers 1–3 to identify areas of improvement.  
        - **Heatmap**: Quickly spot domains and terms with strong or weak performance.  
        - **Recovery**: Detect subjects or groups that rebound after performance dips.  

        These insights help identify **patterns of growth**, highlight **priority areas for support**, 
        and showcase **domains that maintain consistent excellence**.
        """
    )
