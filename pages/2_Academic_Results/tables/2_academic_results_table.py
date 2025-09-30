import streamlit as st
import pandas as pd
from datetime import datetime


def render_academic_data_explorer(df: pd.DataFrame):
    """Interactive Data Explorer for academic results."""

    st.subheader("📋 Academic Results — Data Explorer")
    st.caption("Filter, explore, and export academic performance across fellows, subjects, and phases.")

    # --------------------------
    # Select & Format Columns
    # --------------------------
    display_df = df[[
        'fellow_name', 'year_display', 'subject', 'grade', 'phase',
        'class_size', 'term_1_pct', 'term_2_pct', 'improvement_pct',
        'pass_term_2'
    ]].copy()

    display_df.columns = [
        'Fellow', 'Year', 'Subject', 'Grade', 'Phase',
        'Class Size', 'Term 1 (%)', 'Term 2 (%)',
        'Improvement (pp)', 'Passing'
    ]

    # Format numeric columns
    display_df['Term 1 (%)'] = display_df['Term 1 (%)'].map(lambda x: f"{x:.1f}" if pd.notna(x) else "-")
    display_df['Term 2 (%)'] = display_df['Term 2 (%)'].map(lambda x: f"{x:.1f}" if pd.notna(x) else "-")
    display_df['Improvement (pp)'] = display_df['Improvement (pp)'].map(lambda x: f"{x:+.1f}" if pd.notna(x) else "-")
    display_df['Passing'] = display_df['Passing'].map(lambda x: "✅" if x else "❌")

    # --------------------------
    # Filters
    # --------------------------
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        fellow_filter = st.text_input("Search Fellow (name contains)", "")
    with c2:
        year_filter = st.multiselect("Year", options=sorted(df['year_display'].unique()), default=sorted(df['year_display'].unique()))
    with c3:
        subject_filter = st.multiselect("Subject", options=sorted(df['subject'].unique()), default=[])
    with c4:
        phase_filter = st.multiselect("Phase", options=sorted(df['phase'].unique()), default=[])

    # --------------------------
    # Apply Filters
    # --------------------------
    filtered_df = display_df.copy()
    if fellow_filter:
        filtered_df = filtered_df[filtered_df['Fellow'].str.contains(fellow_filter, case=False, na=False)]
    if year_filter:
        filtered_df = filtered_df[filtered_df['Year'].isin(year_filter)]
    if subject_filter:
        filtered_df = filtered_df[filtered_df['Subject'].isin(subject_filter)]
    if phase_filter:
        filtered_df = filtered_df[filtered_df['Phase'].isin(phase_filter)]

    # --------------------------
    # Show Table
    # --------------------------
    st.dataframe(filtered_df, use_container_width=True, height=440, hide_index=True)
    st.caption(f"Showing **{len(filtered_df)}** of **{len(display_df)}** classes")

    # --------------------------
    # Export CSV
    # --------------------------
    csv = filtered_df.to_csv(index=False)
    st.download_button(
        "📥 Export CSV",
        data=csv,
        file_name=f"academic_results_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv",
        use_container_width=True,
    )
