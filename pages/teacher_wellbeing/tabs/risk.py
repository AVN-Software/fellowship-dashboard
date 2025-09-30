# dash/fellow_wellbeing/tabs/risk.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render(filtered: pd.DataFrame, ALL_ITEMS, COLORS, risk_bucket):
    st.subheader("🚨 At-Risk Analysis")
    if filtered.empty:
        st.warning("No data available for selected filters.")
        return

    tmp = filtered.copy()
    tmp["overall_score"] = tmp[ALL_ITEMS].mean(axis=1)
    tmp["risk_level"] = tmp["overall_score"].apply(risk_bucket)

    risk_counts = tmp["risk_level"].value_counts()
    fig_risk = px.pie(
        values=risk_counts.values,
        names=risk_counts.index,
        title="Risk Level Distribution",
        color_discrete_sequence=COLORS["gradient"]
    )
    st.plotly_chart(fig_risk, use_container_width=True)

    high_risk = tmp[tmp["overall_score"] < 1.8].sort_values("overall_score")
    if len(high_risk) > 0:
        st.error(f"**{len(high_risk)} surveys in High Risk (<1.8)**")
        display_cols = ["name_of_client", "term", "phase", "fellowship_year", "overall_score", "risk_level"]
        st.dataframe(high_risk[display_cols], use_container_width=True, hide_index=True)
    else:
        st.success("✅ No surveys in High Risk category")
