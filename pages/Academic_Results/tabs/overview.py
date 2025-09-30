"""Overview Tab - Academic Results Dashboard"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ..utils import calculate_metrics, weighted_mean, COLORS, PASS_THRESHOLD

def render(filtered):
    """Render the overview tab."""
    
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
        return
    
    metrics = calculate_metrics(filtered)
    
    st.subheader("Program Impact Overview")
    
    # Top metrics
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
    
    # Visualizations
    st.markdown("### Term Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Bar chart
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
        # Box plot
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
                f"**Positive Impact:** Across **{metrics['total_classes']} classes** reaching "
                f"**{metrics['total_learners']:,} learners**, performance improved by "
                f"**{improvement_pct:+.1f}pp**, with **{pass_improvement:+d} additional classes** passing."
            )
        else:
            st.warning(f"Performance declined by {abs(improvement_pct):.1f}pp.")