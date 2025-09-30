import streamlit as st
import pandas as pd
import numpy as np

# Try to use Altair for nicer charts (optional)
try:
    import altair as alt
    ALT_AVAILABLE = True
except Exception:
    ALT_AVAILABLE = False

# -------------------------------
# Helpers
# -------------------------------
def wmean(series, weights):
    s = pd.to_numeric(series, errors="coerce")
    w = pd.to_numeric(weights, errors="coerce").fillna(0)
    denom = w.sum()
    return float((s.fillna(0) * w).sum() / denom) if denom > 0 else np.nan

def pct(n, d):
    return float(n) / float(d) if d else np.nan

def fmt_pct(x, places=1):
    if pd.isna(x): return "-"
    return f"{x*100:.{places}f}%"

def fmt_dec(x, places=2):
    if pd.isna(x): return "-"
    return f"{x:.{places}f}"

def safe_mean(series):
    s = pd.to_numeric(series, errors="coerce")
    return float(s.mean()) if len(s) else np.nan

# -------------------------------
# Page
# -------------------------------
def run():
    st.set_page_config(page_title="Fellowship Impact", layout="wide")
    
    # Header with impact statement
    st.markdown("""
    # 🎓 Fellowship Impact Report
    ### Measuring Academic Growth & Excellence
    """)
    
    # ============================================================
    # Demo data - Replace with Supabase/DB fetch
    # ============================================================
    df = pd.DataFrame([
        {"fellowship_year":"Year 1","subject":"English","Phase":"Foundation","grade":"Grade 2","class_size":32,"term_1":0.46,"term_2":0.61,"has_both_terms":True,"pass_term_1":False,"pass_term_2":True},
        {"fellowship_year":"Year 2","subject":"English","Phase":"Foundation","grade":"Grade 1","class_size":42,"term_1":0.51,"term_2":0.58,"has_both_terms":True,"pass_term_1":True,"pass_term_2":True},
        {"fellowship_year":"Year 2","subject":"Mathematics","Phase":"Intermediate","grade":"Grade 6","class_size":39,"term_1":0.37,"term_2":0.52,"has_both_terms":True,"pass_term_1":False,"pass_term_2":True},
        {"fellowship_year":"Year 1","subject":"Natural Sciences","Phase":"Senior","grade":"Grade 7","class_size":44,"term_1":0.56,"term_2":0.69,"has_both_terms":True,"pass_term_1":True,"pass_term_2":True},
        {"fellowship_year":"Year 1","subject":"Afrikaans","Phase":"Foundation","grade":"Grade R","class_size":31,"term_1":0.55,"term_2":0.57,"has_both_terms":True,"pass_term_1":True,"pass_term_2":True},
        {"fellowship_year":"Year 2","subject":"Mathematics","Phase":"FET","grade":"Grade 11","class_size":99,"term_1":0.45,"term_2":0.56,"has_both_terms":True,"pass_term_1":False,"pass_term_2":True},
    ])

    # Derived fields
    df["term_1"] = pd.to_numeric(df["term_1"], errors="coerce")
    df["term_2"] = pd.to_numeric(df["term_2"], errors="coerce")
    df["class_size"] = pd.to_numeric(df["class_size"], errors="coerce").fillna(0).astype(int)
    df["improvement_raw"] = df["term_2"] - df["term_1"]
    base = df["term_1"].replace(0, np.nan)
    df["improvement_pct"] = (df["term_2"] - df["term_1"]) / base

    # -------------------------------
    # FILTERS - Compact sidebar
    # -------------------------------
    with st.sidebar:
        st.markdown("### 🔎 View Selector")
        f_phase = st.selectbox("Phase", ["All Phases"] + sorted(df["Phase"].dropna().unique().tolist()))
        f_subject = st.selectbox("Subject", ["All Subjects"] + sorted(df["subject"].dropna().unique().tolist()))
        f_grade = st.selectbox("Grade", ["All Grades"] + sorted(df["grade"].dropna().unique().tolist()))
        
        st.markdown("---")
        st.caption("💡 **Tip:** Select specific filters to drill into subject or phase performance")

    filtered = df.copy()
    if f_phase != "All Phases":
        filtered = filtered[filtered["Phase"] == f_phase]
    if f_subject != "All Subjects":
        filtered = filtered[filtered["subject"] == f_subject]
    if f_grade != "All Grades":
        filtered = filtered[filtered["grade"] == f_grade]

    # Calculate metrics
    avg_t1_w = wmean(filtered["term_1"], filtered["class_size"])
    avg_t2_w = wmean(filtered["term_2"], filtered["class_size"])
    avg_improv_w = (avg_t2_w - avg_t1_w) if not (pd.isna(avg_t1_w) or pd.isna(avg_t2_w)) else np.nan
    pass_t1_count = (filtered["pass_term_1"] == True).sum()
    pass_t2_count = (filtered["pass_term_2"] == True).sum()
    pass_t1_rate = pct(pass_t1_count, len(filtered))
    pass_t2_rate = pct(pass_t2_count, len(filtered))
    learners = int(filtered["class_size"].sum())
    classes = int(len(filtered))

    # ========================================
    # SECTION 1: HEADLINE IMPACT
    # ========================================
    st.markdown("---")
    st.markdown("## 📊 Overall Impact at a Glance")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Learners Reached",
            value=f"{learners:,}",
            help="Total number of learners across all classes"
        )
        st.metric(
            label="Classes Supported",
            value=f"{classes}",
            help="Number of classes in this view"
        )
    
    with col2:
        improvement_color = "normal" if pd.isna(avg_improv_w) else ("normal" if avg_improv_w >= 0 else "inverse")
        st.metric(
            label="Average Academic Improvement",
            value=fmt_dec(avg_improv_w),
            delta=f"{fmt_pct(avg_improv_w/avg_t1_w if avg_t1_w else 0, 0)} growth" if not pd.isna(avg_improv_w) else None,
            help="Weighted average improvement from Term 1 to Term 2"
        )
    
    with col3:
        st.metric(
            label="Term 1 Performance",
            value=fmt_pct(avg_t1_w*100, 0) if not pd.isna(avg_t1_w) else "-",
            help="Baseline academic performance"
        )
        st.metric(
            label="Term 2 Performance",
            value=fmt_pct(avg_t2_w*100, 0) if not pd.isna(avg_t2_w) else "-",
            delta=fmt_pct((avg_t2_w-avg_t1_w)*100, 0) if not pd.isna(avg_improv_w) else None,
            help="End of term academic performance"
        )
    
    with col4:
        pass_improvement = pass_t2_count - pass_t1_count
        st.metric(
            label="Classes Passing (Term 2)",
            value=f"{pass_t2_count}/{classes}",
            delta=f"+{pass_improvement} classes" if pass_improvement > 0 else f"{pass_improvement} classes",
            help="Number of classes achieving passing grades"
        )
        st.metric(
            label="Pass Rate",
            value=fmt_pct(pass_t2_rate),
            delta=fmt_pct(pass_t2_rate - pass_t1_rate) if not pd.isna(pass_t2_rate) else None,
            help="Percentage of classes passing"
        )

    # Impact narrative
    if not pd.isna(avg_improv_w):
        improvement_desc = "positive growth" if avg_improv_w >= 0 else "decline"
        pass_desc = f"with {pass_t2_count} classes now passing" if pass_t2_count > pass_t1_count else ""
        st.info(f"📈 **Impact Summary:** Across {learners:,} learners in {classes} classes, we see an average improvement of {fmt_dec(avg_improv_w)} ({improvement_desc}) {pass_desc}.")

    # ========================================
    # SECTION 2: COHORT PROGRESSION STORY
    # ========================================
    st.markdown("---")
    st.markdown("## 🚀 Year-over-Year Progression")
    st.caption("Comparing Year 2 fellows with Year 1 baseline — demonstrating program maturity")
    
    if not filtered.empty:
        by_year = (
            filtered.groupby("fellowship_year")
                    .apply(lambda g: pd.Series({
                        "Term 1": wmean(g["term_1"], g["class_size"]),
                        "Term 2": wmean(g["term_2"], g["class_size"]),
                        "Improvement": wmean(g["term_2"], g["class_size"]) - wmean(g["term_1"], g["class_size"]),
                        "Classes": len(g),
                        "Learners": int(g["class_size"].sum()),
                        "Passing Classes": (g["pass_term_2"] == True).sum()
                    }))
                    .reset_index()
        )
        
        # Ensure both years
        for y in ["Year 1", "Year 2"]:
            if y not in by_year["fellowship_year"].values:
                by_year = pd.concat([by_year, pd.DataFrame([{"fellowship_year": y}])], ignore_index=True)

        y1_t2 = float(by_year.loc[by_year["fellowship_year"]=="Year 1", "Term 2"].fillna(np.nan).values[0]) if "Term 2" in by_year.columns else np.nan
        y2_t2 = float(by_year.loc[by_year["fellowship_year"]=="Year 2", "Term 2"].fillna(np.nan).values[0]) if "Term 2" in by_year.columns else np.nan
        cohort_delta = y2_t2 - y1_t2 if not (pd.isna(y1_t2) or pd.isna(y2_t2)) else np.nan

        col1, col2 = st.columns([3, 1])
        
        with col1:
            if ALT_AVAILABLE and "Term 2" in by_year.columns:
                chart_data = by_year.dropna(subset=["Term 2"]).copy()
                chart_data["Metric"] = "Term 2 Performance"
                
                chart = (
                    alt.Chart(chart_data)
                    .mark_bar(size=80)
                    .encode(
                        x=alt.X("fellowship_year:N", title="Fellowship Cohort", axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("Term 2:Q", title="Average Performance (Weighted)", scale=alt.Scale(domain=[0, 1])),
                        color=alt.Color("fellowship_year:N", scale=alt.Scale(scheme="tableau10"), legend=None),
                        tooltip=[
                            alt.Tooltip("fellowship_year", title="Cohort"),
                            alt.Tooltip("Term 1", title="Term 1", format=".2f"),
                            alt.Tooltip("Term 2", title="Term 2", format=".2f"),
                            alt.Tooltip("Improvement", title="Improvement", format=".2f"),
                            alt.Tooltip("Classes", title="Classes"),
                            alt.Tooltip("Learners", title="Learners", format=","),
                            alt.Tooltip("Passing Classes", title="Passing")
                        ]
                    )
                    .properties(height=300)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.dataframe(by_year, use_container_width=True)
        
        with col2:
            st.metric(
                label="Year 2 vs Year 1",
                value=fmt_dec(cohort_delta),
                delta="Improvement" if cohort_delta > 0 else "Decline" if cohort_delta < 0 else "No change",
                help="Difference in Term 2 performance between cohorts"
            )
            
            if not pd.isna(cohort_delta):
                if cohort_delta > 0:
                    st.success(f"✅ Year 2 outperforms Year 1 by {fmt_dec(cohort_delta)}")
                elif cohort_delta < 0:
                    st.warning(f"⚠️ Year 1 performed {fmt_dec(abs(cohort_delta))} better")
                else:
                    st.info("➡️ Both cohorts performed equally")
    else:
        st.info("No data available for cohort comparison with current filters.")

    # ========================================
    # SECTION 3: SUBJECT PERFORMANCE DEEP DIVE
    # ========================================
    st.markdown("---")
    st.markdown("## 📚 Performance by Subject")
    st.caption("Understanding which subjects show strongest improvement and where support is needed")
    
    if not filtered.empty:
        by_subject = (
            filtered.groupby("subject")
                    .apply(lambda g: pd.Series({
                        "Term 1": wmean(g["term_1"], g["class_size"]),
                        "Term 2": wmean(g["term_2"], g["class_size"]),
                        "Improvement": wmean(g["term_2"], g["class_size"]) - wmean(g["term_1"], g["class_size"]),
                        "Classes": len(g),
                        "Learners": int(g["class_size"].sum()),
                        "Pass Rate T2": pct((g["pass_term_2"] == True).sum(), len(g))
                    }))
                    .reset_index()
                    .sort_values("Improvement", ascending=False)
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if ALT_AVAILABLE:
                # Melt for grouped bar chart
                melted = by_subject.melt(
                    id_vars=["subject", "Classes", "Learners", "Pass Rate T2"],
                    value_vars=["Term 1", "Term 2"],
                    var_name="Term",
                    value_name="Performance"
                )
                
                chart = (
                    alt.Chart(melted)
                    .mark_bar()
                    .encode(
                        x=alt.X("subject:N", title="Subject", axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y("Performance:Q", title="Average Performance"),
                        color=alt.Color("Term:N", scale=alt.Scale(scheme="category10")),
                        xOffset="Term:N",
                        tooltip=[
                            alt.Tooltip("subject", title="Subject"),
                            alt.Tooltip("Term", title="Term"),
                            alt.Tooltip("Performance", title="Score", format=".2f"),
                            alt.Tooltip("Classes", title="Classes"),
                            alt.Tooltip("Learners", title="Learners", format=",")
                        ]
                    )
                    .properties(height=350)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.dataframe(by_subject, use_container_width=True)
        
        with col2:
            st.markdown("#### Subject Insights")
            
            # Top performing subject
            top_subj = by_subject.nlargest(1, "Term 2")
            if not top_subj.empty:
                st.metric(
                    "Highest Performer",
                    top_subj.iloc[0]["subject"],
                    f"{fmt_pct(top_subj.iloc[0]['Term 2']*100, 0)} avg"
                )
            
            # Most improved subject
            most_improved = by_subject.nlargest(1, "Improvement")
            if not most_improved.empty:
                st.metric(
                    "Most Improved",
                    most_improved.iloc[0]["subject"],
                    f"+{fmt_dec(most_improved.iloc[0]['Improvement'])}"
                )
            
            # Needs attention
            needs_attn = by_subject.nsmallest(1, "Improvement")
            if not needs_attn.empty and needs_attn.iloc[0]["Improvement"] < 0:
                st.metric(
                    "Needs Attention",
                    needs_attn.iloc[0]["subject"],
                    f"{fmt_dec(needs_attn.iloc[0]['Improvement'])}",
                    delta_color="inverse"
                )
    else:
        st.info("Select different filters to view subject performance.")

    # ========================================
    # SECTION 4: PHASE ANALYSIS
    # ========================================
    st.markdown("---")
    st.markdown("## 🎯 Performance by Education Phase")
    st.caption("Tracking impact across Foundation, Intermediate, Senior, and FET phases")
    
    if not filtered.empty and f_phase == "All Phases":
        by_phase = (
            filtered.groupby("Phase")
                    .apply(lambda g: pd.Series({
                        "Term 1": wmean(g["term_1"], g["class_size"]),
                        "Term 2": wmean(g["term_2"], g["class_size"]),
                        "Improvement": wmean(g["term_2"], g["class_size"]) - wmean(g["term_1"], g["class_size"]),
                        "Classes": len(g),
                        "Learners": int(g["class_size"].sum()),
                        "Pass Rate": pct((g["pass_term_2"] == True).sum(), len(g))
                    }))
                    .reset_index()
        )
        
        # Order phases logically
        phase_order = ["Foundation", "Intermediate", "Senior", "FET"]
        by_phase["Phase"] = pd.Categorical(by_phase["Phase"], categories=phase_order, ordered=True)
        by_phase = by_phase.sort_values("Phase")
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if ALT_AVAILABLE:
                chart = (
                    alt.Chart(by_phase)
                    .mark_bar(size=60)
                    .encode(
                        x=alt.X("Phase:N", title="Education Phase", sort=phase_order),
                        y=alt.Y("Improvement:Q", title="Average Improvement (Term 2 - Term 1)"),
                        color=alt.condition(
                            alt.datum.Improvement > 0,
                            alt.value("#2ecc71"),
                            alt.value("#e74c3c")
                        ),
                        tooltip=[
                            alt.Tooltip("Phase", title="Phase"),
                            alt.Tooltip("Term 1", title="Term 1", format=".2f"),
                            alt.Tooltip("Term 2", title="Term 2", format=".2f"),
                            alt.Tooltip("Improvement", title="Improvement", format=".2f"),
                            alt.Tooltip("Classes", title="Classes"),
                            alt.Tooltip("Learners", title="Learners", format=","),
                            alt.Tooltip("Pass Rate", title="Pass Rate", format=".1%")
                        ]
                    )
                    .properties(height=300)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.dataframe(by_phase, use_container_width=True)
        
        with col2:
            st.markdown("#### Phase Summary")
            best_phase = by_phase.nlargest(1, "Improvement")
            if not best_phase.empty:
                st.metric(
                    "Leading Phase",
                    best_phase.iloc[0]["Phase"],
                    f"+{fmt_dec(best_phase.iloc[0]['Improvement'])}"
                )
    elif f_phase != "All Phases":
        st.info(f"Viewing data for {f_phase} phase only. Change filter to 'All Phases' to compare across phases.")
    else:
        st.info("No phase data available.")

    # ========================================
    # SECTION 5: FOUNDATION PHASE SPOTLIGHT
    # ========================================
    st.markdown("---")
    st.markdown("## ⭐ Foundation Phase Spotlight")
    st.caption("Deep dive into Grades R–3: Building strong early learning foundations")
    
    fnd = df[df["Phase"] == "Foundation"].copy()  # Use full dataset for Foundation
    
    # Apply subject/grade filters if set
    if f_subject != "All Subjects":
        fnd = fnd[fnd["subject"] == f_subject]
    if f_grade != "All Grades":
        fnd = fnd[fnd["grade"] == f_grade]
    
    if fnd.empty:
        st.info("No Foundation Phase data available. This phase covers Grades R through 3.")
    else:
        order = ["Grade R","Grade 1","Grade 2","Grade 3"]
        fnd["grade"] = pd.Categorical(fnd["grade"], categories=order, ordered=True)
        fnd_grade = (
            fnd.groupby("grade")
               .apply(lambda g: pd.Series({
                   "Term 1": wmean(g["term_1"], g["class_size"]),
                   "Term 2": wmean(g["term_2"], g["class_size"]),
                   "Improvement": wmean(g["term_2"], g["class_size"]) - wmean(g["term_1"], g["class_size"]),
                   "Classes": len(g),
                   "Learners": int(g["class_size"].sum())
               }))
               .reset_index()
               .dropna(subset=["grade"])
               .sort_values("grade")
        )
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if ALT_AVAILABLE:
                melted = fnd_grade.melt(
                    id_vars=["grade", "Classes", "Learners"],
                    value_vars=["Term 1", "Term 2", "Improvement"],
                    var_name="Metric",
                    value_name="Score"
                )
                
                chart = (
                    alt.Chart(melted)
                    .mark_bar()
                    .encode(
                        x=alt.X("grade:N", title="Grade Level", sort=order),
                        y=alt.Y("Score:Q", title="Performance Score"),
                        color=alt.Color("Metric:N", scale=alt.Scale(scheme="tableau10")),
                        xOffset="Metric:N",
                        tooltip=[
                            alt.Tooltip("grade", title="Grade"),
                            alt.Tooltip("Metric", title="Metric"),
                            alt.Tooltip("Score", title="Score", format=".2f"),
                            alt.Tooltip("Classes", title="Classes"),
                            alt.Tooltip("Learners", title="Learners", format=",")
                        ]
                    )
                    .properties(height=320)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.dataframe(fnd_grade, use_container_width=True)
        
        with col2:
            st.markdown("#### Foundation Impact")
            fnd_avg_improv = safe_mean(fnd_grade["Improvement"])
            fnd_total_learners = int(fnd_grade["Learners"].sum())
            fnd_total_classes = int(fnd_grade["Classes"].sum())
            
            st.metric(
                "Avg Improvement",
                fmt_dec(fnd_avg_improv),
                help="Average improvement across all Foundation grades"
            )
            st.metric(
                "Learners Impacted",
                f"{fnd_total_learners:,}",
                help="Total learners in Foundation phase"
            )
            st.metric(
                "Classes",
                fnd_total_classes,
                help="Number of Foundation phase classes"
            )
            
            if not pd.isna(fnd_avg_improv) and fnd_avg_improv > 0:
                st.success("✅ Positive early-grade impact")

    # ========================================
    # SECTION 6: TOP PERFORMERS & OPPORTUNITIES
    # ========================================
    st.markdown("---")
    st.markdown("## 🏆 Champions & Opportunities")
    
    if not filtered.empty:
        grp_cols = ["Phase", "subject", "grade"]
        grouped = (
            filtered.groupby(grp_cols)
            .apply(lambda g: pd.Series({
                "Term 1": wmean(g["term_1"], g["class_size"]),
                "Term 2": wmean(g["term_2"], g["class_size"]),
                "Improvement": wmean(g["term_2"], g["class_size"]) - wmean(g["term_1"], g["class_size"]),
                "Classes": len(g),
                "Learners": int(g["class_size"].sum())
            }))
            .reset_index()
        )

        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🥇 Top Performers")
            st.caption("Highest Term 2 achievement")
            top_perf = grouped.dropna(subset=["Term 2"]).sort_values("Term 2", ascending=False).head(5)
            top_perf_display = top_perf.copy()
            top_perf_display["Term 2"] = top_perf_display["Term 2"].apply(lambda x: fmt_pct(x*100, 0))
            top_perf_display["Improvement"] = top_perf_display["Improvement"].apply(lambda x: fmt_dec(x))
            st.dataframe(top_perf_display, use_container_width=True, hide_index=True)
        
        with col2:
            st.markdown("### 📈 Biggest Gains")
            st.caption("Greatest improvement trajectory")
            top_impr = grouped.dropna(subset=["Improvement"]).sort_values("Improvement", ascending=False).head(5)
            top_impr_display = top_impr.copy()
            top_impr_display["Term 1"] = top_impr_display["Term 1"].apply(lambda x: fmt_pct(x*100, 0))
            top_impr_display["Term 2"] = top_impr_display["Term 2"].apply(lambda x: fmt_pct(x*100, 0))
            top_impr_display["Improvement"] = top_impr_display["Improvement"].apply(lambda x: f"+{fmt_dec(x)}")
            st.dataframe(top_impr_display, use_container_width=True, hide_index=True)
    else:
        st.info("Adjust filters to view top performers and improvement champions.")

    # ========================================
    # FOOTER: KEY TAKEAWAYS
    # ========================================
    st.markdown("---")
    st.markdown("### 💡 Key Takeaways")
    
    with st.expander("📋 Impact Summary", expanded=True):
        bullets = []
        
        # Overall impact
        if not pd.isna(avg_improv_w):
            trend = "positive" if avg_improv_w >= 0 else "negative"
            bullets.append(f"**Overall Impact:** Average improvement of {fmt_dec(avg_improv_w)} across {learners:,} learners ({trend} trajectory)")
        
        # Cohort comparison
        if not pd.isna(cohort_delta):
            if cohort_delta > 0:
                bullets.append(f"**Program Maturity:** Year 2 cohort outperforms Year 1 by {fmt_dec(cohort_delta)}, demonstrating program effectiveness")
            elif cohort_delta < 0:
                bullets.append(f"**Attention Needed:** Year 1 baseline was {fmt_dec(abs(cohort_delta))} higher; consider what factors changed")
        
        # Pass rate improvement
        if not pd.isna(pass_t2_rate):
            pass_change = pass_t2_count - pass_t1_count
            if pass_change > 0:
                bullets.append(f"**Quality Improvement:** {pass_change} additional classes achieved passing grades (now {fmt_pct(pass_t2_rate)})")
            else:
                bullets.append(f"**Pass Rate:** {fmt_pct(pass_t2_rate)} of classes meeting standards")
        
        # Filter-specific insights
        if f_phase == "Foundation":
            bullets.append("**Early Learning Focus:** Foundation phase showing grade-by-grade progression — critical for long-term success")
        elif f_phase != "All Phases":
            bullets.append(f"**Phase Focus:** Viewing {f_phase} phase data specifically")
        
        if f_subject != "All Subjects":
            bullets.append(f"**Subject Focus:** Analysis filtered to {f_subject}")
        
        if not bullets:
            bullets.append("Expand your filter selection to see comprehensive impact insights")
        
        for bullet in bullets:
            st.markdown(f"- {bullet}")
    
    st.caption("---")
    st.caption("📊 Dashboard powered by fellowship data • Updated in real-time")

if __name__ == "__main__":
    run()