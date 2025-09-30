import streamlit as st
import pandas as pd
import numpy as np

try:
    import altair as alt
    ALT_AVAILABLE = True
except Exception:
    ALT_AVAILABLE = False

# ---------- Utility functions ----------
def fmt_pct(x, places=1):
    if pd.isna(x):
        return "-"
    return f"{x:.{places}f}%"

def fmt_dec(x, places=2):
    if pd.isna(x):
        return "-"
    return f"{x:.{places}f}"

def wmean(series, weights):
    s = pd.to_numeric(series, errors="coerce")
    w = pd.to_numeric(weights, errors="coerce").fillna(0)
    denom = w.sum()
    return float((s.fillna(0) * w).sum() / denom) if denom > 0 else np.nan

def pct(n, d):
    return float(n) / float(d) if d else np.nan


# ---------- Charts ----------
def chart_overall_impact(filtered, avg_t1_w, avg_t2_w, avg_improv_w,
                        pass_t1_count, pass_t2_count, pass_t1_rate, pass_t2_rate,
                        learners, classes):
    """Section 1: Headline impact metrics"""
    st.markdown("## 📊 Overall Impact at a Glance")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Learners Reached", f"{learners:,}")
        st.metric("Classes Supported", f"{classes}")

    with col2:
        st.metric(
            "Average Academic Improvement",
            fmt_dec(avg_improv_w),
            delta=f"{fmt_pct((avg_t2_w-avg_t1_w)/avg_t1_w*100, 0)} growth"
                  if not pd.isna(avg_improv_w) and avg_t1_w else None,
        )

    with col3:
        st.metric("Term 1 Performance", fmt_pct(avg_t1_w*100, 0) if avg_t1_w else "-")
        st.metric(
            "Term 2 Performance",
            fmt_pct(avg_t2_w*100, 0) if avg_t2_w else "-",
            delta=fmt_pct((avg_t2_w-avg_t1_w)*100, 0) if not pd.isna(avg_improv_w) else None,
        )

    with col4:
        pass_improvement = pass_t2_count - pass_t1_count
        st.metric("Classes Passing (Term 2)", f"{pass_t2_count}/{classes}",
                  delta=f"{pass_improvement:+} classes")
        st.metric("Pass Rate", fmt_pct(pass_t2_rate*100, 1))

    if not pd.isna(avg_improv_w):
        st.info(f"📈 **Impact Summary:** {classes} classes, {learners:,} learners, "
                f"average improvement {fmt_dec(avg_improv_w)}")


def chart_cohort_progression(filtered):
    """Section 2: Cohort progression"""
    st.markdown("## 🚀 Year-over-Year Progression")
    if filtered.empty:
        st.info("No data available")
        return

    by_year = (
        filtered.groupby("fellowship_year")
        .apply(lambda g: pd.Series({
            "Term 1": wmean(g["term_1"], g["class_size"]),
            "Term 2": wmean(g["term_2"], g["class_size"]),
        }))
        .reset_index()
    )

    if ALT_AVAILABLE:
        chart = (
            alt.Chart(by_year)
            .mark_bar()
            .encode(
                x="fellowship_year:N",
                y=alt.Y("Term 2:Q", scale=alt.Scale(domain=[0, 1])),
                color="fellowship_year:N",
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.dataframe(by_year)


def chart_subject_performance(filtered):
    """Section 3: Subject performance"""
    st.markdown("## 📚 Performance by Subject")
    if filtered.empty:
        st.info("No data available")
        return

    by_subject = (
        filtered.groupby("subject")
        .apply(lambda g: pd.Series({
            "Term 1": wmean(g["term_1"], g["class_size"]),
            "Term 2": wmean(g["term_2"], g["class_size"]),
        }))
        .reset_index()
    )

    if ALT_AVAILABLE:
        melted = by_subject.melt(id_vars="subject", value_vars=["Term 1", "Term 2"])
        chart = (
            alt.Chart(melted)
            .mark_bar()
            .encode(
                x="subject:N", y="value:Q", color="variable:N",
                tooltip=["subject", "variable", "value"]
            )
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.dataframe(by_subject)


def chart_phase_performance(filtered):
    """Section 4: Phase performance"""
    st.markdown("## 🎯 Performance by Education Phase")
    if filtered.empty:
        st.info("No data available")
        return

    by_phase = (
        filtered.groupby("Phase")
        .apply(lambda g: pd.Series({
            "Term 1": wmean(g["term_1"], g["class_size"]),
            "Term 2": wmean(g["term_2"], g["class_size"]),
        }))
        .reset_index()
    )

    if ALT_AVAILABLE:
        chart = (
            alt.Chart(by_phase)
            .mark_bar()
            .encode(x="Phase:N", y="Term 2:Q", tooltip=["Phase", "Term 1", "Term 2"])
        )
        st.altair_chart(chart, use_container_width=True)
    else:
        st.dataframe(by_phase)
