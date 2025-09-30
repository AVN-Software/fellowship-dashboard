import streamlit as st
import pandas as pd
from datetime import datetime
from ..components.utils_wellbeing import risk_bucket, ALL_ITEMS


def render_data_explorer(df: pd.DataFrame):
    """Reusable data explorer section with filters + export."""
    st.subheader("📋 Data Explorer")

    if df.empty:
        st.warning("No data available for selected filters.")
        return

    t1, t2, t3 = st.columns(3)
    with t1:
        f_fellows = st.multiselect("Fellows", options=sorted(df["name_of_client"].unique()))
    with t2:
        f_phase = st.multiselect("Phase", options=sorted(df["phase"].unique()))
    with t3:
        f_risks = st.multiselect("Risk Level", options=['🚨 High Risk','⚠️ At Risk','⚡ Moderate','✅ Thriving'])

    tbl = df.copy()
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
    st.caption(f"Showing **{len(view)}** of **{len(df)}** survey rows")

    csv = view.to_csv(index=False)
    st.download_button(
        "📥 Export CSV",
        data=csv,
        file_name=f"wellbeing_surveys_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
