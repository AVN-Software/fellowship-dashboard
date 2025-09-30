# dash/fellow_wellbeing/tabs/fellows.py
import streamlit as st
import pandas as pd
import plotly.express as px

def _dimension_scores(df: pd.DataFrame, DIMENSIONS) -> dict:
    import numpy as np
    out = {}
    for dim, items in DIMENSIONS.items():
        vals = df[items].values.flatten()
        out[dim] = float(np.mean(vals)) if len(vals) else float("nan")
    return out

def render(filtered: pd.DataFrame, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX, risk_bucket):
    st.subheader("👤 Individual Fellow Analysis")
    if filtered.empty:
        st.warning("No data available for selected filters.")
        return

    fellow_list = sorted(filtered["name_of_client"].unique())
    selected_fellow = st.selectbox("Select Fellow", options=fellow_list, key="fellow_select")
    fellow_data = filtered[filtered["name_of_client"] == selected_fellow]

    if fellow_data.empty:
        st.info("No surveys for the selected fellow.")
        return

    fellow_avg = fellow_data[DIMENSIONS[next(iter(DIMENSIONS))] + sum([v for v in list(DIMENSIONS.values())[1:]], [])].values.flatten().mean()
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Survey Count", len(fellow_data))
    with c2: st.metric("Average Score", f"{fellow_avg:.2f}")
    with c3: st.metric("Risk Level", risk_bucket(fellow_avg))

    if len(fellow_data) > 1:
        fd = fellow_data.copy()
        all_items = [i for items in DIMENSIONS.values() for i in items]
        fd["overall_score"] = fd[all_items].mean(axis=1)
        fd = fd.sort_values("date_of_survey")
        fig_fellow = px.line(fd, x="date_of_survey", y="overall_score",
                             markers=True, title=f"{selected_fellow} - Wellbeing Progression")
        fig_fellow.update_layout(yaxis_range=[SCORE_MIN, SCORE_MAX])
        st.plotly_chart(fig_fellow, use_container_width=True)

    fellow_domains = _dimension_scores(fellow_data, DIMENSIONS)
    fellow_dim_df = pd.DataFrame([{"Domain": k, "Score": v} for k, v in fellow_domains.items()])
    fig_fellow_bar = px.bar(
        fellow_dim_df, x="Score", y="Domain", orientation="h",
        title=f"{selected_fellow} - Domain Scores",
        color="Score", color_continuous_scale=COLORS["gradient"]
    )
    st.plotly_chart(fig_fellow_bar, use_container_width=True)
