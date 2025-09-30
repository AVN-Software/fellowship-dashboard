# dash/fellow_wellbeing/tabs/progression.py
import streamlit as st
import pandas as pd
import plotly.express as px

def _order_terms(values, TERMS):
    order = {t: i for i, t in enumerate(TERMS)}
    return sorted(values, key=lambda t: order.get(t, 999))

def render(filtered: pd.DataFrame, ALL_ITEMS, TERMS):
    st.subheader("📈 Wellbeing Progression: Distribution Shift")
    st.caption("Track how confidence levels change from Term 1 to Term 2 across all 63 indicators")

    if filtered.empty:
        st.warning("No data available for selected filters.")
        return

    progression_data = []
    for term in _order_terms(filtered["term"].unique(), TERMS):
        term_data = filtered[filtered["term"] == term]
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

    if not progression_data:
        st.warning("Not enough data to show progression across terms.")
        return

    prog_df = pd.DataFrame(progression_data)
    plot_data = prog_df.melt(
        id_vars=["Term"],
        value_vars=["🔴 Struggling (1)", "🟡 Coping (2)", "🟢 Confident (3)"],
        var_name="Confidence Level",
        value_name="Percentage"
    )

    color_map = {
        "🔴 Struggling (1)": "#E15759",
        "🟡 Coping (2)": "#F1CE63",
        "🟢 Confident (3)": "#59A14F"
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
        category_orders={"Term": TERMS}
    )
    fig_progression.update_layout(
        height=450,
        barmode="stack",
        yaxis_range=[0, 100],
        xaxis_title="",
        legend_title="Confidence Level",
        font=dict(size=13)
    )
    fig_progression.update_traces(texttemplate='%{text}%', textposition='inside', textfont_size=12)
    st.plotly_chart(fig_progression, use_container_width=True)

    if len(prog_df) >= 2:
        term1_data = prog_df.iloc[0]
        term2_data = prog_df.iloc[-1]
        st.markdown("### 📊 Change from Term 1 to Term 2")
        c1, c2, c3 = st.columns(3)
        with c1:
            delta = term2_data["🔴 Struggling (1)"] - term1_data["🔴 Struggling (1)"]
            st.metric("🔴 Struggling", f"{term2_data['🔴 Struggling (1)']:.1f}%", f"{delta:+.1f}%", delta_color="inverse")
            st.caption(f"Term 1: {term1_data['🔴 Struggling (1)']:.1f}%")
        with c2:
            delta = term2_data["🟡 Coping (2)"] - term1_data["🟡 Coping (2)"]
            st.metric("🟡 Coping", f"{term2_data['🟡 Coping (2)']:.1f}%", f"{delta:+.1f}%", delta_color="off")
            st.caption(f"Term 1: {term1_data['🟡 Coping (2)']:.1f}%")
        with c3:
            delta = term2_data["🟢 Confident (3)"] - term1_data["🟢 Confident (3)"]
            st.metric("🟢 Confident", f"{term2_data['🟢 Confident (3)']:.1f}%", f"{delta:+.1f}%", delta_color="normal")
            st.caption(f"Term 1: {term1_data['🟢 Confident (3)']:.1f}%")

    st.divider()
    st.markdown("### 🔍 Breakdown by Subgroup")
    split_option = st.radio(
        "Split progression by:",
        ["None", "Fellowship Year", "School Phase"],
        horizontal=True,
        key="progression_split"
    )
    if split_option == "None":
        return

    split_field = "fellowship_year" if split_option == "Fellowship Year" else "phase"
    split_data = []
    for term in _order_terms(filtered["term"].unique(), TERMS):
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

    if split_data:
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
        fig_split.update_layout(height=400, barmode="stack", yaxis_range=[0, 100])
        st.plotly_chart(fig_split, use_container_width=True)
