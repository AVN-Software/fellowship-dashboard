"""Data Explorer Tab - Academic Results Dashboard"""

import streamlit as st
import pandas as pd
from datetime import datetime

def render(filtered, df_full):
    """Render the data explorer tab."""
    
    st.subheader("Data Explorer")
    st.caption("Explore and export detailed academic results data")
    
    # Additional filters for data exploration
    col1, col2, col3 = st.columns(3)
    
    with col1:
        fellows_filter = st.multiselect(
            "Filter by Fellow",
            sorted(filtered['fellow_name'].unique()) if 'fellow_name' in filtered else [],
            key="data_fellows"
        )
    
    with col2:
        subjects_filter = st.multiselect(
            "Filter by Subject",
            sorted(filtered['subject'].unique()),
            key="data_subjects"
        )
    
    with col3:
        min_imp = st.slider(
            "Minimum Improvement (%)",
            -30.0, 30.0, -30.0,
            key="min_imp",
            help="Filter classes by minimum improvement percentage"
        )
    
    # Apply additional filters
    data_filtered = filtered.copy()
    
    if fellows_filter:
        data_filtered = data_filtered[data_filtered['fellow_name'].isin(fellows_filter)]
    if subjects_filter:
        data_filtered = data_filtered[data_filtered['subject'].isin(subjects_filter)]
    
    data_filtered = data_filtered[data_filtered['improvement_pct'] >= min_imp]
    
    # Display columns
    display_cols = [
        'fellow_name', 'subject', 'grade', 'phase', 'class_size', 
        'term_1_pct', 'term_2_pct', 'improvement_pct', 'pass_term_2'
    ]
    
    # Check which columns exist
    available_cols = [col for col in display_cols if col in data_filtered.columns]
    
    display_df = data_filtered[available_cols].rename(columns={
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
    
    # Display dataframe with styling
    st.dataframe(
        display_df.style.format({
            'Term 1 (%)': '{:.1f}',
            'Term 2 (%)': '{:.1f}',
            'Improvement (pp)': '{:+.1f}'
        }).background_gradient(subset=['Improvement (pp)'], cmap='RdYlGn', vmin=-20, vmax=20),
        use_container_width=True,
        height=500,
        hide_index=True
    )
    
    # Summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Records Shown",
            f"{len(data_filtered):,}",
            help=f"Out of {len(df_full):,} total records"
        )
    
    with col2:
        if len(data_filtered) > 0:
            avg_improvement = data_filtered['improvement_pct'].mean()
            st.metric(
                "Average Improvement",
                f"{avg_improvement:+.1f}pp"
            )
    
    with col3:
        if len(data_filtered) > 0:
            passing_pct = (data_filtered['pass_term_2'].sum() / len(data_filtered)) * 100
            st.metric(
                "Passing Rate",
                f"{passing_pct:.1f}%"
            )
    
    # Download button
    csv = display_df.to_csv(index=False)
    st.download_button(
        "📥 Download Filtered Data as CSV",
        csv,
        f"academic_results_{datetime.now().strftime('%Y%m%d')}.csv",
        "text/csv",
        use_container_width=True
    )