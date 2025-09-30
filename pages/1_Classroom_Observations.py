# classroom_observations_dashboard.py — Report View (sections + exports)
# -------------------------------------------------------------------
# Streamlined report for TTN HITS observations
# • DB-backed with safe fallback sample data
# • Sections (no tabs)
# • Export: Markdown + Tables (CSV ZIP) + Charts (PNG/HTML ZIP)
# -------------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import io, zipfile

# At the top of your dashboard files
from utils.supabase.database_manager import get_db

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Classroom Observations (HITS) — Report", page_icon="📊", layout="wide")

# =========================
# Constants & Palettes
# =========================
TERMS = ["Term 1", "Term 2"]  # focus on 1 & 2; sample gen can produce 3
DOMAIN_NAMES = {
    "KPC": "Knowledge Progression & Connections",
    "LE": "Learning Environment",
    "SE": "Student Engagement",
    "AII": "Assessment-Informed Instruction",
    "IAL": "Instructional Approach – Literacy",
    "IAN": "Instructional Approach – Numeracy",
}
DOMAINS = list(DOMAIN_NAMES.keys())

COLORS = {
    "terms": {"Term 1": "#4E79A7", "Term 2": "#59A14F", "Term 3": "#F28E2B"},
    "years": {"Year 1": "#4E79A7", "Year 2": "#59A14F"},
    "tiers": {"Tier 1": "#E15759", "Tier 2": "#F1CE63", "Tier 3": "#59A14F"},
    "domains": {
        "LE": "#59A14F", "SE": "#4E79A7", "KPC": "#9C755F",
        "AII": "#E15759", "IAL": "#F28E2B", "IAN": "#76B7B2",
    },
}

# =========================
# Utilities
# =========================
def color_map_from_keys(keys, mapping):
    return [mapping.get(k, "#888888") for k in keys]

def reset_filters():
    for k in list(st.session_state.keys()):
        if k.startswith("flt_"):
            del st.session_state[k]

def kpi_card(label, value, delta=None, help_text=None):
    st.metric(label, value, delta=delta, help=help_text)

def safe_mean(series):
    s = pd.to_numeric(series, errors="coerce").dropna()
    return float(s.mean()) if len(s) else np.nan

def _grade_key(g):
    try:
        if isinstance(g, (int, float)): return int(g)
        return int(str(g).split()[-1])
    except Exception:
        return 9999

def _safe(name: str) -> str:
    return str(name).replace("/", "_").replace("\\", "_").replace(" ", "_")[:60]

# =========================
# Export Recorder
# =========================
class Exporter:
    """Collect sections' markdown, figures, and tables for export."""
    def __init__(self):
        self.md_chunks: list[str] = []
        self.tables: dict[str, pd.DataFrame] = {}
        self.figs: dict[str, go.Figure] = {}

    def md(self, text: str):
        st.markdown(text)
        self.md_chunks.append(text if text.endswith("\n") else text + "\n")

    def hr(self):
        st.write("---")
        self.md_chunks.append("\n---\n")

    def add_table(self, name: str, df: pd.DataFrame):
        if isinstance(df, pd.DataFrame) and not df.empty:
            self.tables[name] = df.copy()

    def add_fig(self, name: str, fig: go.Figure | None):
        if fig is not None:
            self.figs[name] = fig

    def export_markdown(self) -> bytes:
        return "".join(self.md_chunks).encode("utf-8")

    def export_tables_zip(self) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, df in self.tables.items():
                zf.writestr(f"{_safe(name)}.csv", df.to_csv(index=False).encode("utf-8"))
        buf.seek(0)
        return buf.getvalue()

    def export_charts_zip(self) -> bytes:
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, fig in self.figs.items():
                wrote = False
                try:
                    png = fig.to_image(format="png", scale=2)  # needs kaleido
                    zf.writestr(f"{_safe(name)}.png", png)
                    wrote = True
                except Exception:
                    wrote = False
                if not wrote:
                    html = fig.to_html(include_plotlyjs="cdn", full_html=False).encode("utf-8")
                    zf.writestr(f"{_safe(name)}.html", html)
        buf.seek(0)
        return buf.getvalue()

rec = Exporter()

# =========================
# Data (DB-backed with safe fallback)
# =========================
@st.cache_data(show_spinner=True)
def load_observation_data():
    """
    Loads from Supabase view `v_observation_full`.
    Produces:
      - df_observations : one row per observation_id (lesson-level fields)
      - df_domain_scores: domain-level rows (observation_id, domain, score, classification)
      - df_full         : observation-level with `score` = mean of domain scores
      - TERM_OPTIONS, SUBJECTS, GRADES for filters
    Fallbacks to generated sample data if DB is empty/unavailable.
    """
    try:
        db = get_db()
        df_view = db.get_observations_full()

        if df_view is not None and not df_view.empty:
            keep_domain_cols = ["observation_id", "domain", "score", "classification"]
            df_domain_scores = df_view[keep_domain_cols].dropna(subset=["observation_id"]).copy()

            obs_cols = [
                "observation_id","term","date_lesson_observed","time_lesson",
                "fellowship_year","coach_name","fellow_name","school_name",
                "grade","subject","class_size","present_learners",
            ]
            obs_cols = [c for c in obs_cols if c in df_view.columns]
            df_observations = df_view[obs_cols].drop_duplicates(subset=["observation_id"]).copy()

            avg_by_obs = (
                df_domain_scores.groupby("observation_id", as_index=False)["score"]
                .mean()
                .rename(columns={"score": "score"})
            )
            df_full = df_observations.merge(avg_by_obs, on="observation_id", how="left")

            term_order = {"Term 1": 1, "Term 2": 2, "Term 3": 3, "Term 4": 4}
            terms_raw = sorted(df_full["term"].dropna().unique(), key=lambda t: term_order.get(t, 999))
            TERM_OPTIONS = [t for t in terms_raw if t in ("Term 1", "Term 2")] or terms_raw[:2]

            SUBJECTS = sorted(df_full["subject"].dropna().unique()) if "subject" in df_full.columns else []
            GRADES   = sorted(df_full["grade"].dropna().unique(), key=_grade_key) if "grade" in df_full.columns else []

            return df_observations, df_domain_scores, df_full, TERM_OPTIONS, SUBJECTS, GRADES

        st.warning("`v_observation_full` returned no rows; using sample data fallback.")
        raise RuntimeError("Empty DB result")

    except Exception:
        # ---------- FALLBACK: sample generator ----------
        np.random.seed(42)
        fellows = [f"Fellow {i}" for i in range(1, 96)]
        coaches = ["Coach Sarah", "Coach John", "Coach Maria", "Coach David", "Coach Lisa"]
        subjects = ["Mathematics", "English", "Life Sciences", "Physical Sciences", "History"]
        grades = ["Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"]
        schools = ["Park High", "Ridge Secondary", "Valley School", "Summit Academy", "Horizon High"]
        all_terms = ["Term 1", "Term 2", "Term 3"]
        terms = all_terms[:2]

        observations, domain_scores = [], []
        obs_id_counter = 1

        for term_idx, term in enumerate(terms):
            num_obs_term = 70 + (term_idx * 15)
            for _ in range(num_obs_term):
                fellow = np.random.choice(fellows)
                fellowship_year = 1 if fellows.index(fellow) < 45 else 2
                coach = np.random.choice(coaches)
                subject = np.random.choice(subjects)
                grade = np.random.choice(grades)
                school = np.random.choice(schools)

                base_date = datetime(2024, 1, 1) + timedelta(days=term_idx * 90)
                date_observed = base_date + timedelta(days=np.random.randint(0, 80))

                class_size = np.random.randint(25, 45)
                present_learners = int(class_size * np.random.uniform(0.8, 0.95))

                obs_id = f"obs_{obs_id_counter}"
                observations.append({
                    "observation_id": obs_id, "term": term,
                    "date_lesson_observed": date_observed.date(),
                    "time_lesson": f"{np.random.randint(8,15)}:00",
                    "fellowship_year": fellowship_year, "coach_name": coach,
                    "fellow_name": fellow, "school_name": school,
                    "grade": grade, "subject": subject,
                    "class_size": class_size, "present_learners": present_learners,
                })

                base_score = 2.0 + (fellowship_year - 1) * 0.4 + term_idx * 0.25
                difficulty = {"LE": 0.3, "SE": 0.2, "KPC": 0.1, "AII": -0.1, "IAL": -0.2, "IAN": -0.3}

                for d in ["KPC","LE","SE","AII","IAL","IAN"]:
                    s = base_score + difficulty[d] + np.random.uniform(-0.3, 0.3)
                    s = max(1.0, min(4.0, s))
                    tier = "Tier 1" if s < 2.3 else ("Tier 2" if s < 3.2 else "Tier 3")
                    domain_scores.append({"observation_id": obs_id, "domain": d, "classification": tier, "score": round(s, 2)})

                obs_id_counter += 1

        df_observations = pd.DataFrame(observations)
        df_domain_scores = pd.DataFrame(domain_scores)
        df_full = df_observations.merge(
            df_domain_scores.groupby("observation_id")["score"].mean().reset_index(),
            on="observation_id", how="left",
        )
        TERM_OPTIONS = ["Term 1", "Term 2"]
        SUBJECTS = sorted(df_observations["subject"].unique())
        GRADES = sorted(df_observations["grade"].unique(), key=_grade_key)

        return df_observations, df_domain_scores, df_full, TERM_OPTIONS, SUBJECTS, GRADES

# Load data now (DB or fallback)
df_observations, df_domain_scores, df_full, TERM_OPTIONS, SUBJECTS, GRADES = load_observation_data()

# =========================
# Sidebar Filters
# =========================
with st.sidebar:
    st.header("🎛️ Filters")
    st.caption("These apply across all sections.")
    flt_terms = st.multiselect("Term", options=TERM_OPTIONS, default=TERM_OPTIONS, key="flt_terms")
    flt_subjects = st.multiselect("Subject", options=sorted(SUBJECTS), default=list(SUBJECTS), key="flt_subjects")
    grade_sorted = sorted(GRADES, key=_grade_key)
    flt_grades = st.multiselect("Grade", options=grade_sorted, default=grade_sorted, key="flt_grades")
    flt_year = st.radio("Fellowship Year", options=["Both", "Year 1", "Year 2"], horizontal=True, key="flt_year")
    st.markdown("---")
    if st.button("♻️ Reset filters", use_container_width=True):
        reset_filters()
        st.rerun()

# Apply filters (global)
filtered = df_full[
    df_full["term"].isin(flt_terms)
    & df_full["subject"].isin(flt_subjects)
    & df_full["grade"].isin(flt_grades)
].copy()
if flt_year != "Both":
    y = 1 if flt_year.endswith("1") else 2
    filtered = filtered[filtered["fellowship_year"] == y]
filtered_domain = df_domain_scores[df_domain_scores["observation_id"].isin(filtered["observation_id"])].copy()

# =========================
# Header
# =========================
st.title("📊 Classroom Observations — Report")
st.markdown("**Tracking teaching quality across HITS domains with termly progression**")
st.caption("Demo with generated data. Swap `get_observations_full()` with your live DB view.")
st.divider()

# =========================
# Helper computations (fig factories)
# =========================
def compute_kpis(df):
    if df.empty:
        return {"total_obs": 0, "fellows_observed": 0, "total_fellows": df_observations["fellow_name"].nunique(),
                "coverage": 0.0, "growth": np.nan, "first_mean": np.nan, "latest_avg": np.nan, "latest_count": 0}
    total_obs = len(df)
    fellows_observed = df["fellow_name"].nunique()
    total_fellows = df_observations["fellow_name"].nunique()
    coverage = (fellows_observed / total_fellows * 100) if total_fellows else 0.0

    if len(flt_terms) >= 2:
        t_sorted = sorted(flt_terms)
        first_mean = safe_mean(df[df["term"] == t_sorted[0]]["score"])
        last_mean  = safe_mean(df[df["term"] == t_sorted[-1]]["score"])
        growth = last_mean - first_mean if not (np.isnan(first_mean) or np.isnan(last_mean)) else np.nan
    else:
        first_mean = safe_mean(df["score"])
        growth = np.nan

    latest_term = max(flt_terms) if len(flt_terms) else None
    latest_avg  = safe_mean(df[df["term"] == latest_term]["score"]) if latest_term else np.nan
    latest_count = int(len(df[df["term"] == latest_term])) if latest_term else 0

    return {"total_obs": total_obs, "fellows_observed": fellows_observed, "total_fellows": total_fellows,
            "coverage": coverage, "growth": growth, "first_mean": first_mean,
            "latest_avg": latest_avg, "latest_count": latest_count}

def line_progression_overall(df):
    if df.empty: return go.Figure()
    term_avg = df.groupby("term", as_index=False)["score"].mean().sort_values("term")
    fig = px.line(
        term_avg, x="term", y="score", markers=True,
        title="Overall Teaching Quality Across Terms",
        labels={"score": "Average Score", "term": "Term"},
        color_discrete_sequence=color_map_from_keys(term_avg["term"], COLORS["terms"]),
    )
    fig.update_traces(line_width=3)
    fig.update_layout(height=380, yaxis=dict(range=[0, 4]))
    return fig, term_avg.rename(columns={"score":"avg_score"})

def line_progression_by_year(df):
    if df.empty: return go.Figure()
    term_avg = df.groupby(["term", "fellowship_year"], as_index=False)["score"].mean()
    term_avg["Year"] = "Year " + term_avg["fellowship_year"].astype(int).astype(str)
    fig = px.line(
        term_avg, x="term", y="score", color="Year", markers=True,
        title="Overall Teaching Quality: Year 1 vs Year 2",
        labels={"score": "Average Score", "term": "Term"},
        color_discrete_map=COLORS["years"],
    )
    fig.update_layout(height=380, yaxis=dict(range=[0, 4]))
    return fig, term_avg.rename(columns={"score":"avg_score"})

def domain_term_bar(df_domain, df_obs):
    if df_domain.empty or df_obs.empty: return go.Figure(), pd.DataFrame()
    data = df_domain.merge(df_obs[["observation_id", "term"]], on="observation_id", how="left")
    domain_term = data.groupby(["domain", "term"], as_index=False)["score"].mean()
    domain_term["domain_name"] = domain_term["domain"].map(DOMAIN_NAMES)
    fig = px.bar(
        domain_term, x="domain_name", y="score", color="term", barmode="group",
        title="Domain Performance Across Terms",
        labels={"domain_name": "Domain", "score": "Average Score", "term": "Term"},
        color_discrete_map=COLORS["terms"],
    )
    fig.update_layout(height=480, yaxis=dict(range=[0, 4]))
    return fig, domain_term.rename(columns={"score":"avg_score"})

def latest_domain_bar(df_domain, df_obs, split_by_year=False):
    latest = max(flt_terms) if flt_terms else None
    if (latest is None) or df_domain.empty or df_obs.empty:
        return go.Figure(), pd.DataFrame()
    data = df_domain.merge(df_obs[["observation_id", "term", "fellowship_year"]], on="observation_id", how="left")
    data = data[data["term"] == latest]
    if data.empty: return go.Figure(), pd.DataFrame()

    if split_by_year and flt_year == "Both":
        g = data.groupby(["domain", "fellowship_year"], as_index=False)["score"].mean()
        g["Year"] = "Year " + g["fellowship_year"].astype(int).astype(str)
        g["domain_name"] = g["domain"].map(DOMAIN_NAMES)
        fig = px.bar(
            g, x="domain_name", y="score", color="Year", barmode="group",
            title=f"Domain Performance — {latest}",
            labels={"domain_name": "Domain", "score": "Average Score"},
            color_discrete_map=COLORS["years"],
        )
        fig.update_layout(height=460, yaxis=dict(range=[0, 4]))
        return fig, g.rename(columns={"score":"avg_score"})
    g = data.groupby("domain", as_index=False)["score"].mean()
    g["domain_name"] = g["domain"].map(DOMAIN_NAMES)
    g = g.sort_values("score", ascending=True)
    fig = px.bar(
        g, x="score", y="domain_name", orientation="h",
        title=f"Domain Performance — {latest}",
        labels={"domain_name": "Domain", "score": "Average Score"},
        color_discrete_sequence=["#4E79A7"],
    )
    fig.update_layout(height=460, xaxis=dict(range=[0, 4]))
    return fig, g.rename(columns={"score":"avg_score"})

def tier_stack_for_term(df_domain, df_obs, selected_term):
    if (df_domain.empty or df_obs.empty or selected_term is None):
        return None, None, pd.DataFrame()
    data = df_domain.merge(df_obs[["observation_id", "term"]], on="observation_id", how="left")
    data = data[data["term"] == selected_term]
    if data.empty: return None, None, pd.DataFrame()

    dist = data.groupby(["domain", "classification"], as_index=False).size().rename(columns={"size": "count"})
    totals = data.groupby("domain", as_index=False).size().rename(columns={"size": "total"})
    dist = dist.merge(totals, on="domain", how="left")
    dist["pct"] = (dist["count"] / dist["total"]) * 100

    pivot = dist.pivot(index="domain", columns="classification", values="pct").fillna(0.0)
    for t in ["Tier 1", "Tier 2", "Tier 3"]:
        if t not in pivot.columns: pivot[t] = 0.0
    pivot = pivot[["Tier 1", "Tier 2", "Tier 3"]]
    pivot["domain_name"] = pivot.index.map(DOMAIN_NAMES)

    fig = go.Figure()
    for t in ["Tier 1", "Tier 2", "Tier 3"]:
        fig.add_trace(go.Bar(
            name=t, x=pivot["domain_name"], y=pivot[t], marker_color=COLORS["tiers"][t],
            text=[f"{v:.0f}%" for v in pivot[t]], textposition="inside",
        ))
    fig.update_layout(
        barmode="stack", title=f"Tier Distribution by Domain — {selected_term}",
        xaxis_title="Domain", yaxis_title="Percentage", height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[0, 100]),
    )
    tier3_pct = pivot["Tier 3"].mean()
    tier2_plus_pct = (pivot["Tier 2"] + pivot["Tier 3"]).mean()
    summary = {"tier3_avg_pct": tier3_pct, "tier2_plus_avg_pct": tier2_plus_pct}
    return fig, summary, pivot.reset_index(drop=False).rename(columns={"index":"domain"})

def bar_by_category(df, category_col, split_by_year=False, title=""):
    if df.empty: return go.Figure(), pd.DataFrame()
    if split_by_year and flt_year == "Both":
        g = df.groupby([category_col, "fellowship_year"], as_index=False)["score"].mean()
        g["Year"] = "Year " + g["fellowship_year"].astype(int).astype(str)
        fig = px.bar(
            g, x=category_col, y="score", color="Year", barmode="group",
            title=title, labels={"score": "Average Score"},
            color_discrete_map=COLORS["years"],
        )
    else:
        g = df.groupby(category_col, as_index=False)["score"].mean()
        if category_col == "grade":
            g["__gnum"] = g[category_col].map(_grade_key)
            g = g.sort_values("__gnum")
        fig = px.bar(
            g, x=category_col, y="score",
            title=title, labels={"score": "Average Score"},
            color_discrete_sequence=["#4E79A7"],
        )
    fig.update_layout(height=380, yaxis=dict(range=[0, 4]))
    return fig, g.rename(columns={"score":"avg_score"})

# =========================
# Table of Contents
# =========================
rec.md("## Table of Contents")
rec.md("""
- [1. Executive Summary](#1-executive-summary)
- [2. Domains & Tiers](#2-domains--tiers)
- [3. Subjects & Grades](#3-subjects--grades)
- [4. Fellows Spotlight](#4-fellows-spotlight)
- [5. Data Appendix](#5-data-appendix)
""")
rec.hr()

# =========================
# 1) Executive Summary
# =========================
rec.md("## 1. Executive Summary")
if filtered.empty:
    rec.md("_No data available for selected filters._")
else:
    kpis = compute_kpis(filtered)
    c1, c2, c3, c4 = st.columns(4)
    with c1: kpi_card("Total Observations", f"{kpis['total_obs']:,}")
    with c2: kpi_card("Coverage", f"{kpis['coverage']:.0f}%")
    with c3: kpi_card("Avg Score (Latest)", f"{(kpis['latest_avg'] if not np.isnan(kpis['latest_avg']) else 0):.2f}")
    with c4:
        delta = f"{kpis['growth']:+.2f}" if not np.isnan(kpis["growth"]) else None
        base_delta = (kpis['latest_avg'] - kpis['first_mean']) if not np.isnan(kpis['latest_avg']) else np.nan
        kpi_card("Term-on-Term Growth", f"{(base_delta if not np.isnan(base_delta) else 0):+.2f}", delta=delta)

    # Overall progression (by year or total)
    if flt_year == "Both":
        fig_exec, term_year_tbl = line_progression_by_year(filtered)
        st.plotly_chart(fig_exec, use_container_width=True)
        rec.add_fig("Executive_Progress_YearSplit", fig_exec)
        rec.add_table("Executive_Term_Year_Averages", term_year_tbl)
    else:
        fig_exec, term_tbl = line_progression_overall(filtered)
        st.plotly_chart(fig_exec, use_container_width=True)
        rec.add_fig("Executive_Progress_Overall", fig_exec)
        rec.add_table("Executive_Term_Averages", term_tbl)

    st.caption(
        f"Fellows observed: **{kpis['fellows_observed']}** / total **{kpis['total_fellows']}** "
        f"(**{kpis['coverage']:.0f}%** coverage)."
    )
rec.hr()

# =========================
# 2) Domains & Tiers
# =========================
rec.md("## 2. Domains & Tiers")
if filtered.empty:
    st.warning("No data available for selected filters.")
else:
    c_view, c_split = st.columns([1,1])
    with c_view:
        view_mode = st.radio("View", options=["Progress (All Terms)", "Latest Term Only"], horizontal=True, key="view_domains")
    with c_split:
        split_by_year = st.toggle("Split by Year", value=(flt_year == "Both"), key="split_domains_year")

    if view_mode == "Progress (All Terms)":
        fig_dom, dom_tbl = domain_term_bar(filtered_domain, filtered)
        st.plotly_chart(fig_dom, use_container_width=True)
        rec.add_fig("Domains_Progress_AllTerms", fig_dom)
        rec.add_table("Domains_Avg_by_Term", dom_tbl)
    else:
        fig_dom, dom_tbl = latest_domain_bar(filtered_domain, filtered, split_by_year=split_by_year)
        st.plotly_chart(fig_dom, use_container_width=True)
        rec.add_fig("Domains_Latest", fig_dom)
        rec.add_table("Domains_Latest_Table", dom_tbl)

    st.markdown("---")
    valid_terms = sorted(set(flt_terms))
    idx = max(0, len(valid_terms) - 1)
    sel_term = st.selectbox("Select term for tier distribution", options=valid_terms or ["(none)"], index=idx)
    fig_tier, tier_summary, tier_tbl = tier_stack_for_term(filtered_domain, filtered, sel_term) if valid_terms else (None, None, pd.DataFrame())
    if fig_tier is not None:
        st.plotly_chart(fig_tier, use_container_width=True)
        rec.add_fig(f"Tier_Distribution_{sel_term}", fig_tier)
        rec.add_table(f"Tier_Distribution_{sel_term}_Table", tier_tbl)
        st.success(f"**Tier 3 (Advanced):** ~{tier_summary['tier3_avg_pct']:.0f}% • **Tier 2+:** ~{tier_summary['tier2_plus_avg_pct']:.0f}%")
    else:
        st.caption("Select a term with data to view tier insights.")
rec.hr()

# =========================
# 3) Subjects & Grades
# =========================
rec.md("## 3. Subjects & Grades")
if filtered.empty:
    st.warning("No data available for selected filters.")
else:
    c1, c2 = st.columns(2)
    with c1:
        split_year_sbj = st.toggle("Split Subjects by Year", value=(flt_year == "Both"), key="split_subj_year")
        fig_sbj, subj_tbl = bar_by_category(filtered, "subject", split_by_year=split_year_sbj, title="Teaching Quality by Subject")
        st.plotly_chart(fig_sbj, use_container_width=True)
        rec.add_fig("Subjects_by_Term_or_Year", fig_sbj)
        rec.add_table("Subjects_Summary", subj_tbl)
    with c2:
        split_year_grd = st.toggle("Split Grades by Year", value=(flt_year == "Both"), key="split_grade_year")
        fig_grd, grade_tbl = bar_by_category(filtered, "grade", split_by_year=split_year_grd, title="Teaching Quality by Grade")
        st.plotly_chart(fig_grd, use_container_width=True)
        rec.add_fig("Grades_by_Term_or_Year", fig_grd)
        rec.add_table("Grades_Summary", grade_tbl)
rec.hr()

# =========================
# 4) Fellows Spotlight
# =========================
rec.md("## 4. Fellows Spotlight")
if filtered.empty:
    st.warning("No data available for selected filters.")
else:
    # Leaderboard tables (export-friendly, minimal interactivity)
    top_avg = (
        filtered.groupby("fellow_name")["score"]
        .agg(avg_score="mean", n_obs="count").reset_index()
        .sort_values("avg_score", ascending=False).head(10)
    )
    rec.add_table("Fellows_Top_Average", top_avg)
    st.markdown("**🏆 Highest Average Scores (Top 10)**")
    st.dataframe(top_avg, use_container_width=True, hide_index=True)

    improvements = []
    for f in filtered["fellow_name"].unique():
        fdf = filtered[filtered["fellow_name"] == f].sort_values("date_lesson_observed")
        if len(fdf) >= 2:
            first_s, last_s = float(fdf["score"].iloc[0]), float(fdf["score"].iloc[-1])
            improvements.append((f, last_s - first_s, first_s, last_s, len(fdf)))
    if improvements:
        imp_df = pd.DataFrame(improvements, columns=["fellow_name", "improvement", "first", "latest", "n_obs"])\
                 .sort_values("improvement", ascending=False).head(10)
        rec.add_table("Fellows_Most_Improved", imp_df)
        st.markdown("**📈 Most Improved (Top 10)**")
        st.dataframe(imp_df, use_container_width=True, hide_index=True)
    else:
        st.caption("Need at least 2 observations per fellow to compute improvement.")
rec.hr()

# =========================
# 5) Data Appendix
# =========================
rec.md("## 5. Data Appendix")
if filtered.empty:
    st.warning("No data available for selected filters.")
else:
    # Compact record table (same as before, exportable)
    pivot = (
        filtered_domain[filtered_domain["observation_id"].isin(filtered["observation_id"])]
        .pivot_table(index="observation_id", columns="domain", values="score", aggfunc="mean")
        .reset_index()
    )
    table_display = filtered.merge(pivot, on="observation_id", how="left")
    display_cols = [
        "term","date_lesson_observed","fellow_name","coach_name","school_name","grade",
        "subject","score","class_size","present_learners",
    ] + [d for d in DOMAINS if d in table_display.columns]
    table_display = table_display[display_cols].sort_values("date_lesson_observed", ascending=False).rename(columns={
        "term": "Term","date_lesson_observed": "Date","fellow_name": "Fellow","coach_name": "Coach",
        "school_name": "School","grade": "Grade","subject": "Subject","score": "Avg Score",
        "class_size": "Class Size","present_learners": "Present",
    })
    st.dataframe(table_display, use_container_width=True, height=420, hide_index=True)
    st.caption(f"Showing **{len(table_display)}** of **{len(filtered)}** observations")
    rec.add_table("Appendix_Observations_Table", table_display)

rec.hr()

# =========================
# Exports
# =========================
st.subheader("⬇️ Export")
cA, cB, cC = st.columns([1,1,1])
with cA:
    st.download_button(
        "Download Report (Markdown)",
        data=rec.export_markdown(),
        file_name=f"classroom_observations_report_{datetime.now().strftime('%Y%m%d')}.md",
        mime="text/markdown", use_container_width=True
    )
with cB:
    st.download_button(
        "Download Tables (CSV ZIP)",
        data=rec.export_tables_zip(),
        file_name=f"classroom_observations_tables_{datetime.now().strftime('%Y%m%d')}.zip",
        mime="application/zip", use_container_width=True
    )
with cC:
    st.download_button(
        "Download Charts (PNG/HTML ZIP)",
        data=rec.export_charts_zip(),
        file_name=f"classroom_observations_charts_{datetime.now().strftime('%Y%m%d')}.zip",
        mime="application/zip", use_container_width=True
    )

st.caption("📊 Classroom Observations • Report view • Streamlit • Standardized HITS (Term 1–2)")
