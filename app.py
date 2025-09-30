import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase.database_manager import get_db

# Page config
st.set_page_config(
    page_title="TTN Fellowship Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 10px;
        color: white;
        text-align: center;
    }
    .section-divider {
        margin: 2rem 0;
        border-top: 2px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<p class="main-header">TTN Fellowship Impact Dashboard</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Comprehensive insights into classroom observations, academic performance, and teacher wellbeing</p>', unsafe_allow_html=True)

st.divider()

# Quick stats from database
@st.cache_data(ttl=3600)
def load_summary_stats():
    """Load key metrics from all data sources"""
    db = get_db()
    
    stats = {
        "observations": 0,
        "fellows": 0,
        "schools": 0,
        "wellbeing_responses": 0,
        "academic_records": 0,
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    try:
        # Observations
        obs_df = db.get_observations_full()
        if not obs_df.empty:
            stats["observations"] = len(obs_df)
            if "fellow_name" in obs_df.columns:
                stats["fellows"] = obs_df["fellow_name"].nunique()
            if "school_name" in obs_df.columns:
                stats["schools"] = obs_df["school_name"].nunique()
        
        # Wellbeing
        wellbeing_df = db.get_teacher_wellbeing()
        if not wellbeing_df.empty:
            stats["wellbeing_responses"] = len(wellbeing_df)
        
        # Academic Results
        academic_df = db.get_academic_results()
        if not academic_df.empty:
            stats["academic_records"] = len(academic_df)
    
    except Exception as e:
        st.warning(f"Could not load all statistics: {e}")
    
    return stats

# Load stats
with st.spinner("Loading dashboard statistics..."):
    stats = load_summary_stats()

# Key Metrics
st.subheader("Program Overview")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Observations",
        value=f"{stats['observations']:,}",
        help="Classroom observations conducted across all terms"
    )

with col2:
    st.metric(
        label="Fellows Tracked",
        value=f"{stats['fellows']:,}",
        help="Unique fellows in the program"
    )

with col3:
    st.metric(
        label="Schools Reached",
        value=f"{stats['schools']:,}",
        help="Partner schools in the network"
    )

with col4:
    st.metric(
        label="Wellbeing Surveys",
        value=f"{stats['wellbeing_responses']:,}",
        help="Teacher wellbeing survey responses"
    )

st.divider()

# Dashboard Sections
st.subheader("Navigate to Detailed Reports")

col_a, col_b, col_c = st.columns(3)

with col_a:
    st.markdown("### 📋 Classroom Observations")
    st.write("Track teaching quality across HITS domains with termly progression and tier analysis.")
    st.page_link("pages/1_Classroom_Observations.py", label="View Observations →", icon="📊")

with col_b:
    st.markdown("### 📚 Academic Results")
    st.write("Analyze learner performance data, pass rates, and academic trends across schools.")
    st.page_link("pages/2_Academic_Results.py", label="View Results →", icon="📈")

with col_c:
    st.markdown("### 💚 Teacher Wellbeing")
    st.write("Monitor educator wellbeing indicators and support needs across the fellowship.")
    st.page_link("pages/3_Teacher_Wellbeing.py", label="View Wellbeing →", icon="🧘")

st.divider()

# Key Insights Section
st.subheader("Key Insights")

insight_col1, insight_col2 = st.columns(2)

with insight_col1:
    st.info("""
    **Program Health**
    
    The dashboard tracks three critical dimensions of fellowship impact:
    - **Teaching Quality**: Domain-specific observations and tier progression
    - **Academic Outcomes**: Learner pass rates and performance trends
    - **Educator Support**: Wellbeing metrics and intervention needs
    """)

with insight_col2:
    st.success(f"""
    **Data Status**
    
    Last updated: **{stats['last_updated']}**
    
    - {stats['observations']:,} classroom observations recorded
    - {stats['academic_records']:,} academic performance records
    - {stats['wellbeing_responses']:,} wellbeing survey responses
    
    All data synced from Supabase database.
    """)

st.divider()

# About Section
with st.expander("ℹ️ About This Dashboard"):
    st.markdown("""
    ### TTN Fellowship Impact Dashboard
    
    This dashboard provides comprehensive insights into the Teach the Nation (TTN) Fellowship program's impact across multiple dimensions:
    
    **Data Sources:**
    - Classroom observation records with HITS domain scoring
    - Academic performance data from partner schools
    - Teacher wellbeing survey responses
    - Fellow demographic and placement information
    
    **Key Features:**
    - Real-time data from Supabase database
    - Interactive filtering and drill-down capabilities
    - Tier progression tracking and movement analysis
    - Comparative visualizations across terms, years, and cohorts
    - Exportable reports for stakeholder communication
    
    **Technical Stack:**
    - Built with Streamlit
    - Data stored in Supabase PostgreSQL
    - Interactive charts powered by Plotly
    
    For technical support or data inquiries, contact the TTN data team.
    """)

# Footer
st.divider()
st.caption(f"TTN Fellowship Dashboard • Last updated: {stats['last_updated']} • Powered by Streamlit + Supabase")