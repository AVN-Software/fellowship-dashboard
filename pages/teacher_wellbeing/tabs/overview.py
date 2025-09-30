# dash/fellow_wellbeing/tabs/overview.py
import streamlit as st
import pandas as pd
import plotly.express as px

def render(filtered: pd.DataFrame, ALL_ITEMS, TERMS, COLORS, risk_bucket, order_terms):
    st.subheader("Program Snapshot")
    if filtered.empty:
        st.warning("No data available for selected filters.")
        return

    total_surveys = len(filtered)
    fellows_surveyed = filtered["name_of_client"].nunique()
    ow = float(filtered[ALL_ITEMS].values.flatten().mean())

    tot_conf = int(filtered["doing_well"].sum())
    tot_coping = int(filtered["trying_but_struggling"].sum())
    tot_str = int(filtered["stuck"].sum())
    resp_total = tot_conf + tot_coping + tot_str
    p_conf = (tot_conf / resp_total * 100) if resp_total else 0
    p_cop = (tot_coping / resp_total * 100) if resp_total else 0
    p_str = (tot_str / resp_total * 100) if resp_total else 0

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
