# dash/fellow_wellbeing/tabs/indicators.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# -----------------------------
# Helpers (shared)
# -----------------------------
def _pct_bucket(series: pd.Series, bucket_value: int) -> float:
    n = series.notna().sum()
    return (float((series == bucket_value).sum()) / n * 100.0) if n else 0.0

def _pretty_label(key: str) -> str:
    return key.replace("_", " ").title()

def _term_pair(filtered: pd.DataFrame):
    """Infer Baseline/Second terms safely; defaults to first two alphabetical."""
    if "term" not in filtered.columns:
        return None, None
    terms = sorted(t for t in filtered["term"].dropna().unique())
    if len(terms) >= 2:
        return terms[0], terms[1]
    elif len(terms) == 1:
        return terms[0], None
    return None, None

# -----------------------------
# Section 1: Drilldown (kept)
# -----------------------------
def render(filtered: pd.DataFrame, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX):
    st.subheader("Indicator Drilldown (per Domain)")
    if filtered.empty:
        st.warning("No data available for selected filters.")
        return

    sel_dim = st.selectbox("Select Domain", options=list(DIMENSIONS.keys()), key="tab_ind_sel")
    items = DIMENSIONS[sel_dim]

    rows = []
    for it in items:
        if it not in filtered.columns:
            continue
        vals = filtered[it]
        n1 = int((vals == 1).sum()); n2 = int((vals == 2).sum()); n3 = int((vals == 3).sum())
        tot = n1 + n2 + n3
        rows.append({
            "Indicator": _pretty_label(it),
            "Avg Score": float(vals.mean()),
            "% Struggling": (n1/tot*100) if tot else 0.0,
            "% Coping": (n2/tot*100) if tot else 0.0,
            "% Confident": (n3/tot*100) if tot else 0.0,
        })
    idf = pd.DataFrame(rows).sort_values("Avg Score") if rows else pd.DataFrame()

    if idf.empty:
        st.info("No indicators present for this domain in the filtered data.")
        return

    fig = px.bar(
        idf, x="Avg Score", y="Indicator", orientation="h",
        title=f"Indicators — {sel_dim}",
        labels={"Avg Score":"Average Score","Indicator":"Indicator"},
        color="Avg Score", color_continuous_scale=COLORS.get("gradient", ['#E15759','#F28E2B','#F1CE63','#59A14F']),
        range_color=[SCORE_MIN, SCORE_MAX], text="Avg Score"
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

    st.divider()

    # Hand over to comparison section for the SAME selected domain
    render_baseline_second_section(filtered, DIMENSIONS, sel_dim, COLORS)


# -----------------------------
# Section 2: Baseline vs Second
#  - Table (Doing well/Struggling/Stuck)
#  - Chart (Doing well %, Baseline vs Second)
# -----------------------------
def render_baseline_second_section(filtered: pd.DataFrame, DIMENSIONS: dict, sel_dim: str, COLORS: dict):
    st.subheader("Baseline vs Second — Summary Table & Chart")

    term_baseline, term_second = _term_pair(filtered)
    if not term_baseline or not term_second:
        st.info("Need two terms to compare (e.g., Term 1 and Term 2). Adjust filters to include both.")
        return

    # Allow user override (defaults inferred)
    c1, c2, c3 = st.columns([1,1,2])
    with c1:
        t_base = st.selectbox("Baseline term", options=[term_baseline, term_second], index=0, key="wb_base_term")
    with c2:
        t_second = st.selectbox("Second term", options=[term_baseline, term_second], index=1, key="wb_second_term")
    if t_base == t_second:
        st.warning("Baseline and Second are the same term — choose different terms to compare.")
        return

    # Filter frames
    baseline = filtered[filtered["term"] == t_base].copy()
    second   = filtered[filtered["term"] == t_second].copy()

    # Buckets mapping to your headers:
    # 1 = Struggling, 2 = Coping, 3 = Confident → rename to "Doing well / Struggling / Stuck"
    doing_well_bucket, struggling_bucket, stuck_bucket = 3, 1, 2

    items = [it for it in DIMENSIONS.get(sel_dim, []) if it in filtered.columns]
    if not items:
        st.info("No indicators available for the selected domain.")
        return

    # Build table rows
    table_rows = []
    chart_rows = []
    for idx, key in enumerate(items, start=1):
        b = baseline[key].dropna()
        s = second[key].dropna()

        b_dw = _pct_bucket(b, doing_well_bucket); b_str = _pct_bucket(b, struggling_bucket); b_stk = _pct_bucket(b, stuck_bucket)
        s_dw = _pct_bucket(s, doing_well_bucket); s_str = _pct_bucket(s, struggling_bucket); s_stk = _pct_bucket(s, stuck_bucket)

        change = s_dw - b_dw
        direction = "" if change > 1e-9 else ("" if change < -1e-9 else "")

        table_rows.append({
            "Dimension": sel_dim,
            "Indicators": f"{idx}. {_pretty_label(key)}",
            "Matched Baseline — Doing well": f"{b_dw:.0f}%",
            "Matched Baseline — Struggling": f"{b_str:.0f}%",
            "Matched Baseline — Stuck": f"{b_stk:.0f}%",
            "Second — Doing well": f"{s_dw:.0f}%",
            "Second — Struggling": f"{s_str:.0f}%",
            "Second — Stuck": f"{s_stk:.0f}%",
            "Change": f"{change:+.0f}%",
            "Direction": direction,
        })

        # For chart (Doing well % only)
        chart_rows.append({"Indicator": f"{idx}. {_pretty_label(key)}", "Term": t_base,   "Doing well %": b_dw})
        chart_rows.append({"Indicator": f"{idx}. {_pretty_label(key)}", "Term": t_second, "Doing well %": s_dw})

    # Render table
    out = pd.DataFrame(table_rows)
    out = out.sort_values("Indicators", key=lambda s: s.str.extract(r"^(\d+)").astype(float)[0])

    st.dataframe(out, use_container_width=True, hide_index=True)

    # Render chart: grouped bars by term, sorted by change descending
    change_sorter = out.assign(_chg=out["Change"].str.replace("%","").astype(float)).sort_values("_chg", ascending=False)
    order = change_sorter["Indicators"].tolist()

    chart_df = pd.DataFrame(chart_rows)
    chart_df["Indicator"] = pd.Categorical(chart_df["Indicator"], categories=order, ordered=True)

    color_map = COLORS.get("terms", {t_base: "#4E79A7", t_second: "#59A14F"})
    fig = px.bar(
        chart_df,
        x="Doing well %", y="Indicator", color="Term",
        barmode="group", orientation="h",
        color_discrete_map=color_map,
        title=f"Doing well (%) — {sel_dim}: {t_base} vs {t_second}",
        text="Doing well %"
    )
    fig.update_traces(texttemplate='%{text:.0f}%', textposition='outside')
    fig.update_layout(height=max(420, len(items)*38), xaxis_title="Percent", yaxis_title="Indicator")
    st.plotly_chart(fig, use_container_width=True)

    # Tiny legend
    st.caption(f"Direction symbols:  improved •  unchanged •  declined (based on Doing well % change {t_base}→{t_second})")
