"""Fellowship Years Tab - Academic Results Dashboard"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from ..utils import weighted_mean, COLORS, PASS_THRESHOLD

def render(filtered):
    """Render the fellowship years comparison tab."""
    
    if len(filtered) == 0:
        st.warning("No data available for selected filters.")
        return
    
    st.subheader("Fellowship Year Comparison")
    st.caption("Does experience matter? Year 1 vs Year 2")
    
    df_year = filtered[filtered['class_size'] > 0].copy()
    
    # Calculate year statistics
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
        # Grouped bar chart
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
        
        fig.add_hline(
            y=PASS_THRESHOLD, 
            line_dash="dash", 
            line_color="gray", 
            opacity=0.5,
            annotation_text=f"Pass ({PASS_THRESHOLD}%)"
        )
        
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
                
                st.metric("Year 2 Advantage (Term 2)", f"{delta_t2:+.1f}pp")
                st.metric("Growth Difference", f"{delta_imp:+.1f}pp")
                
                if delta_t2 > 2:
                    st.success(f"✅ Year 2 ahead by {delta_t2:.1f}pp")
                elif delta_t2 < -2:
                    st.info(f"ℹ️ Year 1 ahead by {abs(delta_t2):.1f}pp")
                else:
                    st.info("➡️ Similar performance")
    
    # Detailed statistics table
    st.markdown("### Detailed Statistics")
    st.dataframe(
        year_stats.style.format({
            'Term 1': '{:.1f}%',
            'Term 2': '{:.1f}%',
            'Improvement': '{:+.1f}pp'
        }).background_gradient(subset=['Improvement'], cmap='RdYlGn'),
        use_container_width=True,
        hide_index=True
    )
    
    # Insights
    if len(year_stats) >= 2:
        st.markdown("### Insights")
        
        best_year = year_stats.loc[year_stats['Term 2'].idxmax()]
        most_improved = year_stats.loc[year_stats['Improvement'].idxmax()]
        
        st.info(
            f"📊 **Best Performance**: {best_year['year_display']} with {best_year['Term 2']:.1f}% average in Term 2\n\n"
            f"📈 **Most Improved**: {most_improved['year_display']} with {most_improved['Improvement']:+.1f}pp improvement"
        )