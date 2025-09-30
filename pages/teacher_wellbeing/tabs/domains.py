# dash/fellow_wellbeing/tabs/domains.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# ---------------------------------------
# Helpers
# ---------------------------------------
def _pretty(df: pd.DataFrame, col: str, fmt="{:.2f}"):
    if col in df.columns:
        df[col] = df[col].map(lambda x: "" if pd.isna(x) else fmt.format(x))
    return df

def _terms_present(df: pd.DataFrame) -> list:
    if "term" not in df.columns:
        return []
    return list(df["term"].dropna().unique())

def _order_terms(terms: list) -> list:
    order = {"Term 1": 0, "Term 2": 1, "Term 3": 2}
    return sorted(terms, key=lambda t: order.get(t, 999))

def _dimension_scores(df: pd.DataFrame, DIMENSIONS: dict) -> dict:
    out = {}
    for dim, items in DIMENSIONS.items():
        cols = [c for c in items if c in df.columns]
        if not cols:
            out[dim] = np.nan
            continue
        vals = df[cols].to_numpy().astype(float).flatten()
        vals = vals[~np.isnan(vals)]
        out[dim] = float(np.mean(vals)) if len(vals) else np.nan
    return out

def _dim_scores_by_term(df: pd.DataFrame, DIMENSIONS: dict) -> pd.DataFrame:
    """Returns long dataframe: Domain, term, Score."""
    if "term" not in df.columns or df.empty:
        return pd.DataFrame(columns=["Domain", "term", "Score"])
    rows = []
    for t, sub in df.groupby("term"):
        scores = _dimension_scores(sub, DIMENSIONS)
        for d, s in scores.items():
            rows.append({"Domain": d, "term": t, "Score": s})
    out = pd.DataFrame(rows)
    return out

def _delta_table(by_term_df: pd.DataFrame, base="Term 1", second="Term 2"):
    """Wide pivot with Delta and Direction."""
    if by_term_df.empty:
        return pd.DataFrame()
    wide = by_term_df.pivot_table(index="Domain", columns="term", values="Score", aggfunc="mean")
    for t in [base, second]:
        if t not in wide.columns:
            wide[t] = np.nan
    wide["Delta (Second–Base)"] = wide[second] - wide[base]
    def dir_glyph(x):
        if pd.isna(x): return "▬"
        return "▲" if x > 1e-9 else ("▼" if x < -1e-9 else "▬")
    wide["Direction"] = wide["Delta (Second–Base)"].map(dir_glyph)
    wide = wide.reset_index()
    return wide

# ---------------------------------------
# Main render
# ---------------------------------------
def render(filtered: pd.DataFrame, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX):
    st.subheader("Wellbeing by Domain (comparative)")

    if filtered.empty:
        st.warning("No data available for selected filters.")
        return

    # Compute scores
    by_term = _dim_scores_by_term(filtered, DIMENSIONS)
    if by_term.empty:
        st.warning("No indicators available for domains in the filtered data.")
        return

    terms = _order_terms(_terms_present(filtered))
    base_term  = terms[0] if len(terms) > 0 else None
    second_term = terms[1] if len(terms) > 1 else None

    # --- Controls ---
    c1, c2, c3 = st.columns([1,1,1])
    with c1:
        chart_type = st.radio("Chart", ["Grouped Bars", "Lines", "Radar"], key="dom_chart", horizontal=True)
    with c2:
        sel_terms = st.multiselect("Terms", options=terms, default=terms, key="dom_terms")
        if not sel_terms:
            st.info("Select at least one term to plot.")
            return
    with c3:
        sort_by = st.selectbox("Sort Domains", ["By Base Score", "By Second Score", "Alphabetical"], index=0)

    plot_df = by_term[by_term["term"].isin(sel_terms)].copy()
    # Domain order
    wide_for_order = plot_df.pivot_table(index="Domain", columns="term", values="Score", aggfunc="mean")
    if base_term in wide_for_order.columns and second_term in wide_for_order.columns:
        if sort_by == "By Base Score":
            domain_order = wide_for_order[base_term].sort_values().index.tolist()
        elif sort_by == "By Second Score":
            domain_order = wide_for_order[second_term].sort_values().index.tolist()
        else:
            domain_order = sorted(wide_for_order.index.tolist())
    else:
        domain_order = sorted(wide_for_order.index.tolist())
    plot_df["Domain"] = pd.Categorical(plot_df["Domain"], categories=domain_order, ordered=True)

    # --- Chart ---
    if chart_type == "Grouped Bars":
        fig = px.bar(
            plot_df,
            x="Score", y="Domain", color="term",
            barmode="group", orientation="h",
            color_discrete_map=COLORS.get("terms", {}),
            labels={"Score":"Average Score","Domain":"Domain","term":"Term"},
            title="Domain Scores by Term"
        )
        fig.update_layout(xaxis_range=[SCORE_MIN, SCORE_MAX], height=max(480, 36*len(domain_order)))
        st.plotly_chart(fig, use_container_width=True)

    elif chart_type == "Lines":
        fig = px.line(
            plot_df.sort_values(["Domain","term"]),
            x="term", y="Score", color="Domain", markers=True,
            labels={"Score":"Average Score","term":"Term","Domain":"Domain"},
            title="Domain Trajectories by Term"
        )
        fig.update_layout(yaxis_range=[SCORE_MIN, SCORE_MAX], legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
        st.plotly_chart(fig, use_container_width=True)

    else:  # Radar
        # One trace per term
        # Keep a stable domain order (by base score if present)
        categories = domain_order
        fig = go.Figure()
        for t in sel_terms:
            series = by_term[by_term["term"] == t].set_index("Domain").reindex(categories)["Score"].tolist()
            fig.add_trace(go.Scatterpolar(
                r=series, theta=categories, fill='toself', name=t
            ))
        fig.update_layout(
            title="Radar — Domain Scores by Term",
            polar=dict(radialaxis=dict(visible=True, range=[SCORE_MIN, SCORE_MAX])),
            showlegend=True, height=520
        )
        st.plotly_chart(fig, use_container_width=True)

    # --- Delta table (only if we have at least two terms overall) ---
    st.markdown("### Change Table (Second − Base)")
    if base_term and second_term:
        delta = _delta_table(by_term, base=base_term, second=second_term)
        show = delta.rename(columns={
            base_term: f"{base_term} Score",
            second_term: f"{second_term} Score"
        }).copy()
        show = _pretty(show, f"{base_term} Score")
        show = _pretty(show, f"{second_term} Score")
        show = _pretty(show, "Delta (Second–Base)")
        st.dataframe(show[["Domain", f"{base_term} Score", f"{second_term} Score", "Delta (Second–Base)", "Direction"]],
                     use_container_width=True, hide_index=True)
    else:
        st.info("Provide at least two terms to compute change.")

    # --- Insights ---
    st.markdown("### Insights")
    if base_term and second_term:
        # Score thresholds
        THRIVING = 2.6
        AT_RISK = 2.0

        # Top movers
        movers = delta.dropna(subset=["Delta (Second–Base)"]).sort_values("Delta (Second–Base)", ascending=False)
        improvers = movers.head(3)
        decliners = movers.tail(3)

        # Current term (second) health
        latest_scores = by_term[by_term["term"] == second_term].dropna(subset=["Score"])
        thriving = latest_scores[latest_scores["Score"] >= THRIVING]["Domain"].tolist()
        at_risk = latest_scores[latest_scores["Score"] < AT_RISK]["Domain"].tolist()

        c1, c2 = st.columns(2)
        with c1:
            st.success("**Top Improvements (Second − Base)**")
            if improvers.empty:
                st.caption("• No improvements to highlight.")
            else:
                for _, r in improvers.iterrows():
                    st.caption(f"• {r['Domain']}: +{r['Delta (Second–Base)']:.2f}")

            st.info("**Thriving Domains (Second ≥ 2.6)**")
            st.caption("• " + (", ".join(thriving) if thriving else "None"))

        with c2:
            st.warning("**Largest Declines (Second − Base)**")
            if decliners.empty:
                st.caption("• No declines to highlight.")
            else:
                for _, r in decliners.iterrows():
                    st.caption(f"• {r['Domain']}: {r['Delta (Second–Base)']:.2f}")

            st.error("**At-Risk Domains (Second < 2.0)**")
            st.caption("• " + (", ".join(at_risk) if at_risk else "None"))

    else:
        st.caption("Provide at least two terms to unlock comparative insights.")
