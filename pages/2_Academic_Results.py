"""
Academic Results Dashboard - Main Page
Modular design with separate tab files
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import sys

# Add repo root to path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

from utils.supabase.database_manager import get_db
from pages.Academic_Results.tabs import (
    overview, subjects, fellowship_years, 
    education_phases, data_explorer
)
from pages.Academic_Results.utils import prepare_data, apply_filters

# ========================================
# PAGE CONFIG
# ========================================
st.set_page_config(
    page_title="Academic Results Dashboard",
    page_icon="📊",
    layout="wide"
)

# ========================================
# STYLING
# ========================================
st.markdown("""
    <style>
    .filter-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .filter-header {
        color: white;
        font-size: 1.3rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    div[data-baseweb="select"] > div {
        background-color: white;
        border-radius: 8px;
    }
    
    .stMultiSelect {
        margin-bottom: 0;
    }
    
    .stButton button {
        background-color: rgba(255, 255, 255, 0.2);
        color: white;
        border: 2px solid white;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        background-color: white;
        color: #667eea;
        transform: translateY(-2px);
    }
    
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        margin-bottom: 0.5rem;
    }
    
    .sub-header {
        font-size: 1.1rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    hr {
        margin: 2rem 0;
        border: none;
        border-top: 2px solid #e0e0e0;
    }
    </style>
""", unsafe_allow_html=True)

# ========================================
# DATA LOADING
# ========================================
@st.cache_data(ttl=300)
def load_academic_data():
    """Fetch academic results from database."""
    try:
        db = get_db()
        df = db.get_academic_results()
        
        if df is not None and len(df) > 0:
            return df
        else:
            st.warning("No data found in report_academic_results table.")
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

# ========================================
# MAIN PAGE
# ========================================

# Header
st.markdown('<p class="main-header">📊 Academic Results Dashboard</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="sub-header">Student performance and improvement across the fellowship</p>',
    unsafe_allow_html=True
)

# Load and prepare data
df = load_academic_data()

if df.empty:
    st.error("No data available. Please check your database connection.")
    st.stop()

df_clean = prepare_data(df)

# Get filter options
subj_opts = sorted(df_clean['subject'].dropna().unique())
phase_opts = sorted(df_clean['phase'].dropna().unique())

def grade_key(g):
    try:
        if isinstance(g, (int, float)): 
            return int(g)
        return int(str(g).split()[-1])
    except:
        return 9999

grade_opts = sorted(df_clean['grade'].dropna().unique(), key=grade_key)

# ========================================
# FILTERS
# ========================================
with st.container():
    st.markdown('<div class="filter-container">', unsafe_allow_html=True)
    st.markdown('<div class="filter-header">🎛️ Filters</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns([2, 1.5, 1.5, 1])
    
    with col1:
        flt_subjects = st.multiselect(
            "📚 Subject",
            options=subj_opts,
            default=subj_opts,
            key="acad_subj",
            help="Filter by subject area"
        )
    
    with col2:
        flt_phases = st.multiselect(
            "🎓 Phase",
            options=phase_opts,
            default=phase_opts,
            key="acad_phase",
            help="Filter by education phase"
        )
    
    with col3:
        flt_grades = st.multiselect(
            "📊 Grade",
            options=grade_opts,
            default=grade_opts,
            key="acad_grade",
            help="Filter by grade level"
        )
    
    with col4:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("♻️ Reset", use_container_width=True, key="acad_reset"):
            for k in list(st.session_state.keys()):
                if k.startswith("acad_"):
                    del st.session_state[k]
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

# Apply filters
filtered = apply_filters(df_clean, flt_subjects, flt_phases, flt_grades)

if len(filtered) < len(df_clean):
    st.caption(f"📌 Showing {len(filtered):,} of {len(df_clean):,} records after filtering")

st.divider()

# ========================================
# TABS
# ========================================
tab_overview, tab_subjects, tab_years, tab_phases, tab_data = st.tabs([
    "📊 Overview",
    "📚 Subjects", 
    "👥 Fellowship Years",
    "🎓 Education Phases",
    "📋 Data Explorer"
])

with tab_overview:
    overview.render(filtered)

with tab_subjects:
    subjects.render(filtered)

with tab_years:
    fellowship_years.render(filtered)

with tab_phases:
    education_phases.render(filtered)

with tab_data:
    data_explorer.render(filtered, df_clean)

# Footer
st.divider()
st.caption("📊 Academic Results Dashboard • Powered by Streamlit + Supabase")