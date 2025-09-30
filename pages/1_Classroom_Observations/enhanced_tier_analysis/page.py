import streamlit as st
import pandas as pd
from typing import Optional, Dict, Any

from .config import tier_colors, domain_colors


class EnhancedTierProgressionPage:
    """Main entry point for the Enhanced Tier Progression dashboard."""

    def __init__(self):
        self.tier_colors = tier_colors
        self.domain_colors = domain_colors

    def render(
        self,
        df: Optional[pd.DataFrame],
        raw_df: Optional[pd.DataFrame] = None,
        config: Dict[str, Any] = None,
    ):
        # --- Page Styling ---
        st.markdown(
            """
            <style>
                .report-container {
                    max-width: 1100px;
                    margin: 0 auto; /* center */
                    padding: 2rem;
                    background-color: white;
                    border-radius: 12px;
                }
                .report-container h1, 
                .report-container h2, 
                .report-container h3 {
                    text-align: center;
                }
            </style>
            """,
            unsafe_allow_html=True,
        )

        st.markdown('<div class="report-container">', unsafe_allow_html=True)

        # --- Title ---
        st.title("Advanced Tier Progression Analysis")

        if df is None or df.empty:
            st.error("No materialized view data available.")
            st.markdown("</div>", unsafe_allow_html=True)
            return

        # ---------------------------
        # Section 1: Tier Mix Evolution
        # ---------------------------
        from .sections import tier_mix_section
        st.markdown("---")
        st.header("Tier Mix Evolution")
        st.markdown(
            """
            This section examines **how fellows are distributed across Tier 1, Tier 2, and Tier 3** over time.  
            It provides insight into the balance of performance levels and highlights shifts in learning outcomes.  
            """
        )
        tier_mix_section.render_tier_mix_section(df, None, self.domain_colors)

        st.markdown(
            """
            Having understood the tier distributions, the next step is to explore 
            **how performance trends evolve across terms and domains**.
            """
        )

        # ---------------------------
        # Section 2: Performance Trends
        # ---------------------------
        from .sections import performance_section
        st.markdown("---")
        st.header("Performance Trends")
        st.markdown(
            """
            This section tracks **performance trajectories across domains and terms**, 
            revealing areas of improvement, stagnation, or decline.  
            It helps identify where interventions are most effective or most needed.  
            """
        )
        performance_section.render_performance_section(df, None, self.domain_colors)

        st.markdown(
            """
            While performance trends show directional movement, a deeper layer of insight comes from examining 
            **strategic strengths and weaknesses** across the tier framework.
            """
        )

        # ---------------------------
        # Section 3: Strategic Analysis
        # ---------------------------
        from .sections import strategic_section
        st.markdown("---")
        st.header("Strategic Analysis")
        st.markdown(
            """
            This section provides a **strategic view of system performance**, 
            focusing on dominant strengths, emerging weaknesses, and actionable opportunities.  
            It highlights domains requiring targeted interventions versus those that can serve as models of best practice.  
            """
        )
        strategic_section.render_strategic_section(df, None, self.domain_colors)

        st.markdown(
            """
            To complete the analysis, we compare **performance variations across key segments** 
            (e.g., Primary vs High School, Year 1 vs Year 2 fellows), identifying disparities and gaps.
            """
        )

        # ---------------------------
        # Section 4: Comparative Analysis
        # ---------------------------
        from .sections import comparative_section
        st.markdown("---")
        st.header("Comparative Analysis")
        st.markdown(
            """
            This section compares **tier performance across different segments**, 
            enabling equity-focused insights.  
            It highlights where certain groups outperform others, and where targeted support is most urgent.  
            """
        )
        comparative_section.render_comparative_section(df, None, self.domain_colors)

        # --- Closing summary ---
        st.markdown("---")
        st.markdown(
            """
            ### Closing Summary  
            By combining tier distributions, performance trajectories, strategic positioning, 
            and comparative insights, this report delivers a **comprehensive view of fellow progression**.  
            The findings can inform both **day-to-day coaching decisions** and **long-term strategic planning**.  
            """
        )

        st.markdown("</div>", unsafe_allow_html=True)
