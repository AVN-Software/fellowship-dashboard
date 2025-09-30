"""Subjects Tab - Academic Results Dashboard"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ..utils import weighted_mean, COLORS

def render(filtered):
    """Render the subjects analysis tab."""
    
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
        return
    
    st.subheader("Subject Performance Analysis")
    
    df_subj = filtered[filtered['class_size'] > 0].copy()
    
    # Calculate subject statistics
    subject_stats = df_subj.groupby('subject').apply(
        lambda g: pd.Series({
            'Term 1': weighted_mean(g['term_1_pct'], g['class_size']),
            'Term 2': weighted_mean(g['term_2_pct'], g['class_size']),
            'Improvement': weighted_mean(g['improvement_pct'], g['class_size']),
            'Classes': len(g),
            'Learners': int(g['class_size'].sum()),
        })
    ).reset_index().sort_values('Improvement', ascending=True)
    
    # Horizontal bar chart for improvement
    fig = go.Figure()
    
    colors = [COLORS['success'] if x > 0 else COLORS['danger'] 
             for x in subject_stats['Improvement']]
    
    fig.add_trace(go.Bar(
        y=subject_stats['subject'],
        x=subject_stats['Improvement'],
        orientation='h',
        marker_color=colors,
        text=subject_stats['Improvement'].apply(lambda x: f'{x:+.1f}pp'),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Improvement: %{x:+.1f}pp<extra></extra>'
    ))
    
    fig.update_layout(
        title="Subject Improvement (Term 1 → Term 2)",
        xaxis_title="Improvement (percentage points)",
        height=max(450, len(subject_stats) * 35),
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Top performers section
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏆 Highest Performing")
        top_3 = subject_stats.nlargest(3, 'Term 2')
        for idx, row in top_3.iterrows():
            st.metric(
                f"{idx+1}. {row['subject']}",
                f"{row['Term 2']:.1f}%",
                delta=f"{row['Improvement']:+.1f}pp"
            )
    
    with col2:
        st.markdown("#### 📈 Most Improved")
        top_growth = subject_stats.nlargest(3, 'Improvement')
        for idx, row in top_growth.iterrows():
            st.metric(
                f"{idx+1}. {row['subject']}",
                f"{row['Improvement']:+.1f}pp",
                help=f"{row['Term 1']:.1f}% → {row['Term 2']:.1f}%"
            )
    
    # Detailed table
    st.markdown("### Detailed Statistics")
    st.dataframe(
        subject_stats[['subject', 'Term 1', 'Term 2', 'Improvement', 'Classes', 'Learners']].style.format({
            'Term 1': '{:.1f}%',
            'Term 2': '{:.1f}%',
            'Improvement': '{:+.1f}pp',
        }).background_gradient(subset=['Improvement'], cmap='RdYlGn', vmin=-10, vmax=10),
        use_container_width=True,
        hide_index=True
    )