"""
Program Scale Component - Story-Driven Version
Tells the story: Scale & Reach → Growth Journey → Diverse & Representative
"""

import streamlit as st
import pandas as pd
import numpy as np

try:
    import altair as alt
    ALT_AVAILABLE = True
except Exception:
    ALT_AVAILABLE = False


def calculate_program_scale_metrics(fellows_df, academic_results_df=None):
    """
    Calculate program scale metrics from fellows and academic data.
    
    Parameters:
    -----------
    fellows_df : pd.DataFrame
        Fellows table with: year_of_fellowship, gender, province_of_origin, school_assignment_id
    academic_results_df : pd.DataFrame (optional)
        Academic results with: fellow_id, class_size, etc.
        
    Returns:
    --------
    dict : Dictionary containing all scale metrics
    """
    
    # Filter to active fellows
    if 'status' in fellows_df.columns:
        active_fellows = fellows_df[fellows_df['status'] == 'Active'].copy()
    else:
        active_fellows = fellows_df.copy()
    
    metrics = {
        # Overall totals
        "total_fellows": len(active_fellows),
        "total_schools": active_fellows['school_assignment_id'].nunique() if 'school_assignment_id' in active_fellows.columns else None,
        "total_provinces": active_fellows['province_of_origin'].nunique() if 'province_of_origin' in active_fellows.columns else None,
        
        # Year breakdown
        "year_1_fellows": len(active_fellows[active_fellows['year_of_fellowship'] == 1]) if 'year_of_fellowship' in active_fellows.columns else None,
        "year_2_fellows": len(active_fellows[active_fellows['year_of_fellowship'] == 2]) if 'year_of_fellowship' in active_fellows.columns else None,
        
        # Gender
        "female_count": len(active_fellows[active_fellows['gender'] == 'Female']) if 'gender' in active_fellows.columns else None,
        "male_count": len(active_fellows[active_fellows['gender'] == 'Male']) if 'gender' in active_fellows.columns else None,
    }
    
    # Calculate learners if academic data provided
    if academic_results_df is not None:
        metrics["total_learners"] = int(academic_results_df['class_size'].sum())
        metrics["total_classes"] = len(academic_results_df)
    else:
        metrics["total_learners"] = None
        metrics["total_classes"] = None
    
    return metrics


def render_program_scale_story(fellows_df, academic_results_df=None, historical_data=None):
    """
    Render the complete Program Scale section with story arc.
    
    Parameters:
    -----------
    fellows_df : pd.DataFrame
        Current fellows (2025)
    academic_results_df : pd.DataFrame (optional)
        Academic results for learner count
    historical_data : pd.DataFrame (optional)
        Columns: year, fellows, provinces, schools (for growth chart)
    """
    
    st.markdown("## 📊 Program Scale & Reach")
    st.caption("The fellowship journey: From 23 pioneers to a national movement")
    
    # Calculate metrics
    metrics = calculate_program_scale_metrics(fellows_df, academic_results_df)
    
    # ========================================
    # ARC 1: SCALE & REACH
    # ========================================
    st.markdown("### 🎯 2025 Active Cohort")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="👥 Fellows",
            value=f"{metrics['total_fellows']:,}",
            help="Active teachers in the fellowship program"
        )
        if metrics['year_1_fellows'] and metrics['year_2_fellows']:
            st.caption(f"**{metrics['year_1_fellows']}** Year 1 • **{metrics['year_2_fellows']}** Year 2")
    
    with col2:
        if metrics['total_schools']:
            st.metric(
                label="🏫 Schools",
                value=f"{metrics['total_schools']:,}",
                help="Schools with fellow placements"
            )
        else:
            st.metric(label="🏫 Schools", value="-")
    
    with col3:
        if metrics['total_provinces']:
            st.metric(
                label="🌍 Provinces",
                value=f"{metrics['total_provinces']}",
                help="Provinces where fellows are teaching"
            )
        else:
            st.metric(label="🌍 Provinces", value="-")
    
    with col4:
        if metrics['total_learners']:
            st.metric(
                label="🎓 Learners",
                value=f"{metrics['total_learners']:,}",
                help="Estimated learners reached (total class sizes)"
            )
        else:
            st.metric(label="🎓 Learners", value="-")
    
    # ========================================
    # ARC 2: GROWTH JOURNEY
    # ========================================
    st.markdown("---")
    st.markdown("### 📈 Growth Trajectory")
    st.caption("Building a movement: 2021 → 2025")
    
    if historical_data is not None and not historical_data.empty:
        # Create growth visualization
        col1, col2 = st.columns([2, 1])
        
        with col1:
            if ALT_AVAILABLE:
                # Line chart showing growth
                chart = (
                    alt.Chart(historical_data)
                    .mark_line(point=True, strokeWidth=3)
                    .encode(
                        x=alt.X('year:O', title='Year', axis=alt.Axis(labelAngle=0)),
                        y=alt.Y('fellows:Q', title='Number of Fellows', scale=alt.Scale(domain=[0, historical_data['fellows'].max() * 1.1])),
                        tooltip=[
                            alt.Tooltip('year:O', title='Year'),
                            alt.Tooltip('fellows:Q', title='Fellows'),
                            alt.Tooltip('provinces:Q', title='Provinces'),
                            alt.Tooltip('schools:Q', title='Schools') if 'schools' in historical_data.columns else alt.Tooltip('year:O')
                        ]
                    )
                    .properties(height=300)
                    .configure_point(size=100, color='#1f77b4')
                    .configure_line(color='#1f77b4')
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.dataframe(historical_data, use_container_width=True)
        
        with col2:
            # Growth stats
            first_year = historical_data.iloc[0]
            last_year = historical_data.iloc[-1]
            
            growth_fellows = last_year['fellows'] - first_year['fellows']
            growth_pct = ((last_year['fellows'] - first_year['fellows']) / first_year['fellows'] * 100)
            
            st.metric(
                "Fellows Growth",
                f"+{growth_fellows}",
                f"{growth_pct:.0f}% increase"
            )
            
            if 'provinces' in historical_data.columns:
                st.metric(
                    "Provincial Expansion",
                    f"{first_year['provinces']} → {last_year['provinces']}",
                    f"+{int(last_year['provinces'] - first_year['provinces'])} provinces"
                )
            
            st.info(f"**{first_year['year']}:** {int(first_year['fellows'])} fellows in {int(first_year['provinces'])} province\n\n**{int(last_year['year'])}:** {int(last_year['fellows'])} fellows across {int(last_year['provinces'])} provinces")
    else:
        st.info("💡 Historical data not available. Add `historical_data` DataFrame to show growth trajectory.")
    
    # ========================================
    # ARC 3: DIVERSE & REPRESENTATIVE
    # ========================================
    st.markdown("---")
    st.markdown("### 👥 Fellow Composition")
    st.caption("Who our fellows are: Gender diversity and geographic reach")
    
    # Control for splitting by year
    split_option = st.radio(
        "View by:",
        ["Combined (All Fellows)", "Year 1", "Year 2", "Year 1 vs Year 2 Comparison"],
        horizontal=True,
        key="composition_split"
    )
    
    # Filter based on selection
    if split_option == "Year 1":
        display_df = fellows_df[fellows_df['year_of_fellowship'] == 1].copy()
    elif split_option == "Year 2":
        display_df = fellows_df[fellows_df['year_of_fellowship'] == 2].copy()
    else:
        display_df = fellows_df.copy()
    
    col1, col2 = st.columns(2)
    
    # ========================================
    # GENDER CHART
    # ========================================
    with col1:
        st.markdown("#### Gender Distribution")
        
        if 'gender' in display_df.columns:
            if split_option == "Year 1 vs Year 2 Comparison":
                # Grouped bar chart
                gender_data = display_df.groupby(['year_of_fellowship', 'gender']).size().reset_index(name='count')
                gender_data['year_label'] = gender_data['year_of_fellowship'].map({1: 'Year 1', 2: 'Year 2'})
                
                if ALT_AVAILABLE and not gender_data.empty:
                    chart = (
                        alt.Chart(gender_data)
                        .mark_bar()
                        .encode(
                            x=alt.X('gender:N', title='Gender'),
                            y=alt.Y('count:Q', title='Number of Fellows'),
                            color=alt.Color('year_label:N', title='Fellowship Year', scale=alt.Scale(scheme='tableau10')),
                            xOffset='year_label:N',
                            tooltip=['year_label', 'gender', 'count']
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.dataframe(gender_data, use_container_width=True)
            else:
                # Simple bar chart
                gender_counts = display_df['gender'].value_counts().reset_index()
                gender_counts.columns = ['gender', 'count']
                gender_counts['percentage'] = (gender_counts['count'] / gender_counts['count'].sum() * 100).round(1)
                
                if ALT_AVAILABLE and not gender_counts.empty:
                    chart = (
                        alt.Chart(gender_counts)
                        .mark_bar()
                        .encode(
                            x=alt.X('gender:N', title='Gender'),
                            y=alt.Y('count:Q', title='Number of Fellows'),
                            color=alt.Color('gender:N', scale=alt.Scale(scheme='category10'), legend=None),
                            tooltip=[
                                alt.Tooltip('gender', title='Gender'),
                                alt.Tooltip('count', title='Count'),
                                alt.Tooltip('percentage', title='Percentage', format='.1f')
                            ]
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.dataframe(gender_counts, use_container_width=True)
                
                # Summary stats
                female_pct = gender_counts[gender_counts['gender'] == 'Female']['percentage'].values[0] if 'Female' in gender_counts['gender'].values else 0
                st.caption(f"**{female_pct:.0f}%** of fellows are women")
        else:
            st.info("Gender data not available")
    
    # ========================================
    # PROVINCE CHART
    # ========================================
    with col2:
        st.markdown("#### Province of Origin")
        
        if 'province_of_origin' in display_df.columns:
            if split_option == "Year 1 vs Year 2 Comparison":
                # Grouped bar chart
                province_data = display_df.groupby(['year_of_fellowship', 'province_of_origin']).size().reset_index(name='count')
                province_data['year_label'] = province_data['year_of_fellowship'].map({1: 'Year 1', 2: 'Year 2'})
                
                if ALT_AVAILABLE and not province_data.empty:
                    chart = (
                        alt.Chart(province_data)
                        .mark_bar()
                        .encode(
                            y=alt.Y('province_of_origin:N', title='Province', sort='-x'),
                            x=alt.X('count:Q', title='Number of Fellows'),
                            color=alt.Color('year_label:N', title='Fellowship Year', scale=alt.Scale(scheme='tableau10')),
                            yOffset='year_label:N',
                            tooltip=['year_label', 'province_of_origin', 'count']
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.dataframe(province_data, use_container_width=True)
            else:
                # Simple horizontal bar chart
                province_counts = display_df['province_of_origin'].value_counts().reset_index()
                province_counts.columns = ['province', 'count']
                
                if ALT_AVAILABLE and not province_counts.empty:
                    chart = (
                        alt.Chart(province_counts)
                        .mark_bar()
                        .encode(
                            y=alt.Y('province:N', title='Province', sort='-x'),
                            x=alt.X('count:Q', title='Number of Fellows'),
                            color=alt.Color('province:N', scale=alt.Scale(scheme='category20'), legend=None),
                            tooltip=['province', 'count']
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.dataframe(province_counts, use_container_width=True)
                
                # Summary
                top_province = province_counts.iloc[0]
                st.caption(f"**{top_province['province']}** has the most fellows ({top_province['count']})")
        else:
            st.info("Province data not available")
    
    # Story summary
    st.markdown("---")
    if metrics['female_count'] and metrics['total_fellows']:
        female_pct = (metrics['female_count'] / metrics['total_fellows'] * 100)
        st.success(f"💡 **The Fellowship Impact:** {metrics['total_fellows']} diverse educators ({female_pct:.0f}% women) from across South Africa, reaching {metrics['total_learners']:,} learners in {metrics['total_schools']} schools.")
    else:
        st.success(f"💡 **The Fellowship Impact:** {metrics['total_fellows']} diverse educators reaching learners across South Africa.")


# ========================================
# TEST FUNCTION
# ========================================
def test_program_scale():
    """Test the program scale component with sample data"""
    
    st.title("Program Scale Component - Test")
    
    # Sample fellows data
    fellows_data = pd.DataFrame([
        {"year_of_fellowship": 1, "gender": "Female", "province_of_origin": "Gauteng", "status": "Active", "school_assignment_id": "school-1"},
        {"year_of_fellowship": 1, "gender": "Male", "province_of_origin": "Western Cape", "status": "Active", "school_assignment_id": "school-2"},
        {"year_of_fellowship": 2, "gender": "Female", "province_of_origin": "Gauteng", "status": "Active", "school_assignment_id": "school-1"},
        {"year_of_fellowship": 2, "gender": "Female", "province_of_origin": "KZN", "status": "Active", "school_assignment_id": "school-3"},
        {"year_of_fellowship": 1, "gender": "Male", "province_of_origin": "Eastern Cape", "status": "Active", "school_assignment_id": "school-4"},
        {"year_of_fellowship": 2, "gender": "Female", "province_of_origin": "Limpopo", "status": "Active", "school_assignment_id": "school-5"},
    ] * 26)  # Multiply to get ~156 fellows
    
    # Sample academic data
    academic_data = pd.DataFrame([
        {"fellow_id": "f1", "class_size": 32},
        {"fellow_id": "f1", "class_size": 32},
        {"fellow_id": "f2", "class_size": 28},
    ] * 100)
    
    # Historical growth data
    historical = pd.DataFrame([
        {"year": 2021, "fellows": 23, "provinces": 1, "schools": 3},
        {"year": 2022, "fellows": 45, "provinces": 2, "schools": 12},
        {"year": 2023, "fellows": 89, "provinces": 3, "schools": 28},
        {"year": 2024, "fellows": 134, "provinces": 4, "schools": 38},
        {"year": 2025, "fellows": 156, "provinces": 5, "schools": 45},
    ])
    
    render_program_scale_story(fellows_data, academic_data, historical)


if __name__ == "__main__":
    test_program_scale()