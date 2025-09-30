"""
Academic Results Dashboard - Tabbed Interface
Modern design with organized tabs for different analysis views
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import components.filters as fx
from datetime import datetime
from pathlib import Path
import sys

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# Import database manager
from utils.supabase.database_manager import DatabaseManager

# ========================================
# STYLING & CONSTANTS
# ========================================

COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "success": "#06A77D",
    "warning": "#F18F01",
    "danger": "#C73E1D",
    "term1": "#4A90E2",
    "term2": "#50C878",
    "gradient": ["#C73E1D", "#F18F01", "#FDB462", "#06A77D", "#2E86AB"],
}

PASS_THRESHOLD = 50.0

# ========================================
# DATA LOADING
# ========================================

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_academic_data():
    """Fetch academic results using DatabaseManager."""
    try:
        db = DatabaseManager()
        df = db.get_academic_results()
        
        if len(df) > 0:
            st.success(f"✅ Loaded {len(df)} records from database")
            return df
        else:
            st.warning("No data found in report_academic_results table.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")
        return pd.DataFrame()

# ========================================
# DATA PROCESSING
# ========================================

def prepare_academic_data(df):
    """Clean and prepare academic results data."""
    df = df.copy()
    
    df['term_1_avg'] = pd.to_numeric(df['term_1_avg'], errors='coerce')
    df['term_2_avg'] = pd.to_numeric(df['term_2_avg'], errors='coerce')
    df['class_size'] = pd.to_numeric(df['class_size'], errors='coerce').fillna(0).astype(int)
    
    df['term_1_pct'] = df['term_1_avg'] * 100
    df['term_2_pct'] = df['term_2_avg'] * 100
    df['improvement'] = df['term_2_avg'] - df['term_1_avg']
    df['improvement_pct'] = df['improvement'] * 100
    
    df['pass_term_1'] = df['term_1_pct'] >= PASS_THRESHOLD
    df['pass_term_2'] = df['term_2_pct'] >= PASS_THRESHOLD
    
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
    """Calculate weighted mean."""
    v = pd.to_numeric(values, errors='coerce')
    w = pd.to_numeric(weights, errors='coerce').fillna(0)
    total_weight = w.sum()
    if total_weight > 0:
        return float((v.fillna(0) * w).sum() / total_weight)
    return np.nan


def calculate_metrics(df):
    """Calculate key metrics."""
    df_clean = df[df['class_size'] > 0].copy()
    
    return {
        'total_classes': len(df),
        'total_learners': int(df['class_size'].sum()),
        'total_fellows': df['fellow_name'].nunique() if 'fellow_name' in df else 0,
        'term_1_avg': weighted_mean(df_clean['term_1_avg'], df_clean['class_size']),
        'term_2_avg': weighted_mean(df_clean['term_2_avg'], df_clean['class_size']),
        'pass_count_t1': int(df['pass_term_1'].sum()),
        'pass_count_t2': int(df['pass_term_2'].sum()),
        'improvement': weighted_mean(df_clean['improvement'], df_clean['class_size']),
    }


# ========================================
# MAIN RENDER FUNCTION
# ========================================

def render_academic_results_section():
    """Main function with tabbed interface - loads its own data."""
    
    # Header
    fx.topbar(
        title="📊 Academic Results Dashboard",
        subtitle="Student performance and improvement across the fellowship"
    )
    
    # Load data from Supabase
    df = load_academic_data()
    
    if len(df) == 0:
        st.error("No data available. Please check your database connection and ensure report_academic_results table has data.")
        return
    
    # Prepare data
    df_clean = prepare_academic_data(df)
    
    # Filter options
    subj_opts = sorted(df_clean['subject'].dropna().unique())
    phase_opts = sorted(df_clean['phase'].dropna().unique())
    
    def grade_key(g):
        try:
            if isinstance(g, (int, float)): return int(g)
            return int(str(g).split()[-1])
        except:
            return 9999
    
    grade_opts = sorted(df_clean['grade'].dropna().unique(), key=grade_key)
    
    # Top filters
    st.markdown("### 🎛️ Filters")
    c1, c2, c3, c4 = st.columns([1.6, 1.4, 1.4, 0.8])
    
    flt_subjects = fx._multiselect("Subject", subj_opts, subj_opts, "acad_subj", c1)
    flt_phases = fx._multiselect("Phase", phase_opts, phase_opts, "acad_phase", c2)
    flt_grades = fx._multiselect("Grade", grade_opts, grade_opts, "acad_grade", c3)
    
    if fx.reset_button("♻️ Reset", key="acad_reset", target=c4):
        for k in list(st.session_state.keys()):
            if k.startswith("acad_"):
                del st.session_state[k]
        st.rerun()
    
    # Apply filters
    filtered = df_clean.copy()
    if flt_subjects:
        filtered = filtered[filtered['subject'].isin(flt_subjects)]
    if flt_phases:
        filtered = filtered[filtered['phase'].isin(flt_phases)]
    if flt_grades:
        filtered = filtered[filtered['grade'].isin(flt_grades)]
    
    st.divider()
    
    # ========================================
    # TABS
    # ========================================
    
    tab_overview, tab_subjects, tab_years, tab_phases, tab_data = st.tabs([
        "📌 Overview",
        "📚 Subjects", 
        "🥇 Fellowship Years",
        "🎯 Education Phases",
        "📋 Data"
    ])
    
    # -------------------------
    # OVERVIEW TAB
    # -------------------------
    with tab_overview:
        if len(filtered) == 0:
            st.warning("No data available for selected filters.")
        else:
            metrics = calculate_metrics(filtered)
            
            st.subheader("Program Impact Overview")
            
            # Top metrics row
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Learners",
                    f"{metrics['total_learners']:,}",
                    help="Students across all classes"
                )
            
            with col2:
                st.metric(
                    "Classes",
                    f"{metrics['total_classes']}",
                    help="Classes tracked"
                )
            
            with col3:
                st.metric(
                    "Fellows",
                    f"{metrics['total_fellows']}",
                    help="Fellows contributing data"
                )
            
            with col4:
                pass_improvement = metrics['pass_count_t2'] - metrics['pass_count_t1']
                st.metric(
                    "Classes Passing",
                    f"{metrics['pass_count_t2']}",
                    delta=f"{pass_improvement:+d}",
                    help=f"Classes ≥{PASS_THRESHOLD}%"
                )
            
            # Performance metrics
            st.markdown("### Performance Metrics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if not pd.isna(metrics['term_1_avg']):
                    st.metric(
                        "Term 1 Baseline",
                        f"{metrics['term_1_avg']*100:.1f}%"
                    )
            
            with col2:
                if not pd.isna(metrics['term_2_avg']):
                    improvement_val = (metrics['term_2_avg'] - metrics['term_1_avg']) * 100
                    st.metric(
                        "Term 2 Performance",
                        f"{metrics['term_2_avg']*100:.1f}%",
                        delta=f"{improvement_val:+.1f}pp"
                    )
            
            with col3:
                if not pd.isna(metrics['improvement']):
                    st.metric(
                        "Average Improvement",
                        f"{metrics['improvement']*100:+.1f}pp"
                    )
            
            # Distribution visualization
            st.markdown("### Term Comparison")
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Bar chart showing average by term
                df_viz = filtered[filtered['class_size'] > 0].copy()
                
                term_averages = pd.DataFrame([
                    {
                        'Term': 'Term 1',
                        'Average': weighted_mean(df_viz['term_1_pct'], df_viz['class_size']),
                        'Classes': len(df_viz)
                    },
                    {
                        'Term': 'Term 2',
                        'Average': weighted_mean(df_viz['term_2_pct'], df_viz['class_size']),
                        'Classes': len(df_viz)
                    }
                ])
                
                fig_bar = go.Figure()
                
                fig_bar.add_trace(go.Bar(
                    x=term_averages['Term'],
                    y=term_averages['Average'],
                    marker_color=[COLORS['term1'], COLORS['term2']],
                    text=term_averages['Average'].apply(lambda x: f'{x:.1f}%'),
                    textposition='outside',
                    textfont=dict(size=14, weight='bold'),
                    hovertemplate='<b>%{x}</b><br>Average: %{y:.1f}%<br>Classes: %{customdata}<extra></extra>',
                    customdata=term_averages['Classes']
                ))
                
                fig_bar.add_hline(
                    y=PASS_THRESHOLD, 
                    line_dash="dash", 
                    line_color="gray",
                    annotation_text=f"Pass Threshold ({PASS_THRESHOLD}%)",
                    annotation_position="right"
                )
                
                fig_bar.update_layout(
                    title="Average Performance by Term",
                    yaxis_title="Average Score (%)",
                    xaxis_title="",
                    height=450,
                    yaxis_range=[0, 100],
                    showlegend=False
                )
                
                st.plotly_chart(fig_bar, use_container_width=True)
            
            with col2:
                # Box plot showing distribution
                fig_box = go.Figure()
                
                fig_box.add_trace(go.Box(
                    y=df_viz['term_1_pct'],
                    name='Term 1',
                    marker_color=COLORS['term1'],
                    boxmean='sd'
                ))
                
                fig_box.add_trace(go.Box(
                    y=df_viz['term_2_pct'],
                    name='Term 2',
                    marker_color=COLORS['term2'],
                    boxmean='sd'
                ))
                
                fig_box.add_hline(
                    y=PASS_THRESHOLD, 
                    line_dash="dash", 
                    line_color="red",
                    annotation_text=f"Pass ({PASS_THRESHOLD}%)",
                    annotation_position="right"
                )
                
                fig_box.update_layout(
                    title="Distribution by Term",
                    yaxis_title="Class Average (%)",
                    height=450,
                    showlegend=True
                )
                
                st.plotly_chart(fig_box, use_container_width=True)
            
            # Impact summary
            if not pd.isna(metrics['improvement']):
                improvement_pct = metrics['improvement'] * 100
                if improvement_pct > 0:
                    st.success(
                        f"✅ **Positive Impact:** Across **{metrics['total_classes']} classes** reaching "
                        f"**{metrics['total_learners']:,} learners**, performance improved by "
                        f"**{improvement_pct:+.1f}pp**, with **{pass_improvement:+d} additional classes** passing."
                    )
                else:
                    st.warning(f"⚠️ Performance declined by {abs(improvement_pct):.1f}pp.")
    
    # -------------------------
    # SUBJECTS TAB
    # -------------------------
    with tab_subjects:
        if len(filtered) == 0:
            st.warning("No data available.")
        else:
            st.subheader("Subject Performance Analysis")
            
            df_subj = filtered[filtered['class_size'] > 0].copy()
            
            subject_stats = df_subj.groupby('subject').apply(
                lambda g: pd.Series({
                    'Term 1': weighted_mean(g['term_1_pct'], g['class_size']),
                    'Term 2': weighted_mean(g['term_2_pct'], g['class_size']),
                    'Improvement': weighted_mean(g['improvement_pct'], g['class_size']),
                    'Classes': len(g),
                    'Learners': int(g['class_size'].sum()),
                })
            ).reset_index().sort_values('Improvement', ascending=True)
            
            # Horizontal bar chart
            fig = go.Figure()
            
            colors = [COLORS['success'] if x > 0 else COLORS['danger'] 
                     for x in subject_stats['Improvement']]
            
            fig.add_trace(go.Bar(
                y=subject_stats['subject'],
                x=subject_stats['Improvement'],
                orientation='h',
                marker_color=colors,
                text=subject_stats['Improvement'].apply(lambda x: f'{x:+.1f}pp'),
                textposition='outside'
            ))
            
            fig.update_layout(
                title="Subject Improvement (Term 1 → Term 2)",
                xaxis_title="Improvement (percentage points)",
                height=max(450, len(subject_stats) * 35),
                showlegend=False
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Top performers
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("#### 🏆 Highest Performing")
                top_3 = subject_stats.nlargest(3, 'Term 2')
                for _, row in top_3.iterrows():
                    st.metric(
                        row['subject'],
                        f"{row['Term 2']:.1f}%",
                        delta=f"{row['Improvement']:+.1f}pp"
                    )
            
            with col2:
                st.markdown("#### 📈 Most Improved")
                top_growth = subject_stats.nlargest(3, 'Improvement')
                for _, row in top_growth.iterrows():
                    st.metric(
                        row['subject'],
                        f"{row['Improvement']:+.1f}pp",
                        help=f"{row['Term 1']:.1f}% → {row['Term 2']:.1f}%"
                    )
    
    # -------------------------
    # FELLOWSHIP YEARS TAB
    # -------------------------
    with tab_years:
        if len(filtered) == 0:
            st.warning("No data available.")
        else:
            st.subheader("Fellowship Year Comparison")
            st.caption("Does experience matter? Year 1 vs Year 2")
            
            df_year = filtered[filtered['class_size'] > 0].copy()
            
            year_stats = df_year.groupby('year_display').apply(
                lambda g: pd.Series({
                    'Term 1': weighted_mean(g['term_1_pct'], g['class_size']),
                    'Term 2': weighted_mean(g['term_2_pct'], g['class_size']),
                    'Improvement': weighted_mean(g['improvement_pct'], g['class_size']),
                    'Classes': len(g),
                    'Learners': int(g['class_size'].sum()),
                })
            ).reset_index()
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                fig = go.Figure()
                
                fig.add_trace(go.Bar(
                    name='Term 1',
                    x=year_stats['year_display'],
                    y=year_stats['Term 1'],
                    marker_color=COLORS['term1'],
                    text=year_stats['Term 1'].apply(lambda x: f'{x:.1f}%'),
                    textposition='outside'
                ))
                
                fig.add_trace(go.Bar(
                    name='Term 2',
                    x=year_stats['year_display'],
                    y=year_stats['Term 2'],
                    marker_color=COLORS['term2'],
                    text=year_stats['Term 2'].apply(lambda x: f'{x:.1f}%'),
                    textposition='outside'
                ))
                
                fig.add_hline(y=PASS_THRESHOLD, line_dash="dash", line_color="gray", opacity=0.5)
                
                fig.update_layout(
                    title="Performance by Fellowship Year",
                    yaxis_title="Average Score (%)",
                    yaxis_range=[0, 105],
                    barmode='group',
                    height=450
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("**Comparison**")
                
                if len(year_stats) >= 2:
                    y1 = year_stats[year_stats['year_display'].str.contains('Year 1', na=False)]
                    y2 = year_stats[year_stats['year_display'].str.contains('Year 2', na=False)]
                    
                    if not y1.empty and not y2.empty:
                        delta_t2 = y2.iloc[0]['Term 2'] - y1.iloc[0]['Term 2']
                        delta_imp = y2.iloc[0]['Improvement'] - y1.iloc[0]['Improvement']
                        
                        st.metric("Year 2 Advantage", f"{delta_t2:+.1f}pp")
                        st.metric("Growth Difference", f"{delta_imp:+.1f}pp")
                        
                        if delta_t2 > 2:
                            st.success(f"Year 2 ahead by {delta_t2:.1f}pp")
                        elif delta_t2 < -2:
                            st.info(f"Year 1 ahead by {abs(delta_t2):.1f}pp")
                        else:
                            st.info("Similar performance")
            
            # Data table
            st.markdown("### Detailed Stats")
            st.dataframe(
                year_stats.style.format({
                    'Term 1': '{:.1f}%',
                    'Term 2': '{:.1f}%',
                    'Improvement': '{:+.1f}pp'
                }),
                use_container_width=True,
                hide_index=True
            )
    
    # -------------------------
    # PHASES TAB
    # -------------------------
    with tab_phases:
        if len(filtered) == 0:
            st.warning("No data available.")
        else:
            st.subheader("Education Phase Performance")
            
            df_phase = filtered[filtered['class_size'] > 0].copy()
            
            phase_order = ['Foundation Phase', 'Intermediate Phase', 'Senior Phase', 'FET Phase']
            
            phase_stats = df_phase.groupby('phase').apply(
                lambda g: pd.Series({
                    'Term 1': weighted_mean(g['term_1_pct'], g['class_size']),
                    'Term 2': weighted_mean(g['term_2_pct'], g['class_size']),
                    'Improvement': weighted_mean(g['improvement_pct'], g['class_size']),
                    'Classes': len(g),
                    'Pass Rate': (g['pass_term_2'].sum() / len(g) * 100) if len(g) > 0 else 0
                })
            ).reset_index()
            
            phase_stats['phase'] = pd.Categorical(phase_stats['phase'], categories=phase_order, ordered=True)
            phase_stats = phase_stats.sort_values('phase')
            
            # Chart
            fig = go.Figure()
            
            fig.add_trace(go.Bar(
                name='Term 1',
                x=phase_stats['phase'],
                y=phase_stats['Term 1'],
                marker_color=COLORS['term1'],
                opacity=0.7
            ))
            
            fig.add_trace(go.Bar(
                name='Term 2',
                x=phase_stats['phase'],
                y=phase_stats['Term 2'],
                marker_color=COLORS['term2']
            ))
            
            fig.update_layout(
                title="Performance by Education Phase",
                yaxis_title="Average Score (%)",
                yaxis_range=[0, 100],
                height=450,
                barmode='group'
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Table
            st.dataframe(
                phase_stats[['phase', 'Term 1', 'Term 2', 'Improvement', 'Classes', 'Pass Rate']].style.format({
                    'Term 1': '{:.1f}%',
                    'Term 2': '{:.1f}%',
                    'Improvement': '{:+.1f}pp',
                    'Pass Rate': '{:.1f}%'
                }).background_gradient(subset=['Improvement'], cmap='RdYlGn', vmin=-10, vmax=10),
                use_container_width=True,
                hide_index=True
            )
    
    # -------------------------
    # DATA TAB
    # -------------------------
    with tab_data:
        st.subheader("Data Explorer")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fellows_filter = st.multiselect(
                "Fellow",
                sorted(filtered['fellow_name'].unique()) if 'fellow_name' in filtered else [],
                key="data_fellows"
            )
        
        with col2:
            subjects_filter = st.multiselect(
                "Subject",
                sorted(filtered['subject'].unique()),
                key="data_subjects"
            )
        
        with col3:
            min_imp = st.slider(
                "Min Improvement (%)",
                -30.0, 30.0, -30.0,
                key="min_imp"
            )
        
        # Apply data filters
        data_filtered = filtered.copy()
        if fellows_filter:
            data_filtered = data_filtered[data_filtered['fellow_name'].isin(fellows_filter)]
        if subjects_filter:
            data_filtered = data_filtered[data_filtered['subject'].isin(subjects_filter)]
        data_filtered = data_filtered[data_filtered['improvement_pct'] >= min_imp]
        
        # Display
        display_cols = ['fellow_name', 'subject', 'grade', 'phase', 'class_size', 
                       'term_1_pct', 'term_2_pct', 'improvement_pct', 'pass_term_2']
        
        display_df = data_filtered[display_cols].rename(columns={
            'fellow_name': 'Fellow',
            'subject': 'Subject',
            'grade': 'Grade',
            'phase': 'Phase',
            'class_size': 'Class Size',
            'term_1_pct': 'Term 1 (%)',
            'term_2_pct': 'Term 2 (%)',
            'improvement_pct': 'Improvement (pp)',
            'pass_term_2': 'Passing?'
        })
        
        st.dataframe(
            display_df.style.format({
                'Term 1 (%)': '{:.1f}',
                'Term 2 (%)': '{:.1f}',
                'Improvement (pp)': '{:+.1f}'
            }).background_gradient(subset=['Improvement (pp)'], cmap='RdYlGn'),
            use_container_width=True,
            height=500,
            hide_index=True
        )
        
        st.caption(f"Showing {len(data_filtered)} of {len(filtered)} classes")
        
        # Download
        csv = display_df.to_csv(index=False)
        st.download_button(
            "📥 Download CSV",
            csv,
            f"academic_results_{datetime.now().strftime('%Y%m%d')}.csv",
            "text/csv"
        )


# ========================================
# MAIN ENTRY POINT
# ========================================

if __name__ == "__main__":
    st.set_page_config(page_title="Academic Results", page_icon="📊", layout="wide")
    render_academic_results_section()  # Loads data automatically from Supabase