# app.py
# =============================================================================
# CLASSROOM OBSERVATION REPORT 2025 — Read-only Streamlit
# - Uses ONLY existing materialized views (no CREATE/REFRESH).
# - Exact headings/wording kept as provided.
# - One renderer per MV: render_<materialized_view_name>().
# - Exports the full bottom section (markdown + all tables) as .md and .xlsx
# =============================================================================
# .streamlit/secrets.toml (Supabase)
# [supabase]
# url     = "https://<your-project>.supabase.co"
# anon_key = "<YOUR_ANON_KEY>"
# =============================================================================

from __future__ import annotations
from datetime import datetime
from typing import Dict, Optional
import io

import streamlit as st
import pandas as pd
import numpy as np

from utils.supabase.database_manager import get_db

st.set_page_config(page_title="CLASSROOM OBSERVATION REPORT 2025", layout="wide")


# ---------------------------------------
# Load ALL materialized views (page-local)
# ---------------------------------------
@st.cache_data(show_spinner=False)
def load_mvs() -> Dict[str, pd.DataFrame]:
    db = get_db()
    mv_names = [
        # Section 1
        "mv_s1_2_longitudinal_fellow_tracking",
        "mv_s1_3_coverage_by_fellowship_year",
        "mv_s1_4_coverage_by_coach",
        # Section 2
        "mv_s2_1_program_wide_domain_evolution",
        "mv_s2_2_domains_showing_strongest_improvement",
        "mv_s2_3_domains_stuck_at_tier1",
        "mv_s2_4_overall_program_improvement_summary",
        # Section 3
        "mv_s3_1_year1_vs_year2_gap_evolution",
        "mv_s3_2_year1_fellow_development_trajectory",
        "mv_s3_3_experience_gap_change_over_time",
        # Section 4
        "mv_s4_1_overall_phase_performance_trajectory",
        "mv_s4_2_domain_performance_by_phase",
        "mv_s4_3_phase_performance_summary_term3_only",
        # Section 5
        "mv_s5_1_subject_category_performance",
        "mv_s5_2_mathematics_classes_all_domain_performance",
        "mv_s5_3_language_classes_all_domain_performance",
        "mv_s5_4_literacy_vs_numeracy_in_math_classes",
        "mv_s5_5_specific_language_subject_performance_literacy",
        # Section 6
        "mv_s6_1_critical_phase_subject_combinations",
        # Section 7
        "mv_s7_1_high_growth_fellows",
        "mv_s7_2_stagnant_declining_fellows",
        "mv_s7_3_fellow_domain_specific_patterns_high_growth",
        # Section 8
        "mv_s8_1_class_size_impact_on_performance",
        "mv_s8_2_coach_portfolio_performance",
    ]

    data: Dict[str, pd.DataFrame] = {}
    for name in mv_names:
        try:
            data[name] = get_db()._safe_table(name)  # RLS must allow read
        except Exception as e:
            st.error(f"Error loading {name}: {e}")
            data[name] = pd.DataFrame()
    return data


# Load all materialized views at once (cached)
dfs = load_mvs()


# -----------------------------
# Helpers + Recorder for Export
# -----------------------------
class ReportRecorder:
    """
    Collects all text (Markdown) + tables rendered on the page,
    so we can export the whole bottom section as Markdown + Excel.
    """
    def __init__(self):
        self.md_chunks: list[str] = []
        self.tables: Dict[str, pd.DataFrame] = {}

    # ----- Text -----
    def md(self, text: str):
        """Write markdown to page and capture for export."""
        st.markdown(text)
        self.md_chunks.append(text if text.endswith("\n") else text + "\n")

    def hr(self):
        st.write("---")
        self.md_chunks.append("\n---\n")

    # ----- Tables -----
    def table(self, df: pd.DataFrame, name: Optional[str] = None, caption: Optional[str] = None):
        """Render a df and capture it as well."""
        st.dataframe(df, use_container_width=True, hide_index=True)
        if caption:
            st.caption(caption)

        # Save table for exports
        key = name or f"Table_{len(self.tables)+1}"
        self.tables[key] = df.copy()

        # Also add a light Markdown snapshot (first 50 rows) for the .md export
        try:
            snap = df.head(50)
            self.md_chunks.append(f"\n**{key}**\n\n")
            self.md_chunks.append(snap.to_markdown(index=False) + "\n\n")
            if caption:
                self.md_chunks.append(f"*{caption}*\n\n")
        except Exception:
            # to_markdown may fail if wide dtypes; skip silently
            pass

    # ----- Exporters -----
    def export_markdown(self) -> str:
        return "".join(self.md_chunks)

    def export_excel(self) -> bytes:
        buf = io.BytesIO()
        with pd.ExcelWriter(buf, engine="xlsxwriter") as writer:
            for name, df in self.tables.items():
                sheet = name[:31] if name else "Sheet1"
                try:
                    df.to_excel(writer, sheet_name=sheet, index=False)
                except Exception:
                    # fallback to plain cast
                    df.astype(str).to_excel(writer, sheet_name=sheet, index=False)
        buf.seek(0)
        return buf.getvalue()


rec = ReportRecorder()


def _order_dataframe(df: pd.DataFrame, order_by: str | None) -> pd.DataFrame:
    """
    Lightweight ORDER BY parser supporting: "col1, col2 DESC, col3 ASC"
    """
    if df is None or df.empty or not order_by:
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()

    parts = [p.strip() for p in order_by.split(",")]
    cols: list[str] = []
    asc: list[bool] = []
    for p in parts:
        tokens = p.split()
        col = tokens[0]
        direction = tokens[1].upper() if len(tokens) > 1 else "ASC"
        if col in df.columns:
            cols.append(col)
            asc.append(direction != "DESC")
    if not cols:
        return df
    try:
        return df.sort_values(cols, ascending=asc)
    except Exception:
        return df


def get_mv(name: str, order_by: str | None = None) -> pd.DataFrame:
    df = dfs.get(name, pd.DataFrame())
    return _order_dataframe(df, order_by)


def pct_fmt(x):
    try:
        return f"{float(x):.1f}%"
    except Exception:
        return x


# =============================================================================
# EXACT-NAME RENDERERS (1:1 with your MVs)
# =============================================================================
def render_mv_s1_2_longitudinal_fellow_tracking():
    df = get_mv("mv_s1_2_longitudinal_fellow_tracking", order_by="terms_observed DESC")
    rec.table(df, name="mv_s1_2_longitudinal_fellow_tracking")

def render_mv_s1_3_coverage_by_fellowship_year():
    df = get_mv("mv_s1_3_coverage_by_fellowship_year", order_by="term, fellowship_year")
    rec.table(df, name="mv_s1_3_coverage_by_fellowship_year")

def render_mv_s1_4_coverage_by_coach():
    df = get_mv("mv_s1_4_coverage_by_coach", order_by="coach_name, term")
    rec.table(df, name="mv_s1_4_coverage_by_coach")

def render_mv_s2_1_program_wide_domain_evolution():
    df = get_mv("mv_s2_1_program_wide_domain_evolution", order_by="domain, term")
    rec.table(df, name="mv_s2_1_program_wide_domain_evolution")

def render_mv_s2_2_domains_showing_strongest_improvement():
    df = get_mv("mv_s2_2_domains_showing_strongest_improvement", order_by="tier3_improvement DESC")
    rec.table(df, name="mv_s2_2_domains_showing_strongest_improvement")

def render_mv_s2_3_domains_stuck_at_tier1():
    df = get_mv("mv_s2_3_domains_stuck_at_tier1", order_by="domain, term")
    rec.table(df, name="mv_s2_3_domains_stuck_at_tier1")

def render_mv_s2_4_overall_program_improvement_summary():
    df = get_mv("mv_s2_4_overall_program_improvement_summary", order_by="term")
    rec.table(df, name="mv_s2_4_overall_program_improvement_summary")

def render_mv_s3_1_year1_vs_year2_gap_evolution():
    df = get_mv("mv_s3_1_year1_vs_year2_gap_evolution", order_by="domain, term")
    rec.table(df, name="mv_s3_1_year1_vs_year2_gap_evolution")

def render_mv_s3_2_year1_fellow_development_trajectory():
    df = get_mv("mv_s3_2_year1_fellow_development_trajectory", order_by="domain, term")
    rec.table(df, name="mv_s3_2_year1_fellow_development_trajectory")

def render_mv_s3_3_experience_gap_change_over_time():
    df = get_mv("mv_s3_3_experience_gap_change_over_time", order_by="gap_change DESC")
    rec.table(df, name="mv_s3_3_experience_gap_change_over_time")

def render_mv_s4_1_overall_phase_performance_trajectory():
    df = get_mv("mv_s4_1_overall_phase_performance_trajectory", order_by="phase, term")
    rec.table(df, name="mv_s4_1_overall_phase_performance_trajectory")

def render_mv_s4_2_domain_performance_by_phase():
    df = get_mv("mv_s4_2_domain_performance_by_phase", order_by="phase, domain, term")
    rec.table(df, name="mv_s4_2_domain_performance_by_phase")

def render_mv_s4_3_phase_performance_summary_term3_only():
    df = get_mv("mv_s4_3_phase_performance_summary_term3_only", order_by="phase, pct_tier3 DESC")
    rec.table(df, name="mv_s4_3_phase_performance_summary_term3_only")

def render_mv_s5_1_subject_category_performance():
    df = get_mv("mv_s5_1_subject_category_performance", order_by="subject_category, term")
    rec.table(df, name="mv_s5_1_subject_category_performance")

def render_mv_s5_2_mathematics_classes_all_domain_performance():
    df = get_mv("mv_s5_2_mathematics_classes_all_domain_performance", order_by="domain, term")
    rec.table(df, name="mv_s5_2_mathematics_classes_all_domain_performance")

def render_mv_s5_3_language_classes_all_domain_performance():
    df = get_mv("mv_s5_3_language_classes_all_domain_performance", order_by="domain, term")
    rec.table(df, name="mv_s5_3_language_classes_all_domain_performance")

def render_mv_s5_4_literacy_vs_numeracy_in_math_classes():
    df = get_mv("mv_s5_4_literacy_vs_numeracy_in_math_classes", order_by="domain, term")
    rec.table(df, name="mv_s5_4_literacy_vs_numeracy_in_math_classes")

def render_mv_s5_5_specific_language_subject_performance_literacy():
    df = get_mv("mv_s5_5_specific_language_subject_performance_literacy", order_by="subject, term")
    rec.table(df, name="mv_s5_5_specific_language_subject_performance_literacy")

def render_mv_s6_1_critical_phase_subject_combinations():
    df = get_mv("mv_s6_1_critical_phase_subject_combinations", order_by="improvement ASC")
    rec.table(df, name="mv_s6_1_critical_phase_subject_combinations")

def render_mv_s7_1_high_growth_fellows():
    df = get_mv("mv_s7_1_high_growth_fellows", order_by="growth DESC")
    rec.table(df, name="mv_s7_1_high_growth_fellows")

def render_mv_s7_2_stagnant_declining_fellows():
    df = get_mv("mv_s7_2_stagnant_declining_fellows", order_by="change ASC")
    rec.table(df, name="mv_s7_2_stagnant_declining_fellows")

def render_mv_s7_3_fellow_domain_specific_patterns_high_growth():
    df = get_mv("mv_s7_3_fellow_domain_specific_patterns_high_growth", order_by="fellow_name, domain")
    rec.table(df, name="mv_s7_3_fellow_domain_specific_patterns_high_growth")

def render_mv_s8_1_class_size_impact_on_performance():
    df = get_mv("mv_s8_1_class_size_impact_on_performance", order_by="class_size_category, term")
    rec.table(df, name="mv_s8_1_class_size_impact_on_performance")

def render_mv_s8_2_coach_portfolio_performance():
    df = get_mv("mv_s8_2_coach_portfolio_performance", order_by="coach_name, term")
    rec.table(df, name="mv_s8_2_coach_portfolio_performance")


# =============================================================================
# PAGE BODY — EXACT WORDING/PLACEMENT + TABLES FROM MVs
# (All text + tables go through ReportRecorder -> exportable)
# =============================================================================

rec.md("# CLASSROOM OBSERVATION REPORT 2025")
rec.md("## Teaching Quality Development: HITS Performance Across Terms 1-3")
rec.hr()

rec.md("## EXECUTIVE SUMMARY")
rec.md("""
**What HITS Measures:**
High-Impact Teaching Strategies (HITS) assess teaching quality across 5 domains, each scored on a 3-tier developmental continuum:
- **Tier 1 (Foundational)**: Essential baseline practices
- **Tier 2 (Developing)**: Adaptive, sophisticated strategies  
- **Tier 3 (Advanced)**: Mastery, differentiation, responsive teaching
""")

# ---- Executive Summary table (fill from mv_s2_4 and static counts) ----------
exec_df = pd.DataFrame({
    "Metric": ["Observations", "Fellows Observed", "Average Domain Score", "% Tier 3 (Advanced)"],
    "Term 1": ["50", "47", "", ""],
    "Term 2": ["90", "89", "", ""],
    "Term 3": ["130", "118", "", ""],
    "Change": ["+160%", "+151%", "", ""],
})
try:
    prog = get_mv("mv_s2_4_overall_program_improvement_summary", order_by="term")
    for t in ["Term 1", "Term 2", "Term 3"]:
        row = prog.loc[prog["term"] == t]
        if not row.empty:
            exec_df.loc[exec_df["Metric"]=="Average Domain Score", t] = f'{float(row["overall_avg_score"].iloc[0]):.2f}'
            exec_df.loc[exec_df["Metric"]=="% Tier 3 (Advanced)", t] = f'{float(row["overall_pct_tier3"].iloc[0]):.1f}%'
    def delta(a, b):
        try: return f'{(float(b)-float(a)):+.2f}'
        except: return ""
    def delta_pct(a, b):
        try: return f'{(float(b)-float(a)):+.1f}%'
        except: return ""
    exec_df.loc[exec_df["Metric"]=="Average Domain Score","Change"] = delta(exec_df["Term 1"][2] or np.nan, exec_df["Term 3"][2] or np.nan)
    exec_df.loc[exec_df["Metric"]=="% Tier 3 (Advanced)","Change"] = delta_pct((exec_df["Term 1"][3] or "0").rstrip("%"), (exec_df["Term 3"][3] or "0").rstrip("%"))
except Exception as e:
    st.caption(f"Note: Could not derive averages from mv_s2_4_overall_program_improvement_summary ({e}).")

rec.md("**The Year in Numbers:**")
rec.table(exec_df, name="Executive_Summary_The_Year_in_Numbers")

rec.md("""
**Key Findings:**
[Populated from Query 2.2 - Top improving domains]  
[Populated from Query 2.3 - Persistent gaps]  
[Populated from Query 3.1 - Experience effect patterns]
""")

rec.hr()
rec.md("## 1. OBSERVATION COVERAGE & QUALITY")

rec.md("### 1.1 Observation Activity Across Terms")
obs_shell = pd.DataFrame({
    "Term": ["Term 1","Term 2","Term 3","Program Total"],
    "Observations": ["50","90","130","270"],
    "Fellows": ["47","89","118","[Unique]"],
    "Coaches": ["5","6","6","6"],
    "Avg Class Size": ["46","38","39","40 avg"],
    "Avg Attendance": ["95.9%","95.2%","94.1%","95.1% avg"]
})
rec.table(obs_shell, name="Observation_Activity_Shell")

rec.md("""
**Data Collection Improved:**
- 160% increase in observations from T1 to T3
- Coverage expanded from 52% to full cohort by T2
- T3 exceeds cohort size, indicating multiple observations per fellow in final term

**Teaching Conditions:**
- Class size normalized from 46 to 38-39 learners (better data or context shift)
- Consistent 94-96% attendance indicates normal teaching conditions observed
""")

rec.md("### 1.2 Longitudinal Fellow Tracking")
rec.md("**[Populate from Query 1.2]**")
render_mv_s1_2_longitudinal_fellow_tracking()

rec.md("### 1.3 Coverage by Fellowship Year")
rec.md("**[Populate from Query 1.3]**")
render_mv_s1_3_coverage_by_fellowship_year()

rec.hr()
rec.md("## 2. DOMAIN PERFORMANCE TRAJECTORIES")

rec.md("### 2.1 Program-Wide Evolution")
rec.md("**[Populate from Query 2.1 - Create multi-line chart showing Tier 3 % for all 6 domains across 3 terms]**")
render_mv_s2_1_program_wide_domain_evolution()

rec.md("### 2.2 Domains Showing Strongest Improvement")
rec.md("**[Populate from Query 2.2]**")
render_mv_s2_2_domains_showing_strongest_improvement()

rec.md("### 2.3 Persistent Gaps")
rec.md("**[Populate from Query 2.3 - Domains >60% Tier 1]**")
render_mv_s2_3_domains_stuck_at_tier1()

rec.md("### 2.4 Overall Program Quality Score")
rec.md("**[Populate from Query 2.4]**")
render_mv_s2_4_overall_program_improvement_summary()

rec.hr()
rec.md("## 3. EXPERIENCE EFFECT ANALYSIS")

rec.md("### 3.1 Year 1 vs Year 2 Gap Evolution")
rec.md("**[Populate from Query 3.1 - Create grouped bar chart for each domain showing Y1 vs Y2 across terms]**")
render_mv_s3_1_year1_vs_year2_gap_evolution()

rec.md("### 3.2 Year 1 Fellow Development Trajectory")
rec.md("**[Populate from Query 3.2]**")
render_mv_s3_2_year1_fellow_development_trajectory()

rec.md("### 3.3 Experience Gap Trends")
rec.md("**[Populate from Query 3.3]**")
render_mv_s3_3_experience_gap_change_over_time()

rec.hr()
rec.md("## 4. PHASE-SPECIFIC PERFORMANCE")

rec.md("### 4.1 Overall Phase Trajectories")
rec.md("**[Populate from Query 4.1]**")
render_mv_s4_1_overall_phase_performance_trajectory()

rec.md("### 4.2 Domain Performance by Phase")
rec.md("**[Populate from Query 4.2 - Create heatmap showing each phase × domain × term]**")
render_mv_s4_2_domain_performance_by_phase()

rec.md("### 4.3 Phase Performance Summary (Term 3 Snapshot)")
rec.md("**[Populate from Query 4.3]**")
render_mv_s4_3_phase_performance_summary_term3_only()

rec.hr()
rec.md("## 5. SUBJECT-SPECIFIC PERFORMANCE")

rec.md("### 5.1 Subject Category Trajectories")
rec.md("**[Populate from Query 5.1]**")
render_mv_s5_1_subject_category_performance()

rec.md("### 5.2 Mathematics Classes - Full Domain Profile")
rec.md("**[Populate from Query 5.2]**")
render_mv_s5_2_mathematics_classes_all_domain_performance()

rec.md("### 5.3 Language Classes - Full Domain Profile")
rec.md("**[Populate from Query 5.3]**")
render_mv_s5_3_language_classes_all_domain_performance()

rec.md("### 5.4 Literacy vs Numeracy in Math Classes")
rec.md("**[Populate from Query 5.4]**")
render_mv_s5_4_literacy_vs_numeracy_in_math_classes()

rec.md("### 5.5 Language-Specific Literacy Performance")
rec.md("**[Populate from Query 5.5]**")
render_mv_s5_5_specific_language_subject_performance_literacy()

rec.hr()
rec.md("## 6. PHASE × SUBJECT INTERACTIONS")

rec.md("### 6.1 Critical Combinations")
rec.md("**[Populate from Query 6.1]**")
render_mv_s6_1_critical_phase_subject_combinations()

rec.hr()
rec.md("## 7. INDIVIDUAL FELLOW TRAJECTORIES")

rec.md("### 7.1 High-Growth Fellows")
rec.md("**[Populate from Query 7.1]**")
render_mv_s7_1_high_growth_fellows()

rec.md("### 7.2 Stagnant/Declining Fellows")
rec.md("**[Populate from Query 7.2]**")
render_mv_s7_2_stagnant_declining_fellows()

rec.md("### 7.3 Fellow Domain-Specific Patterns (High-Growth)")
rec.md("**[Populate from Query 7.3]**")
render_mv_s7_3_fellow_domain_specific_patterns_high_growth()

rec.hr()
rec.md("## 8. CONTEXTUAL FACTORS")

rec.md("### 8.1 Class Size Impact")
rec.md("**[Populate from Query 8.1]**")
render_mv_s8_1_class_size_impact_on_performance()

rec.md("### 8.2 Coach Portfolio Performance")
rec.md("**[Populate from Query 8.2]**")
render_mv_s8_2_coach_portfolio_performance()

rec.hr()
rec.md("## 9. KEY FINDINGS")
rec.md("""
### 9.1 What Improved
[Based on Query 2.2 results]

### 9.2 What Stagnated
[Based on Query 2.3 results]

### 9.3 Experience Effect Summary
[Based on Query 3.3 results]

### 9.4 Phase-Specific Patterns
[Based on Query 4.3 results]

### 9.5 Subject-Specific Patterns
[Based on Query 5.1 results]
""")

rec.hr()
rec.md("## 10. RECOMMENDATIONS")
rec.md("""
### 10.1 Based on Domain Trajectories
**What Worked (Scale It):**
- [Interventions that showed improvement]

**What Didn't Work (Redesign It):**
- [Persistent gaps requiring new approach]

### 10.2 Phase-Specific Interventions
[Based on phase patterns]

### 10.3 Subject-Specific Support
[Based on subject patterns]

### 10.4 Fellow-Specific Actions
- High-growth fellows: Leverage as peer coaches
- Stagnant fellows: Intensive intervention plan
""")

rec.hr()
rec.md("## 11. CONCLUSION")
rec.md("""
**The 3-Term Story:**
[Synthesize what longitudinal data shows about teaching quality development]

**Evidence-Based Next Steps:**
[What Year 2 should focus on based on actual patterns observed]

---

**Report Length:** 15-20 pages with visuals  
**Data Source:** PostgreSQL queries executed against observations and domain_scores tables  
**Analysis Period:** Terms 1-3, 2025  
**Total Observations:** 270 across 118 unique fellows
""")



# =============================================================================
# EXPORT / COPY — single-click downloads (Markdown + Excel)
# =============================================================================
st.write("")
st.write("")
st.subheader("⬇️ Export / Copy")
md_bytes = rec.export_markdown().encode("utf-8")
st.download_button(
    "Download Full Report (Markdown)",
    data=md_bytes,
    file_name=f"classroom_observation_report_{datetime.now().date()}.md",
    mime="text/markdown",
    use_container_width=True,
)

xlsx_bytes = rec.export_excel()
st.download_button(
    "Download All Tables (Excel)",
    data=xlsx_bytes,
    file_name=f"classroom_observation_report_tables_{datetime.now().date()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True,
)

# Option 3 (updated): Export to Excel by Section, not per MV
excel_buffer = io.BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    # Define sections with their MV names
    sections = {
        "Section 1 - Coverage & Quality": [
            "mv_s1_2_longitudinal_fellow_tracking",
            "mv_s1_3_coverage_by_fellowship_year",
            "mv_s1_4_coverage_by_coach",
        ],
        "Section 2 - Domain Performance": [
            "mv_s2_1_program_wide_domain_evolution",
            "mv_s2_2_domains_showing_strongest_improvement",
            "mv_s2_3_domains_stuck_at_tier1",
            "mv_s2_4_overall_program_improvement_summary",
        ],
        "Section 3 - Experience Effects": [
            "mv_s3_1_year1_vs_year2_gap_evolution",
            "mv_s3_2_year1_fellow_development_trajectory",
            "mv_s3_3_experience_gap_change_over_time",
        ],
        "Section 4 - Phase Performance": [
            "mv_s4_1_overall_phase_performance_trajectory",
            "mv_s4_2_domain_performance_by_phase",
            "mv_s4_3_phase_performance_summary_term3_only",
        ],
        "Section 5 - Subject Performance": [
            "mv_s5_1_subject_category_performance",
            "mv_s5_2_mathematics_classes_all_domain_performance",
            "mv_s5_3_language_classes_all_domain_performance",
            "mv_s5_4_literacy_vs_numeracy_in_math_classes",
            "mv_s5_5_specific_language_subject_performance_literacy",
        ],
        "Section 6 - Phase x Subject": [
            "mv_s6_1_critical_phase_subject_combinations",
        ],
        "Section 7 - Fellow Trajectories": [
            "mv_s7_1_high_growth_fellows",
            "mv_s7_2_stagnant_declining_fellows",
            "mv_s7_3_fellow_domain_specific_patterns_high_growth",
        ],
        "Section 8 - Contextual Factors": [
            "mv_s8_1_class_size_impact_on_performance",
            "mv_s8_2_coach_portfolio_performance",
        ],
    }

    # Loop over sections
    for sheet_name, mv_list in sections.items():
        # Create a sheet per section
        startrow = 0
        for mv in mv_list:
            df = dfs.get(mv, pd.DataFrame())
            if df is not None and not df.empty:
                # Write section heading
                df.to_excel(
                    writer,
                    sheet_name=sheet_name[:31],  # Excel limit 31 chars
                    startrow=startrow,
                    index=False,
                )
                # Leave space before next table
                startrow += len(df) + 3

st.download_button(
    "⬇️ Download Sectioned Report (Excel)",
    data=excel_buffer.getvalue(),
    file_name=f"classroom_observation_report_sections_{datetime.now().date()}.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
