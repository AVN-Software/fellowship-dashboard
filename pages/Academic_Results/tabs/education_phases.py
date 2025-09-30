"""Education Phases Tab - Academic Results Dashboard"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ..utils import weighted_mean, COLORS

def render(filtered):
    """Render the education phases analysis tab."""
    
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
        return
    
    st.subheader("Education Phase Performance")
    
    df_phase = filtered[filtered['class_size'] > 0].copy()
    
    # Define phase order
    phase_order = ['Foundation Phase', 'Intermediate Phase', 'Senior Phase', 'FET Phase']
    
    # Calculate phase statistics
    phase_stats = df_phase.groupby('phase').apply(
        lambda g: pd.Series({
            'Term 1': weighted_mean(g['term_1_pct'], g['class_size']),
            'Term 2': weighted_mean(g['term_2_pct'], g['class_size']),
            'Improvement': weighted_mean(g['improvement_pct'], g['class_size']),
            'Classes': len(g),
            'Pass Rate': (g['pass_term_2'].sum() / len(g) * 100) if len(g) > 0 else 0
        })
    ).reset_index()
    
    # Sort by phase order
    phase_stats['phase'] = pd.Categorical(
        phase_stats['phase'], 
        categories=phase_order, 
        ordered=True
    )
    phase_stats = phase_stats.sort_values('phase')
    
    # Grouped bar chart
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
    
    # Detailed statistics table
    st.markdown("### Detailed Statistics")
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
    
    # Insights
    st.markdown("### Insights")
    
    best_phase = phase_stats.loc[phase_stats['Term 2'].idxmax()]
    most_improved = phase_stats.loc[phase_stats['Improvement'].idxmax()]
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(
            f"**Highest Performance**\n\n"
            f"{best_phase['phase']}: {best_phase['Term 2']:.1f}%"
        )
    
    with col2:
        st.info(
            f"**Greatest Improvement**\n\n"
            f"{most_improved['phase']}: {most_improved['Improvement']:+.1f}pp"
        )