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

# enhanced_tier_analysis/sections/tier_mix_section.py
import re
import numpy as np
import pandas as pd
import streamlit as st

from ..charts import tier_mix_charts
from ..tables import tier_mix_tables


# =========================
# Public entry point
# =========================
def render_tier_mix_section(df: pd.DataFrame, segment_col: str, domain_colors: dict):
    """
    Professional Tier Mix Evolution section with:
      1) Intro KPI cards
      2) Tier Distribution chart
      3) Tier Mix Analysis table + narrative
      4) Dominant Index chart
      5) Movement Analysis table + narrative
    (Stacked vertically for clarity.)
    """
    _inject_css()

    # Title
    st.markdown("<h2 class='ttn-section-title'>🎯 Tier Mix Evolution</h2>", unsafe_allow_html=True)

    # Intro + KPIs
    _provide_section_introduction(df, segment_col)

    # ---- Chart 1: Tier Distribution ----
    st.markdown("<h3 class='ttn-subtitle'>📊 Tier Distribution Over Time</h3>", unsafe_allow_html=True)
    tier_mix_charts.create_tier_distribution_chart(df, segment_col, domain_colors)

    # ---- Table 1: Tier Mix Analysis ----
    st.markdown("<h3 class='ttn-subtitle'>📋 Detailed Tier Mix Analysis</h3>", unsafe_allow_html=True)
    tier_mix_tables.create_tier_mix_table(df, segment_col)
    _narrate_tier_mix_comprehensive(df, segment_col)  # narrative beneath the table

    # ---- Chart 2: Dominant Index ----
    st.markdown("<h3 class='ttn-subtitle'>📈 Dominant Index Progression</h3>", unsafe_allow_html=True)
    tier_mix_charts.create_dominant_index_chart(df, segment_col, domain_colors)

    # ---- Table 2: Movement Analysis ----
    st.markdown("<h3 class='ttn-subtitle'>🔄 Term-to-Term Movement Analysis</h3>", unsafe_allow_html=True)
    tier_mix_tables.create_movement_analysis(df, segment_col)
    _narrate_movements_comprehensive(df, segment_col)  # narrative beneath the table


# =========================
# Style (minimalist)
# =========================
def _inject_css():
    st.markdown(
        """
        <style>
            .ttn-section-title{
                margin: 0.25rem 0 1rem 0;
                color: #1F2A37;
                font-weight: 700;
                letter-spacing: 0.2px;
            }
            .ttn-subtitle{
                margin: 1.25rem 0 0.5rem 0;
                color: #111827;
                font-weight: 600;
            }
            .ttn-card{
                padding: 12px 16px;
                border-radius: 10px;
                border: 1px solid #E5E7EB;
                background: #FFFFFF;
                box-shadow: 0 1px 2px rgba(0,0,0,0.03);
                margin-bottom: 8px;
            }
            .ttn-kpi .metric-container { gap: 10px; }
            .ttn-insight{
                padding: 12px 16px;
                border-left: 5px solid #94A3B8;
                background: #F8FAFC;
                border-radius: 6px;
                margin: 6px 0;
            }
            .ttn-insight.success{ border-left-color:#10B981; background:#ECFDF5; }
            .ttn-insight.danger{  border-left-color:#EF4444; background:#FEF2F2; }
            .ttn-insight.info{    border-left-color:#0EA5E9; background:#EFF6FF; }
            .ttn-insight.warning{ border-left-color:#F59E0B; background:#FFFBEB; }
        </style>
        """,
        unsafe_allow_html=True
    )


# =========================
# Intro & KPIs
# =========================
def _provide_section_introduction(df: pd.DataFrame, segment_col: str):
    if df is None or df.empty:
        st.warning("No data available for tier mix analysis.")
        return

    total_obs = len(df)
    terms = sorted(df['term'].dropna().unique().tolist())
    latest_term = terms[-1] if terms else "—"
    latest_df = df[df['term'] == latest_term] if terms else df

    avg_t3 = float(latest_df['tier_mix_t3_pct'].mean()) if not latest_df.empty else 0.0
    avg_index = float(latest_df['dominant_index'].mean()) if not latest_df.empty else 0.0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Latest Term", latest_term)
    with c2:
        st.metric("Avg Tier 3 %", f"{avg_t3:.1f}%")
    with c3:
        st.metric("Balance Index", f"{avg_index:.2f}")

    st.caption(
        f"Dataset: {total_obs:,} observations across {len(terms)} term(s). "
        "This section focuses on distribution across tiers and progression patterns."
    )


# =========================
# Insight utilities
# =========================
def _insight_card(title: str, body: str, variant: str = "info"):
    klass = f"ttn-insight {variant}"
    st.markdown(
        f"<div class='{klass}'><strong>{title}</strong><br><span>{body}</span></div>",
        unsafe_allow_html=True
    )


# =========================
# Narratives — Tier Mix
# =========================
def _narrate_tier_mix_comprehensive(df: pd.DataFrame, segment_col: str):
    if df is None or df.empty or "term" not in df.columns or "domain" not in df.columns:
        return

    terms = _sorted_terms(df["term"])
    if not terms:
        return

    latest_term = terms[-1]
    latest_df = df[df["term"] == latest_term]
    if latest_df.empty:
        return

    # System
    avg_t3 = latest_df["tier_mix_t3_pct"].mean()
    # Top/bottom
    g = latest_df.groupby("domain")["tier_mix_t3_pct"].mean()
    if g.empty:
        return
    top_domain = g.idxmax()
    bottom_domain = g.idxmin()

    _insight_card("🏆 Best Domain", f"{top_domain} leads on Tier 3 share.", "success")
    _insight_card("⚠️ Needs Attention", f"{bottom_domain} lags and may need targeted support.", "danger")
    _insight_card("📊 System Average", f"Overall Tier 3 is {avg_t3:.1f}% in {latest_term}.", "info")

    # Optional: segment comparison
    if segment_col and segment_col != "both" and segment_col in df.columns:
        _analyze_segment_differences(df, segment_col, terms)
    _analyze_progression_patterns(df, terms)
    _provide_strategic_recommendations(df, terms, segment_col)


# =========================
# Narratives — Movement
# =========================
def _narrate_movements_comprehensive(df: pd.DataFrame, segment_col: str):
    if df is None or df.empty or "term" not in df.columns or "domain" not in df.columns:
        return

    terms = _sorted_terms(df["term"])
    if len(terms) < 2:
        return

    last_term, prev_term = terms[-1], terms[-2]
    prev_g = df[df["term"] == prev_term].groupby("domain")["tier_mix_t3_pct"].mean()
    last_g = df[df["term"] == last_term].groupby("domain")["tier_mix_t3_pct"].mean()
    changes = (last_g - prev_g).dropna()

    improving = changes[changes > 5]
    declining = changes[changes < -5]

    if not improving.empty:
        _insight_card("📈 Strong Improvement", f"{improving.idxmax()} improved by {improving.max():.1f} pts.", "success")
    if not declining.empty:
        _insight_card("📉 Significant Decline", f"{declining.idxmin()} declined by {abs(declining.min()):.1f} pts.", "danger")
    if improving.empty and declining.empty:
        _insight_card("ℹ️ Stable", "No large movements between the last two terms.", "info")


# =========================
# Analytical helpers
# =========================
def _analyze_segment_differences(df: pd.DataFrame, segment_col: str, terms: list):
    latest_term = terms[-1]
    latest_df = df[df["term"] == latest_term]
    if latest_df.empty or segment_col not in latest_df.columns:
        return

    seg = (
        latest_df.groupby([segment_col, "domain"])["tier_mix_t3_pct"]
        .mean()
        .unstack(level=0)
        .fillna(0)
    )
    if seg.empty or seg.shape[1] < 2:
        return

    with st.expander(f"⚖️ {segment_col.replace('_', ' ').title()} Comparison", expanded=False):
        seg_avgs = seg.mean(axis=0).to_dict()
        best_segment = max(seg_avgs, key=seg_avgs.get)
        st.write(f"**Overall Leader:** {best_segment} ({seg_avgs[best_segment]:.1f}% Tier 3 avg)")

        st.write("**Domain-Specific Gaps (>|10| pts):**")
        for domain in seg.index:
            row = seg.loc[domain]
            gap = row.max() - row.min()
            if gap > 10:
                st.write(f"- **{domain}**: {row.idxmax()} leads by {gap:.1f} pts ({row.max():.1f}% vs {row.min():.1f}%).")


def _analyze_progression_patterns(df: pd.DataFrame, terms: list):
    if len(terms) < 2:
        return

    with st.expander("📈 Progression Patterns", expanded=False):
        first = df[df["term"] == terms[0]].groupby("domain")["tier_mix_t3_pct"].mean()
        last = df[df["term"] == terms[-1]].groupby("domain")["tier_mix_t3_pct"].mean()
        diffs = (last - first).dropna()

        improving = diffs[diffs > 5].sort_values(ascending=False)
        declining = diffs[diffs < -5].sort_values()
        stable = diffs[(diffs >= -5) & (diffs <= 5)].sort_index()

        c1, c2, c3 = st.columns(3)
        with c1:
            st.write("**📈 Improving**")
            for k, v in improving.items():
                st.write(f"• {k}: +{v:.1f}%")
        with c2:
            st.write("**➡️ Stable**")
            for k, v in stable.items():
                st.write(f"• {k}: {v:+.1f}%")
        with c3:
            st.write("**📉 Declining**")
            for k, v in declining.items():
                st.write(f"• {k}: {v:.1f}%")

        if len(terms) >= 3:
            _identify_patterns(df, terms)


def _identify_patterns(df: pd.DataFrame, terms: list):
    st.write("**📊 Pattern Analysis**")
    for domain in sorted(df["domain"].unique()):
        vals = []
        for t in terms[:3]:  # first 3 terms for simple pattern read
            v = df[(df["term"] == t) & (df["domain"] == domain)]["tier_mix_t3_pct"].mean()
            vals.append(v if not np.isnan(v) else None)
        if any(v is None for v in vals) or len(vals) < 3:
            continue

        t1, t2, t3 = vals
        if t2 < t1 and t3 > t2 and t3 >= t1:
            st.write(f"• **{domain}**: U-Shape Recovery ({t1:.1f}% → {t2:.1f}% → {t3:.1f}%)")
        elif t3 > t2 > t1:
            st.write(f"• **{domain}**: Consistent Growth ({t1:.1f}% → {t2:.1f}% → {t3:.1f}%)")
        elif t1 > t2 > t3:
            st.write(f"• **{domain}**: Steady Decline ({t1:.1f}% → {t2:.1f}% → {t3:.1f}%)")
        elif abs(t3 - t1) < 3 and abs(t2 - t1) > 8:
            st.write(f"• **{domain}**: Volatile ({t1:.1f}% → {t2:.1f}% → {t3:.1f}%)")


def _provide_strategic_recommendations(df: pd.DataFrame, terms: list, segment_col: str):
    latest_term = terms[-1]
    latest_df = df[df["term"] == latest_term]
    if latest_df.empty:
        return

    domain_summary = (
        latest_df.groupby("domain")
        .agg(t1=("tier_mix_t1_pct", "mean"),
             t3=("tier_mix_t3_pct", "mean"),
             idx=("dominant_index", "mean"))
    )

    with st.expander("💡 Strategic Recommendations", expanded=False):
        recs = []

        # Best/worst by Tier 3
        top = domain_summary["t3"].idxmax()
        bot = domain_summary["t3"].idxmin()
        recs.append(f"**Replicate Success**: Study {top} (Tier 3 {domain_summary.loc[top, 't3']:.1f}%) and scale practices.")
        recs.append(f"**Targeted Support**: {bot} needs intensive coaching (Tier 3 {domain_summary.loc[bot, 't3']:.1f}%).")

        # High Tier 1 share
        high_t1 = domain_summary[domain_summary["t1"] > 40].index.tolist()
        if high_t1:
            recs.append(f"**Foundational Focus**: {', '.join(high_t1)} require baseline skill reinforcement (high Tier 1 share).")

        # Low index
        low_idx = domain_summary[domain_summary["idx"] < 2.0].index.tolist()
        if low_idx:
            recs.append(f"**Progression Acceleration**: {', '.join(low_idx)} need strategies to move learners up tiers (index < 2.0).")

        # Segment gap
        if segment_col and segment_col in df.columns:
            _add_segment_recommendations(df, segment_col, latest_term, recs)

        for i, r in enumerate(recs, 1):
            st.write(f"{i}. {r}")


def _add_segment_recommendations(df: pd.DataFrame, segment_col: str, latest_term: str, recs: list):
    latest_df = df[df["term"] == latest_term]
    seg_perf = latest_df.groupby(segment_col)["tier_mix_t3_pct"].mean().sort_values(ascending=False)
    if len(seg_perf) >= 2:
        gap = seg_perf.iloc[0] - seg_perf.iloc[-1]
        if gap > 10:
            recs.append(f"**Segment Gap**: Address the {gap:.1f} pt Tier-3 gap between {seg_perf.index[0]} and {seg_perf.index[-1]}.")


# =========================
# Utilities
# =========================
def _sorted_terms(series: pd.Series) -> list:
    vals = series.dropna().astype(str).unique().tolist()
    def key_fn(x: str):
        m = re.search(r"\d+", x)
        return int(m.group()) if m else 0
    return sorted(vals, key=key_fn)
