"""
Academic Results — Report View (sections, not tabs)
Adds export of tables (CSV) and charts (PNG/HTML fallback)
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from pathlib import Path
import io, zipfile, sys

# -------------------------
# Path & Imports
# -------------------------
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from utils.supabase.database_manager import get_db
from pages.Academic_Results.tabs import (
    overview, subjects, fellowship_years, education_phases, data_explorer
)
from pages.Academic_Results.utils import prepare_data, apply_filters

# -------------------------
# Page Config & CSS
# -------------------------
st.set_page_config(page_title="Academic Results — Report", page_icon="📊", layout="wide")

st.markdown("""
    <style>
    .filter-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem; border-radius: 12px; margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .filter-header { color: white; font-size: 1.3rem; font-weight: 600; margin-bottom: 1rem; }
    div[data-baseweb="select"] > div { background-color: white; border-radius: 8px; }
    .stButton button {
        background-color: rgba(255,255,255,0.2); color: white; border: 2px solid white;
        border-radius: 8px; font-weight: 500; transition: all 0.3s ease;
    }
    .stButton button:hover { background-color: white; color: #667eea; transform: translateY(-2px); }
    .main-header { font-size: 2.5rem; font-weight: 700; color: #1f77b4; margin-bottom: .5rem; }
    .sub-header { font-size: 1.1rem; color: #666; margin-bottom: 2rem; }
    hr { margin: 2rem 0; border: none; border-top: 2px solid #e0e0e0; }
    </style>
""", unsafe_allow_html=True)

# -------------------------
# Data Loading
# -------------------------
@st.cache_data(ttl=300)
def load_academic_data():
    try:
        db = get_db()
        df = db.get_academic_results()
        if df is not None and len(df) > 0:
            return df
        st.warning("No data found in report_academic_results.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# -------------------------
# Export Recorder
# -------------------------
class ExportRecorder:
    """Collects markdown text, dataframes, and plotly figs to export."""
    def __init__(self):
        self.md_chunks: list[str] = []
        self.tables: dict[str, pd.DataFrame] = {}
        self.figs: dict[str, "plotly.graph_objs.Figure"] = {}

    # Markdown
    def md(self, text: str):
        st.markdown(text)
        self.md_chunks.append(text if text.endswith("\n") else text + "\n")

    def hr(self):
        st.write("---")
        self.md_chunks.append("\n---\n")

    # Tables
    def add_table(self, name: str, df: pd.DataFrame):
        if isinstance(df, pd.DataFrame) and not df.empty:
            self.tables[name] = df.copy()

    # Figures
    def add_fig(self, name: str, fig):
        if fig is not None:
            self.figs[name] = fig

    # ---- Exporters ----
    def export_markdown(self) -> bytes:
        return "".join(self.md_chunks).encode("utf-8")

    def export_tables_zip(self) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, df in self.tables.items():
                csv_bytes = df.to_csv(index=False).encode("utf-8")
                zf.writestr(f"{_safe(name)}.csv", csv_bytes)
        buf.seek(0)
        return buf.getvalue()

    def export_charts_zip(self) -> bytes:
        """Prefer PNG via kaleido; fallback to HTML if kaleido isn't available."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, fig in self.figs.items():
                wrote = False
                # Try PNG
                try:
                    png_bytes = fig.to_image(format="png", scale=2)  # requires kaleido
                    zf.writestr(f"{_safe(name)}.png", png_bytes)
                    wrote = True
                except Exception:
                    wrote = False
                # Fallback HTML
                if not wrote:
                    html = fig.to_html(include_plotlyjs="cdn", full_html=False).encode("utf-8")
                    zf.writestr(f"{_safe(name)}.html", html)
        buf.seek(0)
        return buf.getvalue()

def _safe(name: str) -> str:
    return name.replace("/", "_").replace("\\", "_").replace(" ", "_")[:60]

rec = ExportRecorder()

# -------------------------
# Header
# -------------------------
st.markdown('<p class="main-header">📊 Academic Results — Report</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Student performance and improvement across the fellowship</p>', unsafe_allow_html=True)

# -------------------------
# Load & Prepare
# -------------------------
df = load_academic_data()
if df.empty:
    st.error("No data available. Please check your database connection.")
    st.stop()

df_clean = prepare_data(df)

# -------------------------
# Filters
# -------------------------
subj_opts = sorted(df_clean['subject'].dropna().unique()) if 'subject' in df_clean else []
phase_opts = sorted(df_clean['phase'].dropna().unique()) if 'phase' in df_clean else []

def grade_key(g):
    try:
        if isinstance(g, (int, float)): return int(g)
        return int(str(g).split()[-1])
    except:
        return 9999
grade_opts = sorted(df_clean['grade'].dropna().unique(), key=grade_key) if 'grade' in df_clean else []

with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown('<div class="filter-header">🎛️ Filters</div>', unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
    with col1:
        flt_subjects = st.multiselect("📚 Subject", options=subj_opts, default=subj_opts, key="acad_subj")
    with col2:
        flt_phases = st.multiselect("🎓 Phase", options=phase_opts, default=phase_opts, key="acad_phase")
    with col3:
        flt_grades = st.multiselect("📊 Grade", options=grade_opts, default=grade_opts, key="acad_grade")
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("♻️ Reset", use_container_width=True, key="acad_reset"):
            for k in list(st.session_state.keys()):
                if k.startswith("acad_"):
                    del st.session_state[k]
            st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

filtered = apply_filters(df_clean, flt_subjects, flt_phases, flt_grades)
if len(filtered) < len(df_clean):
    st.caption(f"📌 Showing {len(filtered):,} of {len(df_clean):,} records after filtering")

st.divider()

# -------------------------
# Table of Contents
# -------------------------
rec.md("## Table of Contents")
rec.md("""
- [1. Executive Summary](#1-executive-summary)
- [2. Subject Performance](#2-subject-performance)
- [3. Fellowship Years](#3-fellowship-years)
- [4. Education Phases](#4-education-phases)
- [5. Data Explorer](#5-data-explorer)
""")
rec.hr()

# =========================================================
# 1) Executive Summary
# =========================================================
rec.md("## 1. Executive Summary")
# KPIs (robust to schema)
k1, k2, k3, k4 = st.columns(4)
with k1: st.metric("Records", len(filtered))
with k2:
    terms = sorted(filtered["term"].dropna().unique()) if "term" in filtered else []
    st.metric("Terms", len(terms))
with k3:
    learners_col = "learner_id" if "learner_id" in filtered else ("student_id" if "student_id" in filtered else None)
    st.metric("Unique Learners", int(filtered[learners_col].nunique()) if learners_col else 0)
with k4:
    score_col = _first_present(filtered, ["score", "mark", "percentage"])
    overall = filtered[score_col].dropna() if score_col else pd.Series(dtype=float)
    st.metric("Overall Avg", f"{overall.mean():.1f}" if not overall.empty else "—")

# Summary by term (if present)
if "term" in filtered and (score_col := _first_present(filtered, ["score", "mark", "percentage"])):
    term_summary = (
        filtered.groupby("term", dropna=True)[score_col]
        .agg(n="count", avg="mean", p75=lambda s: s.quantile(0.75))
        .reset_index()
        .sort_values("term")
    )
    rec.add_table("Executive_Term_Summary", term_summary)
    st.dataframe(term_summary, use_container_width=True, hide_index=True)

    fig_exec = px.line(term_summary, x="term", y="avg", markers=True, title="Average by Term")
    st.plotly_chart(fig_exec, use_container_width=True)
    rec.add_fig("Executive_Avg_by_Term", fig_exec)

rec.hr()

# =========================================================
# 2) Subject Performance
# =========================================================
rec.md("## 2. Subject Performance")
# Subject table and chart (robust)
if "subject" in filtered and (score_col := _first_present(filtered, ["score", "mark", "percentage"])):
    # avg by term & subject
    subj_term = (
        filtered.groupby(["subject", "term"], dropna=True)[score_col]
        .agg(avg="mean", n="count")
        .reset_index()
    ) if "term" in filtered else (
        filtered.groupby(["subject"], dropna=True)[score_col]
        .agg(avg="mean", n="count").reset_index()
    )
    rec.add_table("Subject_by_Term", subj_term)
    st.dataframe(subj_term.sort_values(["subject","term"] if "term" in subj_term else ["subject"]),
                 use_container_width=True, hide_index=True)

    if "term" in subj_term:
        fig_subj = px.bar(
            subj_term, x="avg", y="subject", color="term",
            barmode="group", orientation="h",
            title="Average by Subject × Term",
            labels={"avg":"Average", "subject":"Subject"}
        )
    else:
        fig_subj = px.bar(
            subj_term.sort_values("avg"),
            x="avg", y="subject", orientation="h",
            title="Average by Subject", labels={"avg":"Average","subject":"Subject"}
        )
    st.plotly_chart(fig_subj, use_container_width=True)
    rec.add_fig("Subject_by_Term_Chart", fig_subj)
else:
    st.info("Subject columns not found; skipping this section visuals.")

# Optional: render your existing module (kept, but not required for exports)
try:
    subjects.render(filtered)
except Exception:
    pass

rec.hr()

# =========================================================
# 3) Fellowship Years
# =========================================================
rec.md("## 3. Fellowship Years")
year_col = "fellowship_year" if "fellowship_year" in filtered else None
if year_col and (score_col := _first_present(filtered, ["score", "mark", "percentage"])):
    yr_term = (
        filtered.groupby([year_col, "term"], dropna=True)[score_col]
        .agg(avg="mean", n="count").reset_index()
    ) if "term" in filtered else (
        filtered.groupby([year_col], dropna=True)[score_col]
        .agg(avg="mean", n="count").reset_index()
    )
    yr_term[year_col] = yr_term[year_col].astype(str)
    rec.add_table("FellowshipYear_by_Term", yr_term)
    st.dataframe(yr_term, use_container_width=True, hide_index=True)

    if "term" in yr_term:
        fig_year = px.bar(
            yr_term, x="avg", y=year_col, color="term", barmode="group", orientation="h",
            title="Average by Fellowship Year × Term", labels={"avg":"Average", year_col:"Fellowship Year"}
        )
    else:
        fig_year = px.bar(
            yr_term.sort_values("avg"),
            x="avg", y=year_col, orientation="h",
            title="Average by Fellowship Year", labels={"avg":"Average", year_col:"Fellowship Year"}
        )
    st.plotly_chart(fig_year, use_container_width=True)
    rec.add_fig("FellowshipYear_by_Term_Chart", fig_year)
else:
    st.info("Fellowship year or score column not found.")

# Optional existing module
try:
    fellowship_years.render(filtered)
except Exception:
    pass

rec.hr()

# =========================================================
# 4) Education Phases
# =========================================================
rec.md("## 4. Education Phases")
if "phase" in filtered and (score_col := _first_present(filtered, ["score", "mark", "percentage"])):
    ph_term = (
        filtered.groupby(["phase", "term"], dropna=True)[score_col]
        .agg(avg="mean", n="count").reset_index()
    ) if "term" in filtered else (
        filtered.groupby(["phase"], dropna=True)[score_col]
        .agg(avg="mean", n="count").reset_index()
    )
    rec.add_table("Phase_by_Term", ph_term)
    st.dataframe(ph_term.sort_values(["phase","term"] if "term" in ph_term else ["phase"]),
                 use_container_width=True, hide_index=True)

    if "term" in ph_term:
        fig_phase = px.bar(
            ph_term, x="avg", y="phase", color="term", barmode="group", orientation="h",
            title="Average by Phase × Term", labels={"avg":"Average","phase":"Phase"}
        )
    else:
        fig_phase = px.bar(
            ph_term.sort_values("avg"),
            x="avg", y="phase", orientation="h",
            title="Average by Phase", labels={"avg":"Average","phase":"Phase"}
        )
    st.plotly_chart(fig_phase, use_container_width=True)
    rec.add_fig("Phase_by_Term_Chart", fig_phase)
else:
    st.info("Phase or score column not found.")

# Optional existing module
try:
    education_phases.render(filtered)
except Exception:
    pass

rec.hr()

# =========================================================
# 5) Data Explorer
# =========================================================
rec.md("## 5. Data Explorer")
# Your existing explorer stays (for interactive use). Exports come from the tables we created above.
try:
    data_explorer.render(filtered, df_clean)
except Exception:
    st.dataframe(filtered.head(100), use_container_width=True, hide_index=True)

rec.hr()

# =========================================================
# Exports
# =========================================================
st.subheader("⬇️ Export")
colA, colB, colC = st.columns([1,1,1])
with colA:
    st.download_button(
        "Download Report (Markdown)",
        data=rec.export_markdown(),
        file_name="academic_results_report.md",
        mime="text/markdown",
        use_container_width=True
    )
with colB:
    st.download_button(
        "Download Tables (CSV ZIP)",
        data=rec.export_tables_zip(),
        file_name="academic_results_tables.zip",
        mime="application/zip",
        use_container_width=True
    )
with colC:
    st.download_button(
        "Download Charts (PNG/HTML ZIP)",
        data=rec.export_charts_zip(),
        file_name="academic_results_charts.zip",
        mime="application/zip",
        use_container_width=True
    )

st.caption("📊 Academic Results • Report view • Streamlit + Supabase")

# -------------------------
# Utilities (local)
# -------------------------
def _first_present(df: pd.DataFrame, candidates: list[str]) -> str | None:
    for c in candidates:
        if c in df.columns:
            return c
    return None
