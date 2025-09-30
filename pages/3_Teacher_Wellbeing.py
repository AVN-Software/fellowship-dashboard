# fellow_wellbeing_dashboard.py
# ---------------------------------------------------------------
# Fellow Wellbeing Dashboard (Term-focused)
# - Primary lens: Overall wellbeing per term (Term 1, Term 2)
# - Filters: Term • Phase • Year of Fellowship • Facilitator
# - Tabs: Overview • Progression • Domains • Indicators • At-Risk • Fellows • Data
# ---------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
import sys

# --- make repo root importable ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# --- import filters and DB manager ---
import components.filters as fx

try:
    from utils.supabase.database_manager import DatabaseManager
except Exception as e:
    DatabaseManager = None
    st.warning(f"DatabaseManager import failed ({e}). Using sample data.")

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
TERMS = ["Term 1", "Term 2"]
SCORE_MIN, SCORE_MAX = 1, 3

COLORS = {
    "terms": {"Term 1": "#4E79A7", "Term 2": "#59A14F"},
    "years": {"Year 1": "#4E79A7", "Year 2": "#59A14F"},
    "traffic": {"bad": "#E15759", "warn": "#F1CE63", "good": "#59A14F", "neutral": "#4E79A7"},
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

# =========================
# Risk Functions
# =========================
def risk_bucket(score: float) -> str:
    if np.isnan(score): return "—"
    if score < 1.8: return "🚨 High Risk"
    if score < 2.2: return "⚠️ At Risk"
    if score < 2.6: return "⚡ Moderate"
    return "✅ Thriving"

def risk_color(score: float) -> str:
    if np.isnan(score): return COLORS["traffic"]["neutral"]
    if score < 1.8: return COLORS["traffic"]["bad"]
    if score < 2.2: return COLORS["traffic"]["warn"]
    if score < 2.6: return "#F1E5A9"
    return COLORS["traffic"]["good"]

# =========================
# Utilities
# =========================
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

# =========================
# Data Fetch
# =========================
@st.cache_data
def load_wellbeing_data():
    if DatabaseManager:
        db = DatabaseManager()
        df = db.get_teacher_wellbeing()
        return df
    else:
        # Fallback sample data
        st.info("Using sample data (DatabaseManager not available)")
        n = 100
        data = {
            "name_of_client": [f"Fellow_{i%20}" for i in range(n)],
            "term": np.random.choice(TERMS, n),
            "date_of_survey": pd.date_range("2024-01-01", periods=n, freq="3D"),
            "phase": np.random.choice(["Foundation", "Intermediate", "Senior"], n),
            "fellowship_year": np.random.choice([1, 2], n),
            "name_of_facilitator": np.random.choice(["Facilitator A", "Facilitator B", "Facilitator C"], n),
            "category": np.random.choice(["Cat1", "Cat2"], n),
        }
        # Add all 63 indicators with random scores 1-3
        for item in ALL_ITEMS:
            data[item] = np.random.choice([1, 2, 3], n)
        
        # Add count columns
        df = pd.DataFrame(data)
        df["doing_well"] = (df[ALL_ITEMS] == 3).sum(axis=1)
        df["trying_but_struggling"] = (df[ALL_ITEMS] == 2).sum(axis=1)
        df["stuck"] = (df[ALL_ITEMS] == 1).sum(axis=1)
        return df

df_surveys = load_wellbeing_data()

# =========================
# Header & Filters
# =========================
fx.topbar(
    "🌱 Fellow Wellbeing Survey",
    "Tracking holistic wellbeing per term with progression by Phase and Year of Fellowship"
)

# Use the wellbeing-specific filters in SIDEBAR
filters = fx.write_wellbeing_filters(df_surveys, TERMS, target=st.sidebar)

if fx.reset_button("♻️ Reset Filters", key="reset_wb", target=st.sidebar):
    for k in list(st.session_state.keys()):
        if k.startswith("wb_"):
            del st.session_state[k]
    st.rerun()

# =========================
# Apply Filters
# =========================
filtered = df_surveys.copy()

if filters["terms"]:
    filtered = filtered[filtered["term"].isin(filters["terms"])]

if filters["phase"]:
    filtered = filtered[filtered["phase"].isin(filters["phase"])]

if filters["year"] != "Both":
    year_num = 1 if filters["year"] == "Year 1" else 2
    filtered = filtered[filtered["fellowship_year"] == year_num]

if filters["facilitators"]:
    filtered = filtered[filtered["name_of_facilitator"].isin(filters["facilitators"])]

# =========================
# Main Content
# =========================

st.caption("Scoring: 1=Struggling, 2=Coping, 3=Confident • 63 indicators")
st.divider()

# =========================
# Tabs
# =========================
tab_overview, tab_progress, tab_domains, tab_indicators, tab_risk, tab_fellows, tab_data = st.tabs(
    ["📌 Overview", "📈 Progression", "🧭 Domains", "🧩 Indicators", "🚨 At-Risk", "👤 Fellows", "📋 Data"]
)

# -------------------------
# Overview Tab
# -------------------------
with tab_overview:
    st.subheader("Program Snapshot")
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        total_surveys = len(filtered)
        fellows_surveyed = filtered["name_of_client"].nunique()
        ow = overall_score(filtered)

        tot_conf = int(filtered["doing_well"].sum())
        tot_coping = int(filtered["trying_but_struggling"].sum())
        tot_str = int(filtered["stuck"].sum())
        resp_total = tot_conf + tot_coping + tot_str
        p_conf = (tot_conf / resp_total * 100) if resp_total else 0
        p_cop = (tot_coping / resp_total * 100) if resp_total else 0
        p_str = (tot_str / resp_total * 100) if resp_total else 0

        # Term distribution
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
            tmp = filtered.copy()
            tmp["overall_score_row"] = tmp[ALL_ITEMS].mean(axis=1)
            at_risk_count = int((tmp["overall_score_row"] < 2.0).sum())
            st.metric("At-Risk Rows (<2.0)", at_risk_count)

        st.markdown("**Term Distribution — Struggling / Coping / Confident**")
        if not dist_df.empty:
            dist_melt = dist_df.melt(id_vars="Term", var_name="Level", value_name="Percent")
            fig_stack = px.bar(
                dist_melt, x="Term", y="Percent", color="Level",
                title="Distribution by Term", text_auto=".0f",
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
# Progression Tab (IMPROVED)
# Shows distribution shift from Term 1 → Term 2
# Red (Struggling=1), Yellow (Coping=2), Green (Confident=3)
# -------------------------
with tab_progress:
    st.subheader("📈 Wellbeing Progression: Distribution Shift")
    st.caption("Track how confidence levels change from Term 1 to Term 2 across all 63 indicators")
    
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        # Calculate distribution for each term
        progression_data = []
        
        for term in order_terms(filtered["term"].unique()):
            term_data = filtered[filtered["term"] == term]
            
            # Count responses across ALL 63 indicators
            struggling_count = int((term_data[ALL_ITEMS] == 1).sum().sum())
            coping_count = int((term_data[ALL_ITEMS] == 2).sum().sum())
            confident_count = int((term_data[ALL_ITEMS] == 3).sum().sum())
            
            total_responses = struggling_count + coping_count + confident_count
            
            if total_responses > 0:
                progression_data.append({
                    "Term": term,
                    "🔴 Struggling (1)": (struggling_count / total_responses) * 100,
                    "🟡 Coping (2)": (coping_count / total_responses) * 100,
                    "🟢 Confident (3)": (confident_count / total_responses) * 100,
                    "_struggling_count": struggling_count,
                    "_coping_count": coping_count,
                    "_confident_count": confident_count,
                    "_total": total_responses
                })
        
        if len(progression_data) > 0:
            prog_df = pd.DataFrame(progression_data)
            
            # === MAIN VISUALIZATION: Stacked Bar Chart ===
            plot_data = prog_df.melt(
                id_vars=["Term"], 
                value_vars=["🔴 Struggling (1)", "🟡 Coping (2)", "🟢 Confident (3)"],
                var_name="Confidence Level", 
                value_name="Percentage"
            )
            
            color_map = {
                "🔴 Struggling (1)": "#E15759",  # Red
                "🟡 Coping (2)": "#F1CE63",      # Yellow
                "🟢 Confident (3)": "#59A14F"    # Green
            }
            
            fig_progression = px.bar(
                plot_data, 
                x="Term", 
                y="Percentage", 
                color="Confidence Level",
                title="Confidence Distribution: Term 1 → Term 2",
                labels={"Percentage": "Percentage of Responses (%)", "Term": "Term"},
                color_discrete_map=color_map,
                text_auto=".1f",
                category_orders={
                    "Term": TERMS,
                    "Confidence Level": ["🔴 Struggling (1)", "🟡 Coping (2)", "🟢 Confident (3)"]
                }
            )
            
            fig_progression.update_layout(
                height=450,
                barmode="stack",
                yaxis_range=[0, 100],
                xaxis_title="",
                legend_title="Confidence Level",
                font=dict(size=13)
            )
            
            fig_progression.update_traces(
                texttemplate='%{text}%',
                textposition='inside',
                textfont_size=12
            )
            
            st.plotly_chart(fig_progression, use_container_width=True)
            
            # === METRICS: Show the shift ===
            if len(prog_df) >= 2:
                term1_data = prog_df.iloc[0]
                term2_data = prog_df.iloc[-1]
                
                st.markdown("### 📊 Change from Term 1 to Term 2")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    struggling_change = term2_data["🔴 Struggling (1)"] - term1_data["🔴 Struggling (1)"]
                    st.metric(
                        "🔴 Struggling",
                        f"{term2_data['🔴 Struggling (1)']:.1f}%",
                        delta=f"{struggling_change:+.1f}%",
                        delta_color="inverse"  # Red is bad, so inverse the color
                    )
                    st.caption(f"Term 1: {term1_data['🔴 Struggling (1)']:.1f}%")
                
                with col2:
                    coping_change = term2_data["🟡 Coping (2)"] - term1_data["🟡 Coping (2)"]
                    st.metric(
                        "🟡 Coping",
                        f"{term2_data['🟡 Coping (2)']:.1f}%",
                        delta=f"{coping_change:+.1f}%",
                        delta_color="off"  # Neutral
                    )
                    st.caption(f"Term 1: {term1_data['🟡 Coping (2)']:.1f}%")
                
                with col3:
                    confident_change = term2_data["🟢 Confident (3)"] - term1_data["🟢 Confident (3)"]
                    st.metric(
                        "🟢 Confident",
                        f"{term2_data['🟢 Confident (3)']:.1f}%",
                        delta=f"{confident_change:+.1f}%",
                        delta_color="normal"  # Green is good
                    )
                    st.caption(f"Term 1: {term1_data['🟢 Confident (3)']:.1f}%")
                
                st.divider()
                
                # === INSIGHT MESSAGE ===
                if confident_change > 5:
                    st.success(
                        f"✅ **Positive Growth!** Confidence increased by **{confident_change:.1f}%** from Term 1 to Term 2. "
                        f"Fellows are gaining confidence across the 63 wellbeing indicators."
                    )
                elif confident_change < -5:
                    st.warning(
                        f"⚠️ **Attention Needed:** Confidence decreased by **{abs(confident_change):.1f}%** from Term 1 to Term 2. "
                        f"Consider targeted interventions."
                    )
                else:
                    st.info(
                        f"📊 **Stable Progression:** Confidence levels remained relatively stable (change: {confident_change:+.1f}%). "
                        f"Continue monitoring trends."
                    )
                
                # === RAW COUNTS TABLE ===
                with st.expander("📋 View Raw Counts"):
                    summary_table = prog_df[[
                        "Term", 
                        "_struggling_count", 
                        "_coping_count", 
                        "_confident_count", 
                        "_total"
                    ]].rename(columns={
                        "_struggling_count": "Struggling Responses",
                        "_coping_count": "Coping Responses",
                        "_confident_count": "Confident Responses",
                        "_total": "Total Responses"
                    })
                    
                    st.dataframe(summary_table, use_container_width=True, hide_index=True)
            
            # === OPTIONAL: Split by Fellowship Year or Phase ===
            st.divider()
            st.markdown("### 🔍 Breakdown by Subgroup")
            
            split_option = st.radio(
                "Split progression by:",
                ["None", "Fellowship Year", "School Phase"],
                horizontal=True,
                key="progression_split"
            )
            
            if split_option != "None":
                split_field = "fellowship_year" if split_option == "Fellowship Year" else "phase"
                
                split_data = []
                for term in order_terms(filtered["term"].unique()):
                    term_subset = filtered[filtered["term"] == term]
                    
                    for group in term_subset[split_field].unique():
                        group_data = term_subset[term_subset[split_field] == group]
                        
                        struggling = int((group_data[ALL_ITEMS] == 1).sum().sum())
                        coping = int((group_data[ALL_ITEMS] == 2).sum().sum())
                        confident = int((group_data[ALL_ITEMS] == 3).sum().sum())
                        total = struggling + coping + confident
                        
                        if total > 0:
                            split_data.append({
                                "Term": term,
                                "Group": f"Year {int(group)}" if split_field == "fellowship_year" else group,
                                "🔴 Struggling": (struggling / total) * 100,
                                "🟡 Coping": (coping / total) * 100,
                                "🟢 Confident": (confident / total) * 100,
                            })
                
                if len(split_data) > 0:
                    split_df = pd.DataFrame(split_data)
                    split_melt = split_df.melt(
                        id_vars=["Term", "Group"],
                        value_vars=["🔴 Struggling", "🟡 Coping", "🟢 Confident"],
                        var_name="Level",
                        value_name="Percentage"
                    )
                    
                    fig_split = px.bar(
                        split_melt,
                        x="Term",
                        y="Percentage",
                        color="Level",
                        facet_col="Group",
                        title=f"Progression by {split_option}",
                        color_discrete_map={
                            "🔴 Struggling": "#E15759",
                            "🟡 Coping": "#F1CE63",
                            "🟢 Confident": "#59A14F"
                        },
                        text_auto=".0f",
                        category_orders={"Term": TERMS}
                    )
                    
                    fig_split.update_layout(
                        height=400,
                        barmode="stack",
                        yaxis_range=[0, 100]
                    )
                    
                    st.plotly_chart(fig_split, use_container_width=True)
        
        else:
            st.warning("Not enough data to show progression across terms.")
# -------------------------
# Domains Tab
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
                fill='toself', name='Wellbeing',
                line=dict(color=COLORS["traffic"]["good"], width=2),
                fillcolor='rgba(89,161,79,0.25)'
            ))
            fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[SCORE_MIN,SCORE_MAX])), 
                            showlegend=False, height=480, title="Domain Scores")
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
# Indicators Tab
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
            color="Avg Score", color_continuous_scale=COLORS["gradient"], 
            range_color=[SCORE_MIN,SCORE_MAX], text="Avg Score"
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
# At-Risk Tab
# -------------------------
with tab_risk:
    st.subheader("🚨 At-Risk Analysis")
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        tmp = filtered.copy()
        tmp["overall_score"] = tmp[ALL_ITEMS].mean(axis=1)
        tmp["risk_level"] = tmp["overall_score"].apply(risk_bucket)
        
        # Risk distribution
        risk_counts = tmp["risk_level"].value_counts()
        fig_risk = px.pie(values=risk_counts.values, names=risk_counts.index, 
                         title="Risk Level Distribution",
                         color_discrete_sequence=COLORS["gradient"])
        st.plotly_chart(fig_risk, use_container_width=True)
        
        # High risk fellows
        high_risk = tmp[tmp["overall_score"] < 1.8].sort_values("overall_score")
        if len(high_risk) > 0:
            st.error(f"**{len(high_risk)} surveys in High Risk (<1.8)**")
            display_cols = ["name_of_client", "term", "phase", "fellowship_year", "overall_score", "risk_level"]
            st.dataframe(high_risk[display_cols], use_container_width=True, hide_index=True)
        else:
            st.success("✅ No surveys in High Risk category")

# -------------------------
# Fellows Tab
# -------------------------
with tab_fellows:
    st.subheader("👤 Individual Fellow Analysis")
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        fellow_list = sorted(filtered["name_of_client"].unique())
        selected_fellow = st.selectbox("Select Fellow", options=fellow_list, key="fellow_select")
        
        fellow_data = filtered[filtered["name_of_client"] == selected_fellow]
        
        if len(fellow_data) > 0:
            # Overall metrics
            fellow_avg = fellow_data[ALL_ITEMS].values.flatten().mean()
            c1, c2, c3 = st.columns(3)
            with c1: st.metric("Survey Count", len(fellow_data))
            with c2: st.metric("Average Score", f"{fellow_avg:.2f}")
            with c3: st.metric("Risk Level", risk_bucket(fellow_avg))
            
            # Progression
            if len(fellow_data) > 1:
                fellow_prog = fellow_data.copy()
                fellow_prog["overall_score"] = fellow_prog[ALL_ITEMS].mean(axis=1)
                fellow_prog = fellow_prog.sort_values("date_of_survey")
                
                fig_fellow = px.line(fellow_prog, x="date_of_survey", y="overall_score",
                                   markers=True, title=f"{selected_fellow} - Wellbeing Progression")
                fig_fellow.update_layout(yaxis_range=[SCORE_MIN, SCORE_MAX])
                st.plotly_chart(fig_fellow, use_container_width=True)
            
            # Domain scores
            fellow_domains = dimension_scores(fellow_data)
            fellow_dim_df = pd.DataFrame([{"Domain": k, "Score": v} for k, v in fellow_domains.items()])
            fig_fellow_bar = px.bar(fellow_dim_df, x="Score", y="Domain", orientation="h",
                                   title=f"{selected_fellow} - Domain Scores",
                                   color="Score", color_continuous_scale=COLORS["gradient"])
            st.plotly_chart(fig_fellow_bar, use_container_width=True)

# -------------------------
# Data Tab
# -------------------------
with tab_data:
    st.subheader("📋 Full Survey Data")
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
    else:
        t1, t2, t3 = st.columns(3)
        with t1:
            f_fellows = st.multiselect("Fellows", options=sorted(filtered["name_of_client"].unique()), key="tab_data_fellows")
        with t2:
            f_phase = st.multiselect("Phase", options=sorted(filtered["phase"].unique()), key="tab_data_phase")
        with t3:
            f_risks = st.multiselect("Risk Level", 
                                    options=['🚨 High Risk','⚠️ At Risk','⚡ Moderate','✅ Thriving'], 
                                    key="tab_data_risk")

        tbl = filtered.copy()
        if f_fellows: tbl = tbl[tbl["name_of_client"].isin(f_fellows)]
        if f_phase: tbl = tbl[tbl["phase"].isin(f_phase)]
        
        tbl["overall_score"] = tbl[ALL_ITEMS].mean(axis=1)
        tbl["risk_level"] = tbl["overall_score"].apply(risk_bucket)
        if f_risks: tbl = tbl[tbl["risk_level"].isin(f_risks)]

        view = tbl[[
            "name_of_client","term","date_of_survey","phase","fellowship_year","name_of_facilitator",
            "overall_score","doing_well","trying_but_struggling","stuck","risk_level"
        ]].rename(columns={
            "name_of_client":"Fellow","term":"Term","date_of_survey":"Date","phase":"Phase",
            "fellowship_year":"Year","name_of_facilitator":"Facilitator",
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