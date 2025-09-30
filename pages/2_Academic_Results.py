"""
Academic Results Section - Complete with Table and Graphs
Focuses on academic performance analysis with interactive visualizations
"""

import streamlit as st
import pandas as pd
import numpy as np

try:
    import altair as alt
    ALT_AVAILABLE = True
except Exception:
    ALT_AVAILABLE = False


# ========================================
# DATA PROCESSING FUNCTIONS
# ========================================

def prepare_academic_data(df):
    """
    Clean and prepare academic results data.
    
    Parameters:
    -----------
    df : pd.DataFrame with columns:
        - fellow_name, fellowship_year, subject, grade, phase_display
        - class_size, term_1_avg, term_2_avg
    """
    df = df.copy()
    
    # Ensure numeric types
    df['term_1_avg'] = pd.to_numeric(df['term_1_avg'], errors='coerce')
    df['term_2_avg'] = pd.to_numeric(df['term_2_avg'], errors='coerce')
    df['class_size'] = pd.to_numeric(df['class_size'], errors='coerce').fillna(0).astype(int)
    
    # Convert to percentages (assuming 0-1 scale)
    df['term_1_pct'] = df['term_1_avg'] * 100
    df['term_2_pct'] = df['term_2_avg'] * 100
    
    # Calculate improvement
    df['improvement'] = df['term_2_avg'] - df['term_1_avg']
    df['improvement_pct'] = df['improvement'] * 100
    
    # Calculate pass/fail (threshold: 50% = 0.50)
    df['pass_term_1'] = df['term_1_avg'] >= 0.50
    df['pass_term_2'] = df['term_2_avg'] >= 0.50
    
    # Clean display fields
    if 'fellowship_year_display' in df.columns:
        df['year_display'] = df['fellowship_year_display']
    elif 'fellowship_year' in df.columns:
        df['year_display'] = df['fellowship_year'].apply(lambda x: f"Year {x}" if pd.notna(x) else "Unknown")
    else:
        df['year_display'] = "Unknown"
    
    df['phase'] = df.get('phase_display', 'Unknown')
    df['grade'] = df.get('grade_display', df.get('grade', 'Unknown'))
    
    return df


def weighted_mean(values, weights):
    """Calculate weighted mean, handling NaN and zero weights."""
    v = pd.to_numeric(values, errors='coerce')
    w = pd.to_numeric(weights, errors='coerce').fillna(0)
    total_weight = w.sum()
    if total_weight > 0:
        return float((v.fillna(0) * w).sum() / total_weight)
    return np.nan


def calculate_overall_metrics(df):
    """Calculate overall academic metrics."""
    df_clean = df[df['class_size'] > 0].copy()
    
    metrics = {
        'total_classes': len(df),
        'total_learners': int(df['class_size'].sum()),
        'term_1_avg': weighted_mean(df_clean['term_1_avg'], df_clean['class_size']),
        'term_2_avg': weighted_mean(df_clean['term_2_avg'], df_clean['class_size']),
        'pass_count_t1': int(df['pass_term_1'].sum()),
        'pass_count_t2': int(df['pass_term_2'].sum()),
        'pass_rate_t1': df['pass_term_1'].sum() / len(df) if len(df) > 0 else 0,
        'pass_rate_t2': df['pass_term_2'].sum() / len(df) if len(df) > 0 else 0,
    }
    
    metrics['improvement'] = metrics['term_2_avg'] - metrics['term_1_avg'] if not pd.isna(metrics['term_2_avg']) else np.nan
    metrics['pass_improvement'] = metrics['pass_count_t2'] - metrics['pass_count_t1']
    
    return metrics


# ========================================
# VISUALIZATION COMPONENTS
# ========================================

def render_overall_kpis(metrics):
    """Render overall KPI cards."""
    st.markdown("### 🎯 Overall Impact")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Term 1 Average",
            f"{metrics['term_1_avg']*100:.1f}%" if not pd.isna(metrics['term_1_avg']) else "-",
            help="Baseline performance (weighted by class size)"
        )
    
    with col2:
        improvement_val = metrics['improvement'] * 100 if not pd.isna(metrics['improvement']) else 0
        st.metric(
            "Term 2 Average",
            f"{metrics['term_2_avg']*100:.1f}%" if not pd.isna(metrics['term_2_avg']) else "-",
            delta=f"{improvement_val:+.1f}pp",
            help="End of term performance (weighted by class size)"
        )
    
    with col3:
        st.metric(
            "Classes Passing (T2)",
            f"{metrics['pass_count_t2']}/{metrics['total_classes']}",
            delta=f"{metrics['pass_improvement']:+d} classes",
            help="Number of classes achieving ≥50% average"
        )
    
    with col4:
        st.metric(
            "Pass Rate",
            f"{metrics['pass_rate_t2']*100:.1f}%",
            delta=f"{(metrics['pass_rate_t2']-metrics['pass_rate_t1'])*100:+.1f}pp",
            help="Percentage of classes passing"
        )
    
    # Summary insight
    if not pd.isna(metrics['improvement']):
        st.info(f"📊 **Impact Summary:** Across **{metrics['total_classes']} classes** reaching **{metrics['total_learners']:,} learners**, average performance improved by **{improvement_val:+.1f} percentage points**, with **{metrics['pass_improvement']:+d} additional classes** achieving passing grades.")


def render_year_comparison_chart(df):
    """Render Year 1 vs Year 2 comparison."""
    st.markdown("### 🥇 Year 1 vs Year 2 Comparison")
    st.caption("Does experience matter? Comparing performance by fellowship year")
    
    # Aggregate by year
    df_clean = df[df['class_size'] > 0].copy()
    
    year_comparison = df_clean.groupby('year_display').apply(
        lambda g: pd.Series({
            'Term 1': weighted_mean(g['term_1_avg'], g['class_size']) * 100,
            'Term 2': weighted_mean(g['term_2_avg'], g['class_size']) * 100,
            'Improvement': (weighted_mean(g['term_2_avg'], g['class_size']) - weighted_mean(g['term_1_avg'], g['class_size'])) * 100,
            'Classes': len(g),
            'Learners': int(g['class_size'].sum()),
            'Pass Rate': g['pass_term_2'].sum() / len(g) * 100
        })
    ).reset_index()
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if ALT_AVAILABLE and not year_comparison.empty:
            # Melt for grouped bar chart
            melted = year_comparison.melt(
                id_vars=['year_display', 'Classes', 'Learners', 'Pass Rate'],
                value_vars=['Term 1', 'Term 2'],
                var_name='Term',
                value_name='Average Score'
            )
            
            chart = (
                alt.Chart(melted)
                .mark_bar(size=40)
                .encode(
                    x=alt.X('year_display:N', title='Fellowship Year', axis=alt.Axis(labelAngle=0)),
                    y=alt.Y('Average Score:Q', title='Average Score (%)', scale=alt.Scale(domain=[0, 100])),
                    color=alt.Color('Term:N', scale=alt.Scale(scheme='tableau10')),
                    xOffset='Term:N',
                    tooltip=[
                        alt.Tooltip('year_display', title='Year'),
                        alt.Tooltip('Term', title='Term'),
                        alt.Tooltip('Average Score', title='Score', format='.1f'),
                        alt.Tooltip('Classes', title='Classes'),
                        alt.Tooltip('Learners', title='Learners', format=',')
                    ]
                )
                .properties(height=350)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.dataframe(year_comparison, use_container_width=True)
    
    with col2:
        # Calculate delta
        if len(year_comparison) >= 2:
            y1_data = year_comparison[year_comparison['year_display'].str.contains('Year 1', na=False)]
            y2_data = year_comparison[year_comparison['year_display'].str.contains('Year 2', na=False)]
            
            if not y1_data.empty and not y2_data.empty:
                y1_t2 = y1_data.iloc[0]['Term 2']
                y2_t2 = y2_data.iloc[0]['Term 2']
                delta = y2_t2 - y1_t2
                
                st.metric(
                    "Year 2 vs Year 1",
                    f"{delta:+.1f}pp",
                    help="Difference in Term 2 performance"
                )
                
                if delta > 0:
                    st.success(f"✅ Year 2 fellows outperform Year 1 by {delta:.1f} percentage points")
                elif delta < 0:
                    st.warning(f"⚠️ Year 1 performing {abs(delta):.1f}pp better")
                else:
                    st.info("➡️ Both years performing equally")


def render_subject_performance(df):
    """Render performance by subject."""
    st.markdown("### 📚 Performance by Subject")
    st.caption("Which subjects show the strongest improvement?")
    
    # Toggle for year split
    split_by_year = st.checkbox("Split by Fellowship Year", key="subject_year_split")
    
    df_clean = df[df['class_size'] > 0].copy()
    
    if split_by_year:
        # Group by subject and year
        subject_perf = df_clean.groupby(['subject', 'year_display']).apply(
            lambda g: pd.Series({
                'Term 1': weighted_mean(g['term_1_avg'], g['class_size']) * 100,
                'Term 2': weighted_mean(g['term_2_avg'], g['class_size']) * 100,
                'Improvement': (weighted_mean(g['term_2_avg'], g['class_size']) - weighted_mean(g['term_1_avg'], g['class_size'])) * 100,
                'Classes': len(g),
            })
        ).reset_index()
        
        if ALT_AVAILABLE and not subject_perf.empty:
            chart = (
                alt.Chart(subject_perf)
                .mark_bar()
                .encode(
                    x=alt.X('subject:N', title='Subject', axis=alt.Axis(labelAngle=-45)),
                    y=alt.Y('Term 2:Q', title='Term 2 Average (%)'),
                    color=alt.Color('year_display:N', title='Fellowship Year'),
                    xOffset='year_display:N',
                    tooltip=['subject', 'year_display', alt.Tooltip('Term 2', format='.1f'), 'Classes']
                )
                .properties(height=400)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.dataframe(subject_perf, use_container_width=True)
    else:
        # Group by subject only
        subject_perf = df_clean.groupby('subject').apply(
            lambda g: pd.Series({
                'Term 1': weighted_mean(g['term_1_avg'], g['class_size']) * 100,
                'Term 2': weighted_mean(g['term_2_avg'], g['class_size']) * 100,
                'Improvement': (weighted_mean(g['term_2_avg'], g['class_size']) - weighted_mean(g['term_1_avg'], g['class_size'])) * 100,
                'Classes': len(g),
                'Learners': int(g['class_size'].sum()),
            })
        ).reset_index().sort_values('Improvement', ascending=False)
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if ALT_AVAILABLE and not subject_perf.empty:
                # Melted for grouped bars
                melted = subject_perf.melt(
                    id_vars=['subject', 'Classes', 'Learners'],
                    value_vars=['Term 1', 'Term 2'],
                    var_name='Term',
                    value_name='Score'
                )
                
                chart = (
                    alt.Chart(melted)
                    .mark_bar()
                    .encode(
                        x=alt.X('subject:N', title='Subject', axis=alt.Axis(labelAngle=-45)),
                        y=alt.Y('Score:Q', title='Average Score (%)'),
                        color=alt.Color('Term:N', scale=alt.Scale(scheme='category10')),
                        xOffset='Term:N',
                        tooltip=['subject', 'Term', alt.Tooltip('Score', format='.1f'), 'Classes']
                    )
                    .properties(height=400)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.dataframe(subject_perf, use_container_width=True)
        
        with col2:
            st.markdown("#### Top Performers")
            top_3 = subject_perf.nlargest(3, 'Term 2')
            for idx, row in top_3.iterrows():
                st.metric(
                    row['subject'],
                    f"{row['Term 2']:.1f}%",
                    delta=f"{row['Improvement']:+.1f}pp"
                )


def render_phase_performance(df):
    """Render performance by education phase."""
    st.markdown("### 🎯 Performance by Education Phase")
    st.caption("Foundation → Intermediate → Senior → FET")
    
    split_by_year = st.checkbox("Split by Fellowship Year", key="phase_year_split")
    
    df_clean = df[df['class_size'] > 0].copy()
    
    # Define phase order
    phase_order = ['Foundation Phase', 'Intermediate Phase', 'Senior Phase', 'FET Phase']
    
    if split_by_year:
        phase_perf = df_clean.groupby(['phase', 'year_display']).apply(
            lambda g: pd.Series({
                'Term 2': weighted_mean(g['term_2_avg'], g['class_size']) * 100,
                'Improvement': (weighted_mean(g['term_2_avg'], g['class_size']) - weighted_mean(g['term_1_avg'], g['class_size'])) * 100,
                'Classes': len(g),
            })
        ).reset_index()
        
        if ALT_AVAILABLE:
            chart = (
                alt.Chart(phase_perf)
                .mark_bar()
                .encode(
                    x=alt.X('phase:N', title='Education Phase', sort=phase_order),
                    y=alt.Y('Term 2:Q', title='Term 2 Average (%)'),
                    color=alt.Color('year_display:N', title='Fellowship Year'),
                    xOffset='year_display:N',
                    tooltip=['phase', 'year_display', alt.Tooltip('Term 2', format='.1f'), 'Classes']
                )
                .properties(height=350)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.dataframe(phase_perf)
    else:
        phase_perf = df_clean.groupby('phase').apply(
            lambda g: pd.Series({
                'Term 1': weighted_mean(g['term_1_avg'], g['class_size']) * 100,
                'Term 2': weighted_mean(g['term_2_avg'], g['class_size']) * 100,
                'Improvement': (weighted_mean(g['term_2_avg'], g['class_size']) - weighted_mean(g['term_1_avg'], g['class_size'])) * 100,
                'Classes': len(g),
                'Learners': int(g['class_size'].sum()),
            })
        ).reset_index()
        
        # Sort by phase order
        phase_perf['phase'] = pd.Categorical(phase_perf['phase'], categories=phase_order, ordered=True)
        phase_perf = phase_perf.sort_values('phase')
        
        if ALT_AVAILABLE:
            chart = (
                alt.Chart(phase_perf)
                .mark_bar(size=60)
                .encode(
                    x=alt.X('phase:N', title='Education Phase', sort=phase_order),
                    y=alt.Y('Improvement:Q', title='Improvement (pp)'),
                    color=alt.condition(
                        alt.datum.Improvement > 0,
                        alt.value('#2ecc71'),
                        alt.value('#e74c3c')
                    ),
                    tooltip=['phase', alt.Tooltip('Term 1', format='.1f'), alt.Tooltip('Term 2', format='.1f'), alt.Tooltip('Improvement', format='.1f'), 'Classes']
                )
                .properties(height=350)
            )
            st.altair_chart(chart, use_container_width=True)
        else:
            st.dataframe(phase_perf)


def render_full_data_table(df):
    """Render the complete academic results table."""
    st.markdown("### 📋 Complete Academic Results Table")
    st.caption("Full dataset with all classes and performance metrics")
    
    # Select and format columns for display
    display_df = df[[
        'fellow_name', 'year_display', 'subject', 'grade', 'phase',
        'class_size', 'term_1_pct', 'term_2_pct', 'improvement_pct',
        'pass_term_2'
    ]].copy()
    
    display_df.columns = [
        'Fellow', 'Year', 'Subject', 'Grade', 'Phase',
        'Class Size', 'Term 1 (%)', 'Term 2 (%)', 'Improvement (pp)', 'Passing'
    ]
    
    # Format numeric columns
    display_df['Term 1 (%)'] = display_df['Term 1 (%)'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "-")
    display_df['Term 2 (%)'] = display_df['Term 2 (%)'].apply(lambda x: f"{x:.1f}" if pd.notna(x) else "-")
    display_df['Improvement (pp)'] = display_df['Improvement (pp)'].apply(lambda x: f"{x:+.1f}" if pd.notna(x) else "-")
    display_df['Passing'] = display_df['Passing'].apply(lambda x: "✅" if x else "❌")
    
    # Add filters
    col1, col2, col3 = st.columns(3)
    with col1:
        year_filter = st.multiselect("Filter by Year", options=df['year_display'].unique(), default=df['year_display'].unique())
    with col2:
        subject_filter = st.multiselect("Filter by Subject", options=sorted(df['subject'].unique()), default=[])
    with col3:
        phase_filter = st.multiselect("Filter by Phase", options=sorted(df['phase'].unique()), default=[])
    
    # Apply filters
    filtered_df = display_df.copy()
    if year_filter:
        filtered_df = filtered_df[filtered_df['Year'].isin(year_filter)]
    if subject_filter:
        filtered_df = filtered_df[filtered_df['Subject'].isin(subject_filter)]
    if phase_filter:
        filtered_df = filtered_df[filtered_df['Phase'].isin(phase_filter)]
    
    st.dataframe(filtered_df, use_container_width=True, height=400)
    st.caption(f"Showing {len(filtered_df)} of {len(display_df)} classes")


# ========================================
# MAIN SECTION RENDERER
# ========================================

def render_academic_results_section(df):
    """
    Main function to render the complete Academic Results section.
    
    Parameters:
    -----------
    df : pd.DataFrame
        Academic results data with columns:
        - fellow_name, fellowship_year (or fellowship_year_display)
        - subject, grade (or grade_display), phase_display
        - class_size, term_1_avg, term_2_avg
    """
    
    st.markdown("## 📊 Academic Results — 2025 Impact")
    st.caption("Student performance and improvement across the fellowship")
    
    # Prepare data
    df_clean = prepare_academic_data(df)
    
    # Calculate overall metrics
    metrics = calculate_overall_metrics(df_clean)
    
    # Render sections
    render_overall_kpis(metrics)
    
    st.markdown("---")
    render_year_comparison_chart(df_clean)
    
    st.markdown("---")
    render_subject_performance(df_clean)
    
    st.markdown("---")
    render_phase_performance(df_clean)
    
    st.markdown("---")
    render_full_data_table(df_clean)


# ========================================
# TEST/DEMO
# ========================================

def test_academic_results():
    """Test the academic results section with sample data."""
    
    st.title("Academic Results Section - Test")
    
    # Sample data matching your actual structure
    sample_data = pd.DataFrame([
        {"fellow_name": "Mamsie Chauke", "fellowship_year": 2, "subject": "Life skills", "grade": 3, "phase_display": "Foundation Phase", "class_size": 56, "term_1_avg": 0.89, "term_2_avg": 0.90},
        {"fellow_name": "Carmen Britz", "fellowship_year": 1, "subject": "Life Skills", "grade": 1, "phase_display": "Foundation Phase", "class_size": 16, "term_1_avg": 0.80, "term_2_avg": 0.91},
        {"fellow_name": "Lailaa Koopman", "fellowship_year": 1, "subject": "History", "grade": 4, "phase_display": "Intermediate Phase", "class_size": 25, "term_1_avg": 0.88, "term_2_avg": 0.87},
        {"fellow_name": "Lailaa Koopman", "fellowship_year": 1, "subject": "English", "grade": 4, "phase_display": "Intermediate Phase", "class_size": 25, "term_1_avg": 0.80, "term_2_avg": 0.86},
        {"fellow_name": "Mamsie Chauke", "fellowship_year": 2, "subject": "Xitsonga", "grade": 3, "phase_display": "Foundation Phase", "class_size": 56, "term_1_avg": 0.84, "term_2_avg": 0.86},
        {"fellow_name": "MBALENHLE MPHELA", "fellowship_year": 2, "subject": "ENGLISH", "grade": 6, "phase_display": "Intermediate Phase", "class_size": 35, "term_1_avg": 0.78, "term_2_avg": 0.95},
    ] * 10)  # Multiply to have more data
    
    render_academic_results_section(sample_data)


if __name__ == "__main__":
    test_academic_results()