# fellow_wellbeing_dashboard.py
# ---------------------------------------------------------------
# Fellow Wellbeing Dashboard (Term-focused)
# - Primary lens: Overall wellbeing per term (Term 1, Term 2)
# - Filters: Term • Phase • Year of Fellowship • Facilitator
# - Tabs: Overview • Progression • Domains • Indicators • At-Risk • Fellows • Data
# - Safe sample-data gen (no int32 overflow)
# ---------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import components.filters as fx

# --- make repo root importable (so we can import utils.* from /pages) ---
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]  # repo root (one level up from /pages)
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# --- import your DB manager ---
try:
    from utils.supabase.database_manager import DatabaseManager
except Exception as e:
    DatabaseManager = None
    import streamlit as st
    st.warning(f"DatabaseManager import failed ({e}). Will try local fallback for wellbeing data.")

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Fellow Wellbeing Survey",
    page_icon="🌱",
    layout="wide",
)

# =========================
# Constants & Palettes
# =========================
TERMS = ["Term 1", "Term 2"]  # ordered focus
SCORE_MIN, SCORE_MAX = 1, 3

COLORS = {
    "terms": {
        "Term 1": "#4E79A7",
        "Term 2": "#59A14F",
    },
    "years": {
        "Year 1": "#4E79A7",
        "Year 2": "#59A14F",
    },
    "traffic": {
        "bad": "#E15759",      # red
        "warn": "#F1CE63",     # amber
        "good": "#59A14F",     # green
        "neutral": "#4E79A7",  # blue
    },
    "gradient": ['#E15759', '#F28E2B', '#F1CE63', '#59A14F'],
}

# Domain → indicators (63 total)
DIMENSIONS = {
    "School Environment & Participation": [
        "common_vision_and_mission","sense_of_confidence_in_management","autonomy_as_professional_teacher",
        "feedback_on_performance","support_for_professional_development","co_curricular_activities",
        "authenticity_able_to_be_myself_at_school","influence_on_classroom_culture",
        "deep_engagement_in_teaching_process","respect_and_being_valued"
    ],
    "Learning (Others)": [
        "pedagogy_for_effective_performance","stimulating_sense_of_purpose_in_learners",
        "open_communication_on_non_school_topics","role_model_at_school"
    ],
    "Meaning (Self)": [
        "conviction_about_choice_of_career","fulfilment_derived_from_work","perceived_value_in_society_as_teacher",
        "proactive_teaching_approaches","pride_in_work","alignment_of_personal_and_school_values",
        "workload","creative_freedom_to_accomplish_work"
    ],
    "Income & Employment": [
        "income_and_earnings_to_meet_needs","remuneration_aligned_with_responsibilities","employment_contract",
        "access_to_credit_facilities","personal_savings","budgeting_and_planning","management_of_debt"
    ],
    "Health & Environment": [
        "nutrition","ability_to_deal_with_stress","physical_health_and_personal_hygiene","sleep","access_to_health_care",
        "caring_and_loving_relationships","family_unity","drugs_and_alcohol"
    ],
    "Home Environment & Community": [
        "house_structure","sanitation_and_sewage","electricity","separate_sleeping_spaces","stove_fridge_and_kitchen",
        "regular_means_of_transportation","distance_and_time_to_work","home_and_community_security"
    ],
    "Education & Culture": [
        "educational_opportunities","sensitivity_to_different_socio_economic_backgrounds","advice_and_mentorship",
        "social_networks"
    ],
    "Relationships": [
        "self_confidence","sense_of_belonging_inclusion","self_esteem_and_trust","effective_communication",
        "supportive_relationships_with_colleagues","influence_on_colleagues_and_school_culture",
        "reputation_with_colleagues_and_learners","ability_to_solve_problems_and_conflict"
    ],
    "Awareness & Emotions": [
        "joy_in_teaching","self_awareness","aspiration","motivated","sense_of_control","thriving"
    ],
}
ALL_ITEMS = [i for items in DIMENSIONS.values() for i in items]

# Risk thresholds (single source of truth)
def risk_bucket(score: float) -> str:
    if np.isnan(score): return "—"
    if score < 1.8:   return "🚨 High Risk"
    if score < 2.2:   return "⚠️ At Risk"
    if score < 2.6:   return "⚡ Moderate"
    return "✅ Thriving"

def risk_color(score: float) -> str:
    if np.isnan(score): return COLORS["traffic"]["neutral"]
    if score < 1.8:   return COLORS["traffic"]["bad"]
    if score < 2.2:   return COLORS["traffic"]["warn"]
    if score < 2.6:   return "#F1E5A9"
    return COLORS["traffic"]["good"]

# =========================
# Utilities
# =========================
def reset_filters():
    for k in list(st.session_state.keys()):
        if k.startswith("flt_") or k.startswith("tab_"):
            del st.session_state[k]

def safe_mean(series) -> float:
    return float(series.mean()) if len(series) else float("nan")

def overall_score(df: pd.DataFrame) -> float:
    if len(df) == 0: return float("nan")
    return float(df[ALL_ITEMS].values.flatten().mean())

def dimension_scores(df: pd.DataFrame) -> dict:
    out = {}
    for dim, items in DIMENSIONS.items():
        vals = df[items].values.flatten()
        out[dim] = float(np.mean(vals)) if len(vals) else float("nan")
    return out

def order_terms(values):
    order = {t: i for i, t in enumerate(TERMS)}
    return sorted(values, key=lambda t: order.get(t, 999))

def random_sa_id(n=13):
    # Avoids np.int32 overflow issues by building a string
    return "".join(np.random.choice(list("0123456789"), size=n))

# =========================
# Data Fetch (via DatabaseManager)
# =========================
@st.cache_data
def load_wellbeing_data():
    db = DatabaseManager()   # uses your Supabase URL/KEY inside
    df = db.get_teacher_wellbeing()  # load from Supabase table
    return df

df_surveys = load_wellbeing_data()

# =========================
# Top Filter Bar (replaces sidebar)
# =========================
fx.topbar(
    "📊 Classroom Observations Dashboard",
    "Tracking teaching quality across HITS domains with termly progression"
)

toolbar = st.container()
with toolbar:
    st.markdown("### 🎛️ Filters")
    c1, c2, c3, c4, c5 = st.columns([1.2, 1.2, 1.2, 1.0, 0.7])

    # Use the low-level helpers so we can place widgets into specific columns
    flt_terms = fx._multiselect(
        "Term",
        options=TERM_OPTIONS,
        default=TERM_OPTIONS,
        key="flt_terms",
        target=c1,
    )

    flt_subjects = fx._multiselect(
        "Subject",
        options=sorted(SUBJECTS),
        default=list(SUBJECTS),
        key="flt_subjects",
        target=c2,
    )

    # Sort grades numerically but be robust
    def _grade_key(g):
        try:
            if isinstance(g, (int, float)): return int(g)
            return int(str(g).split()[-1])
        except Exception:
            return 9999

    grade_sorted = sorted(GRADES, key=_grade_key)
    flt_grades = fx._multiselect(
        "Grade",
        options=grade_sorted,
        default=grade_sorted,
        key="flt_grades",
        target=c3,
    )

    flt_year = fx._radio(
        "Fellowship Year",
        options=["Both", "Year 1", "Year 2"],
        key="flt_year",
        horizontal=True,
        index=0,
        target=c4,
    )

    # Reset button on the far right
    if fx.reset_button("♻️ Reset", key="reset_topbar", target=c5):
        for k in list(st.session_state.keys()):
            if k.startswith("flt_") or k.startswith("tab_"):
                del st.session_state[k]
        st.rerun()

# =========================
# Header
# =========================
st.title("🌱 Fellow Wellbeing Survey — Term Focus")
st.markdown("**Tracking holistic wellbeing per term (overall first), with progression by Phase and Year of Fellowship.**")
st.caption("Scoring: 1=Struggling, 2=Coping, 3=Confident • 63 indicators")

st.divider()

# =========================
# Tabs
# =========================
tab_overview, tab_progress, tab_domains, tab_indicators, tab_risk, tab_fellows, tab_data = st.tabs(
    ["📌 Overview", "📈 Progression", "🧭 Domains", "🧩 Indicators", "🚨 At-Risk", "👤 Fellows", "📋 Data"]
)

# -------------------------
# Overview (Term-first)
# -------------------------
with tab_overview:
    st.subheader("Program Snapshot")
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        total_surveys = len(filtered)
        fellows_surveyed = filtered["name_of_client"].nunique()
        ow = overall_score(filtered)

        # self-counts across all indicators
        tot_conf = int(filtered["doing_well"].sum())
        tot_coping = int(filtered["trying_but_struggling"].sum())
        tot_str = int(filtered["stuck"].sum())
        resp_total = tot_conf + tot_coping + tot_str
        p_conf = (tot_conf / resp_total * 100) if resp_total else 0
        p_cop = (tot_coping / resp_total * 100) if resp_total else 0
        p_str = (tot_str / resp_total * 100) if resp_total else 0

        # Term-wise distribution (stacked bars)
        dist_rows = []
        for t in order_terms(filtered["term"].unique()):
            sub = filtered[filtered["term"] == t]
            c3 = int(sub["doing_well"].sum())
            c2 = int(sub["trying_but_struggling"].sum())
            c1 = int(sub["stuck"].sum())
            tot = c1 + c2 + c3
            dist_rows.append({
                "Term": t,
                "Struggling (1)": (c1 / tot * 100) if tot else 0,
                "Coping (2)": (c2 / tot * 100) if tot else 0,
                "Confident (3)": (c3 / tot * 100) if tot else 0,
            })
        dist_df = pd.DataFrame(dist_rows)

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Surveys", f"{total_surveys:,}")
        with c2: st.metric("Fellows Surveyed", f"{fellows_surveyed}")
        with c3:
            st.metric("Avg Wellbeing (Overall)", f"{ow:.2f}")
            st.caption(risk_bucket(ow))
        with c4:
            # at-risk count (overall < 2.0) per row
            tmp = filtered.copy()
            tmp["overall_score_row"] = tmp[ALL_ITEMS].mean(axis=1)
            at_risk_count = int((tmp["overall_score_row"] < 2.0).sum())
            st.metric("At-Risk Rows (<2.0)", at_risk_count)

        # Term distribution
        st.markdown("**Term Distribution — Struggling / Coping / Confident**")
        if not dist_df.empty:
            dist_melt = dist_df.melt(id_vars="Term", var_name="Level", value_name="Percent")
            fig_stack = px.bar(
                dist_melt, x="Term", y="Percent", color="Level",
                title="Distribution by Term",
                text_auto=".0f",
                category_orders={"Term": TERMS}
            )
            fig_stack.update_layout(height=360, barmode="stack", yaxis_range=[0, 100])
            st.plotly_chart(fig_stack, use_container_width=True)

        st.info(
            f"**Insight:** {total_surveys} surveys, {fellows_surveyed} fellows. "
            f"Overall **{ow:.2f}/3.0** ({risk_bucket(ow)}). "
            f"Mix → Confident **{p_conf:.0f}%**, Coping **{p_cop:.0f}%**, Struggling **{p_str:.0f}%**."
        )

# -------------------------
# Progression (Core focus)
# -------------------------
with tab_progress:
    st.subheader("Wellbeing Progression by Term")

    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        cc1, cc2 = st.columns([1.15, 2.85])
        with cc1:
            split_by = st.radio(
                "Split By",
                ["None", "Fellowship Year", "School Phase"],
                horizontal=False,
                key="tab_prog_split",
            )
            show_domain_overlay = st.toggle("Overlay: Domain Avg", value=False, help="Adds domain mean lines for context")

        # Build base frame: overall per row → group per term and split field
        base = filtered.copy()
        base["overall_row"] = base[ALL_ITEMS].mean(axis=1)

        if split_by == "Fellowship Year":
            grp = base.groupby(["term", "fellowship_year"])["overall_row"].mean().reset_index()
            grp["Year"] = grp["fellowship_year"].map({1: "Year 1", 2: "Year 2"})
            fig = px.line(
                grp.sort_values("term"),
                x="term", y="overall_row", color="Year",
                markers=True, title="Overall Wellbeing Progression by Year of Fellowship",
                labels={"overall_row":"Average Score","term":"Term"},
                color_discrete_map=COLORS["years"],
                category_orders={"term": TERMS}
            )
        elif split_by == "School Phase":
            grp = base.groupby(["term", "phase"])["overall_row"].mean().reset_index()
            fig = px.line(
                grp.sort_values("term"),
                x="term", y="overall_row", color="phase",
                markers=True, title="Overall Wellbeing Progression by School Phase",
                labels={"overall_row":"Average Score","term":"Term","phase":"Phase"},
                category_orders={"term": TERMS}
            )
        else:
            grp = base.groupby("term")["overall_row"].mean().reset_index()
            fig = px.line(
                grp.sort_values("term"),
                x="term", y="overall_row",
                markers=True, title="Overall Wellbeing Progression",
                labels={"overall_row":"Average Score","term":"Term"},
                color_discrete_sequence=[COLORS["traffic"]["good"]],
                category_orders={"term": TERMS}
            )

        fig.update_layout(height=420, yaxis_range=[SCORE_MIN, SCORE_MAX])
        st.plotly_chart(fig, use_container_width=True)

        # Quick deltas (Term 1 → Term 2)
        by_term = {t: safe_mean(base.loc[base["term"] == t, "overall_row"]) for t in order_terms(base["term"].unique())}
        keys = [k for k in TERMS if k in by_term]  # keep order
        if len(keys) >= 2:
            first, last = keys[0], keys[-1]
            growth = by_term[last] - by_term[first]
            c1, c2 = st.columns(2)
            with c1: st.metric(f"{first} Avg", f"{by_term[first]:.2f}")
            with c2: st.metric(f"{last} Avg", f"{by_term[last]:.2f}", delta=f"{growth:+.2f}")
            if   growth > 0.10: st.success(f"Improving wellbeing (+{growth:.2f}) from {first} → {last}.")
            elif growth < -0.10: st.warning(f"Decline in wellbeing ({growth:+.2f}) from {first} → {last}.")
            else: st.info(f"Stable wellbeing ({growth:+.2f}) across terms.")

        # Optional domain overlay: show domain means per term as faint reference
        if show_domain_overlay:
            recs = []
            for t in order_terms(base["term"].unique()):
                sub = base[base["term"] == t]
                ds = dimension_scores(sub)
                for d, s in ds.items():
                    recs.append({"term": t, "dimension": d, "score": s})
            ref = pd.DataFrame(recs)
            ref = ref.groupby(["term"])["score"].mean().reset_index()
            ref = ref.sort_values("term")
            fig_ref = px.line(
                ref, x="term", y="score", markers=True,
                labels={"term":"Term","score":"Avg Domain Score"},
                title="Reference: Average of Domain Means"
            )
            fig_ref.update_traces(line=dict(dash="dot"))
            fig_ref.update_layout(height=300, yaxis_range=[SCORE_MIN, SCORE_MAX], showlegend=False)
            st.plotly_chart(fig_ref, use_container_width=True)

# -------------------------
# Domains
# -------------------------
with tab_domains:
    st.subheader("Wellbeing by Domain (9)")
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        ds = dimension_scores(filtered)
        dim_df = pd.DataFrame([{"Domain": k, "Score": v} for k, v in ds.items()]).sort_values("Score")

        chart_type = st.radio("Chart Type", ["Radar Chart","Bar Chart"], horizontal=True, key="tab_domains_chart")
        if chart_type == "Radar Chart":
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=dim_df["Score"].tolist(),
                theta=dim_df["Domain"].tolist(),
                fill='toself',
                name='Wellbeing',
                line=dict(color=COLORS["traffic"]["good"], width=2),
                fillcolor='rgba(89,161,79,0.25)'
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[SCORE_MIN,SCORE_MAX])), showlegend=False, height=480, title="Domain Scores")
        else:
            fig = px.bar(
                dim_df, x="Score", y="Domain", orientation="h", title="Domain Scores",
                labels={"Score":"Average Score","Domain":"Domain"},
                color="Score", color_continuous_scale=COLORS["gradient"], range_color=[SCORE_MIN,SCORE_MAX]
            )
            fig.update_layout(height=480, xaxis_range=[SCORE_MIN, SCORE_MAX])

        st.plotly_chart(fig, use_container_width=True)

        strongest = dim_df.iloc[-1]; weakest = dim_df.iloc[0]
        c1,c2,c3 = st.columns(3)
        with c1: st.success(f"**🏆 Strongest:** {strongest['Domain']} — {strongest['Score']:.2f}")
        with c2: st.warning(f"**🧭 Needs Attention:** {weakest['Domain']} — {weakest['Score']:.2f}")
        with c3:
            thriving = sum(1 for s in dim_df["Score"] if s >= 2.6)
            at_risk = sum(1 for s in dim_df["Score"] if s < 2.0)
            st.info(f"**Domain Health:** {thriving}/9 thriving • {at_risk}/9 at-risk")

# -------------------------
# Indicators (drilldown)
# -------------------------
with tab_indicators:
    st.subheader("Indicator Drilldown (per Domain)")
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        sel_dim = st.selectbox("Select Domain", options=list(DIMENSIONS.keys()), key="tab_ind_sel")
        items = DIMENSIONS[sel_dim]

        rows = []
        for it in items:
            vals = filtered[it]
            n1 = int((vals == 1).sum()); n2 = int((vals == 2).sum()); n3 = int((vals == 3).sum())
            tot = n1 + n2 + n3
            rows.append({
                "Indicator": it.replace("_"," ").title(),
                "Avg Score": vals.mean(),
                "% Struggling": (n1/tot*100) if tot else 0,
                "% Coping": (n2/tot*100) if tot else 0,
                "% Confident": (n3/tot*100) if tot else 0,
            })
        idf = pd.DataFrame(rows).sort_values("Avg Score")

        fig = px.bar(
            idf, x="Avg Score", y="Indicator", orientation="h",
            title=f"Indicators — {sel_dim}",
            labels={"Avg Score":"Average Score","Indicator":"Indicator"},
            color="Avg Score", color_continuous_scale=COLORS["gradient"], range_color=[SCORE_MIN,SCORE_MAX],
            text="Avg Score"
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(height=max(420, len(items)*38), xaxis_range=[SCORE_MIN, SCORE_MAX+0.15])
        st.plotly_chart(fig, use_container_width=True)

        show = idf.copy()
        show["Avg Score"] = show["Avg Score"].map(lambda x: f"{x:.2f}")
        show["% Struggling"] = show["% Struggling"].map(lambda x: f"{x:.1f}%")
        show["% Coping"] = show["% Coping"].map(lambda x: f"{x:.1f}%")
        show["% Confident"] = show["% Confident"].map(lambda x: f"{x:.1f}%")
        st.dataframe(show, use_container_width=True, hide_index=True)

        crit = idf[idf["Avg Score"] < 2.0]
        if len(crit):
            st.warning(f"⚠️ {len(crit)} indicators below 2.0:")
            for _, r in crit.iterrows():
                st.caption(f"• {r['Indicator']}: {r['Avg Score']:.2f}")
        else:
            st.success("✅ All indicators above the 2.0 threshold for this domain.")


# -------------------------
# Data Explorer
# -------------------------
with tab_data:
    st.subheader("Full Survey Data")
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        t1, t2, t3 = st.columns(3)
        with t1:
            f_fellows = st.multiselect("Fellows", options=sorted(filtered["name_of_client"].unique()), key="tab_data_fellows")
        with t2:
            f_phase = st.multiselect("Phase", options=sorted(filtered["phase"].unique()), key="tab_data_phase")
        with t3:
            f_risks = st.multiselect("Risk Level", options=['🚨 High Risk','⚠️ At Risk','⚡ Moderate','✅ Thriving'], key="tab_data_risk")

        tbl = filtered.copy()
        if f_fellows: tbl = tbl[tbl["name_of_client"].isin(f_fellows)]
        if f_phase:   tbl = tbl[tbl["phase"].isin(f_phase)]
        tbl["overall_score"] = tbl[ALL_ITEMS].mean(axis=1)
        tbl["risk_level"] = tbl["overall_score"].apply(risk_bucket)
        if f_risks: tbl = tbl[tbl["risk_level"].isin(f_risks)]

        view = tbl[[
            "name_of_client","term","date_of_survey","phase","fellowship_year","name_of_facilitator","category",
            "overall_score","doing_well","trying_but_struggling","stuck","risk_level"
        ]].rename(columns={
            "name_of_client":"Fellow","term":"Term","date_of_survey":"Date","phase":"Phase",
            "fellowship_year":"Year","name_of_facilitator":"Facilitator","category":"Category",
            "overall_score":"Overall Score","doing_well":"Confident","trying_but_struggling":"Coping",
            "stuck":"Struggling","risk_level":"Risk Level"
        }).sort_values("Date", ascending=False)

        view["Overall Score"] = view["Overall Score"].map(lambda x: f"{x:.2f}")

        st.dataframe(view, use_container_width=True, height=440, hide_index=True)
        st.caption(f"Showing **{len(view)}** of **{len(filtered)}** survey rows")

        csv = view.to_csv(index=False)
        st.download_button(
            "📥 Export CSV",
            data=csv,
            file_name=f"wellbeing_surveys_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            use_container_width=True,
        )

st.divider()
st.caption("🌱 Fellow Wellbeing Survey Dashboard • Streamlit • Term-focused (Overall first)")
