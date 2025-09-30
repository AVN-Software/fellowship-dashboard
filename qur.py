# app.py
# =============================================================================
# CLASSROOM OBSERVATION REPORT 2025 — Streamlit Reader
# Fetches ONLY existing materialized views and renders them.
# Each MV has a 1:1 renderer: render_<materialized_view_name>()
# =============================================================================
# Secrets (create .streamlit/secrets.toml):
# [postgres]
# host = "db.<your-supabase-host>.supabase.co"
# port = 5432
# dbname = "postgres"
# user = "postgres"
# password = "<YOUR_PASSWORD>"
# sslmode = "require"
# =============================================================================

import streamlit as st
import pandas as pd
import psycopg2
from psycopg2.extras import RealDictCursor

from utils.supabase.database_manager import DatabaseManager

st.set_page_config(page_title="Classroom Observation Report 2025", layout="wide")

# -----------------------------
# DB connection helper
# -----------------------------
@st.cache_resource(show_spinner=False)
def get_conn():
    cfg = st.secrets["postgres"]
    conn = psycopg2.connect(
        host=cfg["host"],
        port=cfg.get("port", 5432),
        dbname=cfg["dbname"],
        user=cfg["user"],
        password=cfg["password"],
        sslmode=cfg.get("sslmode", "require"),
        cursor_factory=RealDictCursor,
    )
    return conn

def fetch_df(view_name: str, order_by: str | None = None) -> pd.DataFrame:
    sql = f'SELECT * FROM {view_name}'
    if order_by:
        sql += f' ORDER BY {order_by}'
    with get_conn().cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    return pd.DataFrame(rows)

# -----------------------------
# Utility display helpers
# -----------------------------
def box_df(df: pd.DataFrame, caption: str | None = None):
    st.dataframe(df, use_container_width=True, hide_index=True)
    if caption:
        st.caption(caption)

def safe_pct(x):
    try:
        return f"{float(x):.1f}%"
    except Exception:
        return x

# =============================================================================
# RENDERERS (keep exact names per MV, prefixed with render_)
# =============================================================================

# ---- SECTION 1 --------------------------------------------------------------
def render_mv_s1_2_longitudinal_fellow_tracking():
    df = fetch_df("mv_s1_2_longitudinal_fellow_tracking", order_by="terms_observed DESC")
    col_map = {
        "terms_observed": "Terms Observed",
        "fellow_count": "Fellows",
        "percentage": "% of Fellows",
        "avg_obs_per_fellow": "Avg Obs/Fellow",
        "analysis_capability": "Analysis Capability",
    }
    df_disp = df.rename(columns=col_map)
    if "% of Fellows" in df_disp:
        df_disp["% of Fellows"] = df_disp["% of Fellows"].map(safe_pct)
    st.subheader("1.2 Longitudinal Fellow Tracking")
    box_df(df_disp)

def render_mv_s1_3_coverage_by_fellowship_year():
    df = fetch_df("mv_s1_3_coverage_by_fellowship_year", order_by="term, fellowship_year")
    st.subheader("1.3 Coverage by Fellowship Year")
    box_df(df)

def render_mv_s1_4_coverage_by_coach():
    df = fetch_df("mv_s1_4_coverage_by_coach", order_by="coach_name, term")
    st.subheader("1.4 Coverage by Coach")
    box_df(df)

# ---- SECTION 2 --------------------------------------------------------------
def render_mv_s2_1_program_wide_domain_evolution():
    df = fetch_df("mv_s2_1_program_wide_domain_evolution", order_by="domain, term")
    st.subheader("2.1 Program-Wide Domain Evolution (All Terms)")
    box_df(df)

def render_mv_s2_2_domains_showing_strongest_improvement():
    df = fetch_df("mv_s2_2_domains_showing_strongest_improvement", order_by="tier3_improvement DESC")
    st.subheader("2.2 Domains Showing Strongest Improvement (T1→T3)")
    box_df(df)

def render_mv_s2_3_domains_stuck_at_tier1():
    df = fetch_df("mv_s2_3_domains_stuck_at_tier1", order_by="domain, term")
    st.subheader("2.3 Domains Stuck at Tier 1 (>60% across all terms)")
    box_df(df)

def render_mv_s2_4_overall_program_improvement_summary():
    df = fetch_df("mv_s2_4_overall_program_improvement_summary", order_by="term")
    st.subheader("2.4 Overall Program Improvement Summary")
    box_df(df)

# ---- SECTION 3 --------------------------------------------------------------
def render_mv_s3_1_year1_vs_year2_gap_evolution():
    df = fetch_df("mv_s3_1_year1_vs_year2_gap_evolution", order_by="domain, term")
    st.subheader("3.1 Year 1 vs Year 2 Gap Evolution")
    box_df(df)

def render_mv_s3_2_year1_fellow_development_trajectory():
    df = fetch_df("mv_s3_2_year1_fellow_development_trajectory", order_by="domain, term")
    st.subheader("3.2 Year 1 Fellow Development Trajectory")
    box_df(df)

def render_mv_s3_3_experience_gap_change_over_time():
    df = fetch_df("mv_s3_3_experience_gap_change_over_time", order_by="gap_change DESC")
    st.subheader("3.3 Experience Gap Change Over Time")
    box_df(df)

# ---- SECTION 4 --------------------------------------------------------------
def render_mv_s4_1_overall_phase_performance_trajectory():
    df = fetch_df("mv_s4_1_overall_phase_performance_trajectory", order_by="phase, term")
    st.subheader("4.1 Overall Phase Performance Trajectory")
    box_df(df)

def render_mv_s4_2_domain_performance_by_phase():
    df = fetch_df("mv_s4_2_domain_performance_by_phase", order_by="phase, domain, term")
    st.subheader("4.2 Domain Performance by Phase (Full Breakdown)")
    box_df(df)

def render_mv_s4_3_phase_performance_summary_term3_only():
    df = fetch_df("mv_s4_3_phase_performance_summary_term3_only", order_by="phase, pct_tier3 DESC")
    st.subheader("4.3 Phase Performance Summary (Term 3 only)")
    box_df(df)

# ---- SECTION 5 --------------------------------------------------------------
def render_mv_s5_1_subject_category_performance():
    df = fetch_df("mv_s5_1_subject_category_performance", order_by="subject_category, term")
    st.subheader("5.1 Subject Category Performance")
    box_df(df)

def render_mv_s5_2_mathematics_classes_all_domain_performance():
    df = fetch_df("mv_s5_2_mathematics_classes_all_domain_performance", order_by="domain, term")
    st.subheader("5.2 Mathematics Classes — All Domains")
    box_df(df)

def render_mv_s5_3_language_classes_all_domain_performance():
    df = fetch_df("mv_s5_3_language_classes_all_domain_performance", order_by="domain, term")
    st.subheader("5.3 Language Classes — All Domains")
    box_df(df)

def render_mv_s5_4_literacy_vs_numeracy_in_math_classes():
    df = fetch_df("mv_s5_4_literacy_vs_numeracy_in_math_classes", order_by="domain, term")
    st.subheader("5.4 Literacy vs Numeracy in Math Classes")
    box_df(df)

def render_mv_s5_5_specific_language_subject_performance_literacy():
    df = fetch_df("mv_s5_5_specific_language_subject_performance_literacy", order_by="subject, term")
    st.subheader("5.5 Specific Language Subjects (Literacy domain)")
    box_df(df)

# ---- SECTION 6 --------------------------------------------------------------
def render_mv_s6_1_critical_phase_subject_combinations():
    df = fetch_df("mv_s6_1_critical_phase_subject_combinations", order_by="improvement ASC")
    st.subheader("6.1 Critical Phase × Subject Combinations")
    box_df(df)

# ---- SECTION 7 --------------------------------------------------------------
def render_mv_s7_1_high_growth_fellows():
    df = fetch_df("mv_s7_1_high_growth_fellows", order_by="growth DESC")
    st.subheader("7.1 High-Growth Fellows")
    box_df(df)

def render_mv_s7_2_stagnant_declining_fellows():
    df = fetch_df("mv_s7_2_stagnant_declining_fellows", order_by="change ASC")
    st.subheader("7.2 Stagnant/Declining Fellows")
    box_df(df)

def render_mv_s7_3_fellow_domain_specific_patterns_high_growth():
    df = fetch_df("mv_s7_3_fellow_domain_specific_patterns_high_growth", order_by="fellow_name, domain")
    st.subheader("7.3 Fellow Domain-Specific Patterns (High-Growth)")
    box_df(df)

# ---- SECTION 8 --------------------------------------------------------------
def render_mv_s8_1_class_size_impact_on_performance():
    df = fetch_df("mv_s8_1_class_size_impact_on_performance", order_by="class_size_category, term")
    st.subheader("8.1 Class Size Impact on Performance")
    box_df(df)

def render_mv_s8_2_coach_portfolio_performance():
    df = fetch_df("mv_s8_2_coach_portfolio_performance", order_by="coach_name, term")
    st.subheader("8.2 Coach Portfolio Performance")
    box_df(df)

# =============================================================================
# DIRECTORY (exact MV names)
# =============================================================================
DIRECTORY = [
    ("Section 1.2 — Longitudinal Fellow Tracking", "mv_s1_2_longitudinal_fellow_tracking", render_mv_s1_2_longitudinal_fellow_tracking),
    ("Section 1.3 — Coverage by Fellowship Year", "mv_s1_3_coverage_by_fellowship_year", render_mv_s1_3_coverage_by_fellowship_year),
    ("Section 1.4 — Coverage by Coach", "mv_s1_4_coverage_by_coach", render_mv_s1_4_coverage_by_coach),
    ("Section 2.1 — Program-Wide Domain Evolution (All Terms)", "mv_s2_1_program_wide_domain_evolution", render_mv_s2_1_program_wide_domain_evolution),
    ("Section 2.2 — Domains Showing Strongest Improvement (T1→T3)", "mv_s2_2_domains_showing_strongest_improvement", render_mv_s2_2_domains_showing_strongest_improvement),
    ("Section 2.3 — Domains Stuck at Tier 1 (>60% across all terms)", "mv_s2_3_domains_stuck_at_tier1", render_mv_s2_3_domains_stuck_at_tier1),
    ("Section 2.4 — Overall Program Improvement Summary", "mv_s2_4_overall_program_improvement_summary", render_mv_s2_4_overall_program_improvement_summary),
    ("Section 3.1 — Year 1 vs Year 2 Gap Evolution", "mv_s3_1_year1_vs_year2_gap_evolution", render_mv_s3_1_year1_vs_year2_gap_evolution),
    ("Section 3.2 — Year 1 Fellow Development Trajectory", "mv_s3_2_year1_fellow_development_trajectory", render_mv_s3_2_year1_fellow_development_trajectory),
    ("Section 3.3 — Experience Gap Change Over Time", "mv_s3_3_experience_gap_change_over_time", render_mv_s3_3_experience_gap_change_over_time),
    ("Section 4.1 — Overall Phase Performance Trajectory", "mv_s4_1_overall_phase_performance_trajectory", render_mv_s4_1_overall_phase_performance_trajectory),
    ("Section 4.2 — Domain Performance by Phase (Full Breakdown)", "mv_s4_2_domain_performance_by_phase", render_mv_s4_2_domain_performance_by_phase),
    ("Section 4.3 — Phase Performance Summary (Term 3 only)", "mv_s4_3_phase_performance_summary_term3_only", render_mv_s4_3_phase_performance_summary_term3_only),
    ("Section 5.1 — Subject Category Performance", "mv_s5_1_subject_category_performance", render_mv_s5_1_subject_category_performance),
    ("Section 5.2 — Mathematics Classes — All Domains", "mv_s5_2_mathematics_classes_all_domain_performance", render_mv_s5_2_mathematics_classes_all_domain_performance),
    ("Section 5.3 — Language Classes — All Domains", "mv_s5_3_language_classes_all_domain_performance", render_mv_s5_3_language_classes_all_domain_performance),
    ("Section 5.4 — Literacy vs Numeracy in Math Classes", "mv_s5_4_literacy_vs_numeracy_in_math_classes", render_mv_s5_4_literacy_vs_numeracy_in_math_classes),
    ("Section 5.5 — Specific Language Subjects (Literacy domain)", "mv_s5_5_specific_language_subject_performance_literacy", render_mv_s5_5_specific_language_subject_performance_literacy),
    ("Section 6.1 — Critical Phase × Subject Combinations", "mv_s6_1_critical_phase_subject_combinations", render_mv_s6_1_critical_phase_subject_combinations),
    ("Section 7.1 — High-Growth Fellows", "mv_s7_1_high_growth_fellows", render_mv_s7_1_high_growth_fellows),
    ("Section 7.2 — Stagnant/Declining Fellows", "mv_s7_2_stagnant_declining_fellows", render_mv_s7_2_stagnant_declining_fellows),
    ("Section 7.3 — Fellow Domain-Specific Patterns (High-Growth)", "mv_s7_3_fellow_domain_specific_patterns_high_growth", render_mv_s7_3_fellow_domain_specific_patterns_high_growth),
    ("Section 8.1 — Class Size Impact on Performance", "mv_s8_1_class_size_impact_on_performance", render_mv_s8_1_class_size_impact_on_performance),
    ("Section 8.2 — Coach Portfolio Performance", "mv_s8_2_coach_portfolio_performance", render_mv_s8_2_coach_portfolio_performance),
]

# =============================================================================
# UI
# =============================================================================
st.title("CLASSROOM OBSERVATION REPORT 2025")
st.markdown("## Teaching Quality Development: HITS Performance Across Terms 1–3")
st.divider()

with st.expander("Executive Summary (static shell — wire to your narrative as desired)", expanded=True):
    st.write("""
- Use **Section 2.4** for overall averages and Tier mix per term.
- Use **Section 2.2** for top-improving domains.
- Use **Section 2.3** for persistent Tier 1 gaps.
- Use **Section 3.1 / 3.3** to describe experience effects over time.
    """)

st.sidebar.header("Page 1: Directory of Queries")
choice = st.sidebar.radio(
    "Select a section/view",
    options=[f"{label}  →  {name}" for (label, name, _) in DIRECTORY],
    index=0,
)


# Find and run the selected renderer
selected_name = choice.split("→")[-1].strip()
for label, name, renderer in DIRECTORY:
    if name == selected_name:
        st.caption(f"**View:** `{name}`")
        try:
            renderer()
        except Exception as e:
            st.error(f"Failed to render `{name}`: {e}")
        break

# Optional: show all views on one page
st.sidebar.write("---")
if st.sidebar.checkbox("Render ALL views (long page)"):
    for label, name, renderer in DIRECTORY:
        st.markdown("---")
        st.caption(f"**View:** `{name}`  ·  {label}")
        try:
            renderer()
        except Exception as e:
            st.error(f"Failed to render `{name}`: {e}")




# =========================
# Data Fetch – Materialized Views
# =========================
@st.cache_data
def load_mvs() -> Dict[str, pd.DataFrame]:
    """
    Load all materialized views (MVs) defined in DatabaseManager.
    Returns dict keyed by mv name → DataFrame.
    """
    db = DatabaseManager()
    return {
        # SECTION 1
        "mv_s1_2_longitudinal_fellow_tracking": db.mv_s1_2_longitudinal_fellow_tracking(),
        "mv_s1_3_coverage_by_fellowship_year": db.mv_s1_3_coverage_by_fellowship_year(),
        "mv_s1_4_coverage_by_coach": db.mv_s1_4_coverage_by_coach(),

        # SECTION 2
        "mv_s2_1_program_wide_domain_evolution": db.mv_s2_1_program_wide_domain_evolution(),
        "mv_s2_2_domains_showing_strongest_improvement": db.mv_s2_2_domains_showing_strongest_improvement(),
        "mv_s2_3_domains_stuck_at_tier1": db.mv_s2_3_domains_stuck_at_tier1(),
        "mv_s2_4_overall_program_improvement_summary": db.mv_s2_4_overall_program_improvement_summary(),

        # SECTION 3
        "mv_s3_1_year1_vs_year2_gap_evolution": db.mv_s3_1_year1_vs_year2_gap_evolution(),
        "mv_s3_2_year1_fellow_development_trajectory": db.mv_s3_2_year1_fellow_development_trajectory(),
        "mv_s3_3_experience_gap_change_over_time": db.mv_s3_3_experience_gap_change_over_time(),

        # SECTION 4
        "mv_s4_1_overall_phase_performance_trajectory": db.mv_s4_1_overall_phase_performance_trajectory(),
        "mv_s4_2_domain_performance_by_phase": db.mv_s4_2_domain_performance_by_phase(),
        "mv_s4_3_phase_performance_summary_term3_only": db.mv_s4_3_phase_performance_summary_term3_only(),

        # SECTION 5
        "mv_s5_1_subject_category_performance": db.mv_s5_1_subject_category_performance(),
        "mv_s5_2_mathematics_classes_all_domain_performance": db.mv_s5_2_mathematics_classes_all_domain_performance(),
        "mv_s5_3_language_classes_all_domain_performance": db.mv_s5_3_language_classes_all_domain_performance(),
        "mv_s5_4_literacy_vs_numeracy_in_math_classes": db.mv_s5_4_literacy_vs_numeracy_in_math_classes(),
        "mv_s5_5_specific_language_subject_performance_literacy": db.mv_s5_5_specific_language_subject_performance_literacy(),

        # SECTION 6
        "mv_s6_1_critical_phase_subject_combinations": db.mv_s6_1_critical_phase_subject_combinations(),

        # SECTION 7
        "mv_s7_1_high_growth_fellows": db.mv_s7_1_high_growth_fellows(),
        "mv_s7_2_stagnant_declining_fellows": db.mv_s7_2_stagnant_declining_fellows(),
        "mv_s7_3_fellow_domain_specific_patterns_high_growth": db.mv_s7_3_fellow_domain_specific_patterns_high_growth(),

        # SECTION 8
        "mv_s8_1_class_size_impact_on_performance": db.mv_s8_1_class_size_impact_on_performance(),
        "mv_s8_2_coach_portfolio_performance": db.mv_s8_2_coach_portfolio_performance(),


    }
