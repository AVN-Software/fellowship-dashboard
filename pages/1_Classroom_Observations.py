# classroom_observations_dashboard.py
# -------------------------------------------------------------------
# Streamlined, tab-based dashboard for TTN HITS observations
# * Works standalone with generated sample data
# * Robust to empty filters / edge cases
# -------------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# =========================
# Page Config
# =========================
st.set_page_config(page_title="Classroom Observations (HITS)", page_icon="📊", layout="wide")

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
        "LE": "#59A14F",
        "SE": "#4E79A7",
        "KPC": "#9C755F",
        "AII": "#E15759",
        "IAL": "#F28E2B",
        "IAN": "#76B7B2",
    },
}

# =========================
# Utilities
# =========================
def color_map_from_keys(keys, mapping):
    return [mapping.get(k, "#888888") for k in keys]

def reset_filters():
    for k in list(st.session_state.keys()):
        if k.startswith("flt_") or k.startswith("tab_"):
            del st.session_state[k]

def kpi_card(label, value, delta=None, help_text=None):
    st.metric(label, value, delta=delta, help=help_text)

def safe_mean(series):
    s = pd.to_numeric(series, errors="coerce").dropna()
    return float(s.mean()) if len(s) else np.nan

def _grade_key(g):
    """Robust numeric sorter for 'Grade X' or plain ints/strings."""
    try:
        if isinstance(g, (int, float)): return int(g)
        return int(str(g).split()[-1])
    except Exception:
        return 9999

# =========================
# Sample Data (cached)
# =========================
@st.cache_data
def generate_sample_data(num_terms=2, seed=42):
    np.random.seed(seed)

    fellows = [f"Fellow {i}" for i in range(1, 96)]
    coaches = ["Coach Sarah", "Coach John", "Coach Maria", "Coach David", "Coach Lisa"]
    subjects = ["Mathematics", "English", "Life Sciences", "Physical Sciences", "History"]
    grades = ["Grade 8", "Grade 9", "Grade 10", "Grade 11", "Grade 12"]
    schools = ["Park High", "Ridge Secondary", "Valley School", "Summit Academy", "Horizon High"]

    all_terms = ["Term 1", "Term 2", "Term 3"]
    terms = all_terms[:num_terms]

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
            observations.append(
                {
                    "observation_id": obs_id,
                    "term": term,
                    "date_lesson_observed": date_observed.date(),
                    "time_lesson": f"{np.random.randint(8,15)}:00",
                    "fellowship_year": fellowship_year,
                    "coach_name": coach,
                    "fellow_name": fellow,
                    "school_name": school,
                    "grade": grade,
                    "subject": subject,
                    "class_size": class_size,
                    "present_learners": present_learners,
                }
            )

            base_score = 2.0 + (fellowship_year - 1) * 0.4 + term_idx * 0.25
            difficulty = {"LE": 0.3, "SE": 0.2, "KPC": 0.1, "AII": -0.1, "IAL": -0.2, "IAN": -0.3}

            for d in DOMAINS:
                s = base_score + difficulty[d] + np.random.uniform(-0.3, 0.3)
                s = max(1.0, min(4.0, s))
                tier = "Tier 1" if s < 2.3 else ("Tier 2" if s < 3.2 else "Tier 3")
                domain_scores.append({"observation_id": obs_id, "domain": d, "classification": tier, "score": round(s, 2)})

            obs_id_counter += 1

    df_obs = pd.DataFrame(observations)
    df_ds = pd.DataFrame(domain_scores)

    df_full = df_obs.merge(
        df_ds.groupby("observation_id")["score"].mean().reset_index(),
        on="observation_id",
        how="left",
    )
    return df_obs, df_ds, df_full, terms, subjects, grades

# =========================
# Data
# =========================
df_observations, df_domain_scores, df_full, TERM_OPTIONS, SUBJECTS, GRADES = generate_sample_data(num_terms=len(TERMS))

# =========================
# Sidebar Filters
# =========================
with st.sidebar:
    st.header("🎛️ Filters")
    st.caption("These apply across all tabs.")

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
st.title("📊 Classroom Observations Dashboard")
st.markdown("**Tracking teaching quality across HITS domains with termly progression**")
st.caption("Demo with generated data. Swap `generate_sample_data` with your live DB query.")
st.divider()

# =========================
# Helper computations
# =========================
def compute_kpis(df):
    if df.empty:
        return {
            "total_obs": 0, "fellows_observed": 0, "total_fellows": df_observations["fellow_name"].nunique(),
            "coverage": 0.0, "growth": np.nan, "first_mean": np.nan, "latest_avg": np.nan, "latest_count": 0
        }

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

    return {
        "total_obs": total_obs, "fellows_observed": fellows_observed, "total_fellows": total_fellows,
        "coverage": coverage, "growth": growth, "first_mean": first_mean,
        "latest_avg": latest_avg, "latest_count": latest_count
    }

def line_progression_overall(df):
    if df.empty:
        return go.Figure()
    term_avg = df.groupby("term", as_index=False)["score"].mean().sort_values("term")
    fig = px.line(
        term_avg, x="term", y="score", markers=True,
        title="Overall Teaching Quality Across Terms",
        labels={"score": "Average Score", "term": "Term"},
        color_discrete_sequence=color_map_from_keys(term_avg["term"], COLORS["terms"]),
    )
    fig.update_traces(line_width=3)
    fig.update_layout(height=380, yaxis=dict(range=[0, 4]))
    return fig

def line_progression_by_year(df):
    if df.empty:
        return go.Figure()
    term_avg = df.groupby(["term", "fellowship_year"], as_index=False)["score"].mean()
    term_avg["Year"] = "Year " + term_avg["fellowship_year"].astype(int).astype(str)
    fig = px.line(
        term_avg, x="term", y="score", color="Year", markers=True,
        title="Overall Teaching Quality: Year 1 vs Year 2",
        labels={"score": "Average Score", "term": "Term"},
        color_discrete_map=COLORS["years"],
    )
    fig.update_layout(height=380, yaxis=dict(range=[0, 4]))
    return fig

def domain_term_bar(df_domain, df_obs):
    if df_domain.empty or df_obs.empty:
        return go.Figure()
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
    return fig

def latest_domain_bar(df_domain, df_obs, split_by_year=False):
    latest = max(flt_terms) if flt_terms else None
    if (latest is None) or df_domain.empty or df_obs.empty:
        return go.Figure()

    data = df_domain.merge(df_obs[["observation_id", "term", "fellowship_year"]], on="observation_id", how="left")
    data = data[data["term"] == latest]
    if data.empty:
        return go.Figure()

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
        return fig

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
    return fig

def tier_stack_for_term(df_domain, df_obs, selected_term):
    if (df_domain.empty or df_obs.empty or selected_term is None):
        return None, None
    data = df_domain.merge(df_obs[["observation_id", "term"]], on="observation_id", how="left")
    data = data[data["term"] == selected_term]
    if data.empty:
        return None, None

    dist = data.groupby(["domain", "classification"], as_index=False).size().rename(columns={"size": "count"})
    totals = data.groupby("domain", as_index=False).size().rename(columns={"size": "total"})
    dist = dist.merge(totals, on="domain", how="left")
    dist["pct"] = (dist["count"] / dist["total"]) * 100

    pivot = dist.pivot(index="domain", columns="classification", values="pct").fillna(0.0)
    for t in ["Tier 1", "Tier 2", "Tier 3"]:
        if t not in pivot.columns:
            pivot[t] = 0.0
    pivot = pivot[["Tier 1", "Tier 2", "Tier 3"]]
    pivot["domain_name"] = pivot.index.map(DOMAIN_NAMES)

    fig = go.Figure()
    for t in ["Tier 1", "Tier 2", "Tier 3"]:
        fig.add_trace(
            go.Bar(
                name=t,
                x=pivot["domain_name"],
                y=pivot[t],
                marker_color=COLORS["tiers"][t],
                text=[f"{v:.0f}%" for v in pivot[t]],
                textposition="inside",
            )
        )
    fig.update_layout(
        barmode="stack",
        title=f"Tier Distribution by Domain — {selected_term}",
        xaxis_title="Domain",
        yaxis_title="Percentage",
        height=420,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        yaxis=dict(range=[0, 100]),
    )

    tier3_pct = pivot["Tier 3"].mean()
    tier2_plus_pct = (pivot["Tier 2"] + pivot["Tier 3"]).mean()
    return fig, {"tier3_avg_pct": tier3_pct, "tier2_plus_avg_pct": tier2_plus_pct}

def bar_by_category(df, category_col, split_by_year=False, title=""):
    if df.empty:
        return go.Figure()
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
    return fig

# =========================
# Tabs
# =========================
tab_overview, tab_domains, tab_subjects_grades, tab_fellows, tab_data = st.tabs(
    ["📌 Overview", "🧭 Domains & Tiers", "📚 Subjects & Grades", "👤 Fellows", "📋 Data Explorer"]
)

# -------------------------
# Overview
# -------------------------
with tab_overview:
    st.subheader("Program Overview")
    if filtered.empty:
        st.warning("No data available for selected filters.")
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

        colA, colB = st.columns([2, 1])
        with colA:
            st.plotly_chart(
                line_progression_by_year(filtered) if flt_year == "Both" else line_progression_overall(filtered),
                use_container_width=True,
            )
        with colB:
            st.markdown("### Insight")
            if not np.isnan(kpis["growth"]):
                st.info(
                    f"**Trend:** From **{kpis['first_mean']:.2f}** to **{kpis['latest_avg']:.2f}** — "
                    f"change **{kpis['growth']:+.2f}**."
                )
            st.caption(
                f"Fellows observed: **{kpis['fellows_observed']}** / total **{kpis['total_fellows']}** "
                f"(**{kpis['coverage']:.0f}%** coverage)."
            )

# -------------------------
# Domains & Tiers
# -------------------------
with tab_domains:
    st.subheader("Domains & Tiers")
    if filtered.empty:
        st.warning("No data available for selected filters.")
    else:
        col_ctrl = st.columns([1, 1, 2])
        with col_ctrl[0]:
            view_mode = st.radio("View", options=["Progress (All Terms)", "Latest Term Only"], horizontal=False, key="tab_domains_view")
        with col_ctrl[1]:
            split_by_year = st.toggle("Split by Year", value=(flt_year == "Both"), key="tab_domains_split_by_year")

        if view_mode == "Progress (All Terms)":
            st.plotly_chart(domain_term_bar(filtered_domain, filtered), use_container_width=True)
        else:
            st.plotly_chart(latest_domain_bar(filtered_domain, filtered, split_by_year=split_by_year), use_container_width=True)

        st.markdown("---")
        col_ta, col_tb = st.columns([2, 1])
        with col_ta:
            valid_terms = sorted(set(flt_terms))
            idx = max(0, len(valid_terms) - 1)
            sel_term = st.selectbox("Select term for tier distribution", options=valid_terms or ["(none)"], index=idx)
            fig_tier, tier_summary = (tier_stack_for_term(filtered_domain, filtered, sel_term) if valid_terms else (None, None))
            if fig_tier is not None:
                st.plotly_chart(fig_tier, use_container_width=True)
            else:
                st.warning("No tier data for the selected term.")
        with col_tb:
            st.markdown("### Tier Insights")
            if tier_summary:
                st.success(f"**Tier 3 (Advanced):** ~{tier_summary['tier3_avg_pct']:.0f}% on average across domains.")
                st.info(f"**Tier 2+:** ~{tier_summary['tier2_plus_avg_pct']:.0f}% across domains.")
                st.caption("Interpretation: strong Tier 2→3 migration suggests effective instructional coaching.")
            else:
                st.caption("Select a term with data to view tier insights.")

# -------------------------
# Subjects & Grades
# -------------------------
with tab_subjects_grades:
    st.subheader("Subjects & Grades")
    if filtered.empty:
        st.warning("No data available for selected filters.")
    else:
        c1, c2 = st.columns(2)
        with c1:
            split_year_sbj = st.toggle("Split Subjects by Year", value=(flt_year == "Both"), key="tab_sbj_split")
            st.plotly_chart(bar_by_category(filtered, "subject", split_by_year=split_year_sbj, title="Teaching Quality by Subject"), use_container_width=True)
        with c2:
            split_year_grd = st.toggle("Split Grades by Year", value=(flt_year == "Both"), key="tab_grd_split")
            st.plotly_chart(bar_by_category(filtered, "grade", split_by_year=split_year_grd, title="Teaching Quality by Grade"), use_container_width=True)

# -------------------------
# Fellows
# -------------------------
with tab_fellows:
    st.subheader("Fellow Progress Tracking & Recognition")
    if filtered.empty:
        st.warning("No data available for selected filters.")
    else:
        cA, cB = st.columns([2, 2])

        with cA:
            fellow_options = sorted(filtered["fellow_name"].unique())
            if not fellow_options:
                st.info("No fellows under current filters.")
            else:
                selected_fellow = st.selectbox("Select a Fellow", options=fellow_options, key="tab_fellow_select")
                fellow_df = filtered[filtered["fellow_name"] == selected_fellow].sort_values("date_lesson_observed")
                fellow_domain_df = filtered_domain[
                    filtered_domain["observation_id"].isin(fellow_df["observation_id"])
                ].merge(
                    fellow_df[["observation_id", "term", "date_lesson_observed"]],
                    on="observation_id",
                    how="left",
                )

                show_breakdown = st.checkbox("Show domain breakdown", value=True, key="tab_fellow_breakdown")

                if not fellow_df.empty:
                    if show_breakdown and not fellow_domain_df.empty:
                        d = fellow_domain_df.groupby(["term", "domain"], as_index=False)["score"].mean()
                        d["domain_name"] = d["domain"].map(DOMAIN_NAMES)
                        fig = px.line(
                            d, x="term", y="score", color="domain_name", markers=True,
                            title=f"{selected_fellow} — Progress by Domain",
                            labels={"score": "Average Score", "term": "Term", "domain_name": "Domain"},
                            color_discrete_map={k: COLORS["domains"][k] for k in DOMAINS},
                        )
                    else:
                        g = fellow_df.groupby("term", as_index=False)["score"].mean()
                        fig = px.line(
                            g, x="term", y="score", markers=True,
                            title=f"{selected_fellow} — Overall Progress",
                            labels={"score": "Average Score", "term": "Term"},
                            color_discrete_sequence=["#59A14F"],
                        )
                    fig.update_layout(height=380, yaxis=dict(range=[0, 4]))
                    st.plotly_chart(fig, use_container_width=True)

                    c1, c2, c3, c4 = st.columns(4)
                    with c1: kpi_card("Total Observations", len(fellow_df))
                    with c2:
                        latest_score = float(fellow_df["score"].iloc[-1])
                        kpi_card("Latest Score", f"{latest_score:.2f}")
                    with c3:
                        if len(fellow_df) >= 2:
                            first_score = float(fellow_df["score"].iloc[0])
                            growth = latest_score - first_score
                            pct = f"{(growth/first_score*100):.0f}%" if first_score > 0 else None
                            kpi_card("Total Growth", f"{growth:+.2f}", delta=pct)
                        else:
                            kpi_card("Total Growth", "N/A")
                    with c4: kpi_card("Average Score", f"{safe_mean(fellow_df['score']):.2f}")

                    st.markdown("##### Latest Observation")
                    lo = fellow_df.iloc[-1]
                    d1, d2, d3, d4 = st.columns(4)
                    with d1: st.write(f"**Date:** {lo['date_lesson_observed']}  \n**Term:** {lo['term']}")
                    with d2: st.write(f"**School:** {lo['school_name']}  \n**Grade:** {lo['grade']}")
                    with d3: st.write(f"**Subject:** {lo['subject']}  \n**Coach:** {lo['coach_name']}")
                    with d4: st.write(f"**Class Size:** {lo['class_size']}  \n**Present:** {lo['present_learners']}")
                else:
                    st.warning("No observations for the selected fellow under current filters.")

        with cB:
            st.markdown("#### Recognition")
            top = (
                filtered.groupby("fellow_name")["score"]
                .mean()
                .sort_values(ascending=False)
                .head(10)
                .reset_index()
            )
            st.write("**🏆 Highest Average Scores**")
            if len(top):
                for i, row in enumerate(top.itertuples(index=False), start=1):
                    count = int((filtered["fellow_name"] == row.fellow_name).sum())
                    st.write(f"{i}. **{row.fellow_name}** — {row.score:.2f} ({count} obs)")
            else:
                st.caption("No data to display.")

            st.markdown("---")
            st.write("**📈 Most Improved (first vs latest)**")
            improvements = []
            for f in filtered["fellow_name"].unique():
                fdf = filtered[filtered["fellow_name"] == f].sort_values("date_lesson_observed")
                if len(fdf) >= 2:
                    first_s, last_s = float(fdf["score"].iloc[0]), float(fdf["score"].iloc[-1])
                    improvements.append((f, last_s - first_s, first_s, last_s))
            if improvements:
                imp_df = (
                    pd.DataFrame(improvements, columns=["fellow", "improvement", "first", "latest"])
                    .sort_values("improvement", ascending=False)
                    .head(10)
                )
                for i, r in enumerate(imp_df.itertuples(index=False), start=1):
                    st.write(f"{i}. **{r.fellow}** — {r.improvement:+.2f} ({r.first:.2f} → {r.latest:.2f})")
                st.caption("_Note: treat improvements based on very few observations with caution._")
            else:
                st.caption("Need at least 2 observations per fellow to compute improvement.")

# -------------------------
# Data Explorer
# -------------------------
with tab_data:
    st.subheader("Full Observation Records")
    if filtered.empty:
        st.warning("No data available for selected filters.")
    else:
        ta, tb, tc, td = st.columns(4)
        with ta:
            tf_fellows = st.multiselect("Fellows", options=sorted(filtered["fellow_name"].unique()), key="tab_tbl_fellows")
        with tb:
            tf_coaches = st.multiselect("Coaches", options=sorted(filtered["coach_name"].unique()), key="tab_tbl_coaches")
        with tc:
            tf_schools = st.multiselect("Schools", options=sorted(filtered["school_name"].unique()), key="tab_tbl_schools")
        with td:
            tf_terms = st.multiselect("Terms", options=sorted(filtered["term"].unique()), key="tab_tbl_terms")

        table_df = filtered.copy()
        if tf_fellows: table_df = table_df[table_df["fellow_name"].isin(tf_fellows)]
        if tf_coaches: table_df = table_df[table_df["coach_name"].isin(tf_coaches)]
        if tf_schools: table_df = table_df[table_df["school_name"].isin(tf_schools)]
        if tf_terms:   table_df = table_df[table_df["term"].isin(tf_terms)]

        pivot = (
            filtered_domain[filtered_domain["observation_id"].isin(table_df["observation_id"])]
            .pivot_table(index="observation_id", columns="domain", values="score", aggfunc="mean")
            .reset_index()
        )
        table_display = table_df.merge(pivot, on="observation_id", how="left")

        display_cols = [
            "term","date_lesson_observed","fellow_name","coach_name","school_name","grade",
            "subject","score","class_size","present_learners",
        ] + [d for d in DOMAINS if d in table_display.columns]

        table_display = table_display[display_cols].sort_values("date_lesson_observed", ascending=False).rename(
            columns={
                "term": "Term",
                "date_lesson_observed": "Date",
                "fellow_name": "Fellow",
                "coach_name": "Coach",
                "school_name": "School",
                "grade": "Grade",
                "subject": "Subject",
                "score": "Avg Score",
                "class_size": "Class Size",
                "present_learners": "Present",
            }
        )

        st.dataframe(table_display, use_container_width=True, height=420, hide_index=True)
        st.caption(f"Showing **{len(table_display)}** of **{len(filtered)}** observations")

        csv = table_display.to_csv(index=False)
        st.download_button(
            "📥 Export to CSV",
            data=csv,
            file_name=f"observations_export_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.divider()
st.caption("📊 Classroom Observations Dashboard • Streamlit • Standardized HITS view (Term 1–2)")
