# Integration Guide for Enhanced Tier Progression Page

# 1. DATABASE CONNECTION AND DATA LOADING
# Using your existing DatabaseConnection class

import pandas as pd
import streamlit as st
from typing import Optional
from your_database_module import DatabaseConnection  # Import your existing class

# Initialize database connection (adjust based on your config setup)
@st.cache_resource
def get_database_connection():
    """Get database connection using your existing DatabaseConnection class."""
    try:
        # Assuming you have a config object - adjust as needed
        from your_config_module import config  # Replace with your actual config import
        db = DatabaseConnection(config)
        
        # Test the connection
        if db.test_connection():
            return db
        else:
            st.error("Database connection test failed")
            return None
            
    except Exception as e:
        st.error(f"Failed to establish database connection: {str(e)}")
        return None

@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_tier_analysis_data():
    """Load data from the materialized view with caching."""
    db = get_database_connection()
    
    if db is None:
        return None
    
    try:
        # Check if materialized view exists and has data
        check_query = """
        SELECT COUNT(*) as row_count 
        FROM information_schema.tables 
        WHERE table_name = 'mv_comprehensive_tier_analysis'
        AND table_schema = 'public';
        """
        
        result = db.execute_query(check_query)
        
        if result['row_count'].iloc[0] == 0:
            st.error("❌ Materialized view 'mv_comprehensive_tier_analysis' does not exist. Please create it first.")
            return None
        
        # Load the actual data
        data_query = """
        SELECT * FROM mv_comprehensive_tier_analysis
        ORDER BY term, domain, fellow_year, school_level;
        """
        
        df = db.execute_query(data_query)
        
        if df.empty:
            st.warning("⚠️ Materialized view exists but contains no data. Please refresh the view.")
            return None
        
        # Show data loading success with details
        unique_terms = df['term'].nunique()
        unique_domains = df['domain'].nunique()
        unique_fellows = df['fellow_year'].nunique() if 'fellow_year' in df.columns else 0
        unique_schools = df['school_level'].nunique() if 'school_level' in df.columns else 0
        
        st.success(f"✅ Loaded {len(df)} records | {unique_terms} terms | {unique_domains} domains | {unique_fellows} fellow years | {unique_schools} school levels")
        return df
        
    except Exception as e:
        st.error(f"Error loading tier analysis data: {str(e)}")
        return None

def refresh_materialized_view():
    """Refresh the materialized view with fresh data."""
    db = get_database_connection()
    
    if db is None:
        return False
    
    try:
        # Refresh the materialized view
        refresh_query = "REFRESH MATERIALIZED VIEW mv_comprehensive_tier_analysis;"
        
        # Execute using raw SQL since it's not a SELECT
        with db.engine.connect() as conn:
            conn.execute(text(refresh_query))
            conn.commit()
        
        st.success("✅ Materialized view refreshed successfully")
        
        # Clear the cache to force reload of fresh data
        load_tier_analysis_data.clear()
        return True
        
    except Exception as e:
        st.error(f"Error refreshing materialized view: {str(e)}")
        return False

def create_materialized_view():
    """Create the materialized view if it doesn't exist."""
    db = get_database_connection()
    
    if db is None:
        return False
    
    # The comprehensive materialized view SQL from earlier
    create_mv_query = """
    CREATE MATERIALIZED VIEW IF NOT EXISTS mv_comprehensive_tier_analysis AS
    WITH tier_calculations AS (
      SELECT 
        ds.term,
        ds.domain,
        f.year_of_fellowship as fellow_year,
        om.school_level,
        ds.observation_id,
        ds.domain_score,
        ds.tier_status_lax,
        ds.strongest_tier,
        ds.weakest_tier,
        ds.tier_1_score,
        ds.tier_2_score,
        ds.tier_3_score
      FROM domain_scores ds
      JOIN observation_metadata om ON ds.observation_id = om.observation_id
      JOIN fellow f ON om.fellow_id = f.fellow_id
      WHERE ds.term IS NOT NULL 
        AND ds.domain_score IS NOT NULL
        AND ds.tier_status_lax IS NOT NULL
        AND f.year_of_fellowship IS NOT NULL
        AND om.school_level IS NOT NULL
    ),
    
    segment_stats AS (
      SELECT 
        term,
        domain,
        fellow_year,
        school_level,
        
        -- Basic counts and averages
        COUNT(*) as total_observations,
        ROUND(AVG(domain_score), 2) as domain_avg,
        
        -- Tier Mix percentages (based on tier_status_lax)
        ROUND(
          SUM(CASE WHEN tier_status_lax = 'Tier 1' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
          0
        ) as tier_mix_t1_pct,
        
        ROUND(
          SUM(CASE WHEN tier_status_lax = 'Tier 2' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
          0
        ) as tier_mix_t2_pct,
        
        ROUND(
          SUM(CASE WHEN tier_status_lax = 'Tier 3' THEN 1 ELSE 0 END) * 100.0 / COUNT(*), 
          0
        ) as tier_mix_t3_pct,
        
        -- Average Tier Scores
        ROUND(AVG(tier_1_score), 2) as avg_tier_score_t1,
        ROUND(AVG(tier_2_score), 2) as avg_tier_score_t2,
        ROUND(AVG(tier_3_score), 2) as avg_tier_score_t3,
        
        -- Dominant Tier and Index
        MODE() WITHIN GROUP (ORDER BY tier_status_lax) as dominant_tier,
        ROUND(
          (SUM(CASE WHEN tier_status_lax = 'Tier 1' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) +
          (SUM(CASE WHEN tier_status_lax = 'Tier 2' THEN 1 ELSE 0 END) * 2.0 / COUNT(*)) +
          (SUM(CASE WHEN tier_status_lax = 'Tier 3' THEN 1 ELSE 0 END) * 3.0 / COUNT(*)),
          2
        ) as dominant_index,
        
        -- Strongest/Weakest Analysis
        MODE() WITHIN GROUP (ORDER BY strongest_tier) as strongest_tier_dominant,
        MODE() WITHIN GROUP (ORDER BY weakest_tier) as weakest_tier_dominant,
        
        ROUND(
          (SUM(CASE WHEN strongest_tier = 'Tier 1' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) +
          (SUM(CASE WHEN strongest_tier = 'Tier 2' THEN 1 ELSE 0 END) * 2.0 / COUNT(*)) +
          (SUM(CASE WHEN strongest_tier = 'Tier 3' THEN 1 ELSE 0 END) * 3.0 / COUNT(*)),
          2
        ) as strongest_index,
        
        ROUND(
          (SUM(CASE WHEN weakest_tier = 'Tier 1' THEN 1 ELSE 0 END) * 1.0 / COUNT(*)) +
          (SUM(CASE WHEN weakest_tier = 'Tier 2' THEN 1 ELSE 0 END) * 2.0 / COUNT(*)) +
          (SUM(CASE WHEN weakest_tier = 'Tier 3' THEN 1 ELSE 0 END) * 3.0 / COUNT(*)),
          2
        ) as weakest_index
        
      FROM tier_calculations
      GROUP BY term, domain, fellow_year, school_level
    )
    
    SELECT 
      -- Core dimensions
      term,
      domain,
      fellow_year,
      school_level,
      
      -- Performance metrics
      domain_avg,
      dominant_tier,
      dominant_index,
      strongest_tier_dominant as strongest_tier,
      weakest_tier_dominant as weakest_tier,
      strongest_index,
      weakest_index,
      
      -- Tier Mix percentages
      tier_mix_t1_pct,
      tier_mix_t2_pct, 
      tier_mix_t3_pct,
      
      -- Average Tier Performance Scores
      avg_tier_score_t1,
      avg_tier_score_t2,
      avg_tier_score_t3,
      
      -- Meta information
      total_observations,
      NOW() as last_updated

    FROM segment_stats
    ORDER BY term, domain, fellow_year, school_level;
    
    -- Create indexes
    CREATE INDEX IF NOT EXISTS idx_mv_tier_analysis_term_domain 
      ON mv_comprehensive_tier_analysis (term, domain);
    CREATE INDEX IF NOT EXISTS idx_mv_tier_analysis_segments 
      ON mv_comprehensive_tier_analysis (fellow_year, school_level);
    """
    
    try:
        with db.engine.connect() as conn:
            conn.execute(text(create_mv_query))
            conn.commit()
        
        st.success("✅ Materialized view created successfully")
        return True
        
    except Exception as e:
        st.error(f"Error creating materialized view: {str(e)}")
        return False

# 2. MAIN APP INTEGRATION
# Add this to your main Streamlit app file

from enhanced_tier_progression import EnhancedTierProgressionPage  # Import your enhanced class

def main():
    """Main Streamlit application."""
    
    st.set_page_config(
        page_title="Education Analytics Dashboard",
        page_icon="📊",
        layout="wide"
    )
    
    # Sidebar navigation
    with st.sidebar:
        st.title("📊 Analytics Dashboard")
        
        # Data management section
        with st.expander("🔧 Data Management", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🔄 Refresh Data", help="Refresh materialized view with latest data"):
                    with st.spinner("Refreshing data..."):
                        if refresh_materialized_view():
                            st.rerun()  # Rerun to reload fresh data
            
            with col2:
                if st.button("🏗️ Create MV", help="Create materialized view if missing"):
                    with st.spinner("Creating materialized view..."):
                        if create_materialized_view():
                            st.rerun()
        
        # Navigation menu
        page = st.selectbox(
            "Select Analysis",
            [
                "🏠 Home",
                "📈 Tier Progression Analysis",  # Your new enhanced page
                "📊 Domain Performance", 
                "👥 Fellow Analytics",
                "🏫 School Insights",
                # ... other existing pages
            ]
        )
    
    # Page routing
    if page == "🏠 Home":
        render_home_page()
    
    elif page == "📈 Tier Progression Analysis":
        render_enhanced_tier_progression()
    
    # ... other page routes
    
    else:
        st.write("Page not found")

def render_enhanced_tier_progression():
    """Render the enhanced tier progression analysis page."""
    
    # Load data with loading indicator
    with st.spinner("Loading tier analysis data..."):
        df = load_tier_analysis_data()
    
    if df is None:
        st.error("❌ Unable to load tier progression data")
        
        # Show troubleshooting options
        with st.expander("🔧 Troubleshooting"):
            st.write("**Possible solutions:**")
            st.write("1. ✅ Click 'Create MV' to create the materialized view")
            st.write("2. 🔄 Click 'Refresh Data' to update existing view")
            st.write("3. 🔌 Check database connection")
            st.write("4. 📊 Verify data exists in source tables")
            
            # Quick diagnostic queries
            if st.button("🔍 Run Diagnostics"):
                run_diagnostics()
        
        return
    
    # Data quality checks
    if not perform_data_quality_checks(df):
        st.warning("⚠️ Data quality issues detected. Results may be incomplete.")
    
    # Show data summary
    show_data_summary(df)
    
    # Initialize and render the enhanced page
    tier_page = EnhancedTierProgressionPage()
    tier_page.render(df)

def perform_data_quality_checks(df: pd.DataFrame) -> bool:
    """Perform data quality checks and show warnings if needed."""
    
    # Check for required columns
    required_columns = [
        'term', 'domain', 'fellow_year', 'school_level',
        'tier_mix_t1_pct', 'tier_mix_t2_pct', 'tier_mix_t3_pct',
        'domain_avg', 'dominant_index'
    ]
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        st.error(f"❌ Missing required columns: {missing_columns}")
        return False
    
    # Check data completeness
    total_records = len(df)
    null_counts = df.isnull().sum()
    
    issues_found = False
    
    if null_counts.sum() > 0:
        st.warning("⚠️ Data completeness issues:")
        for col, null_count in null_counts.items():
            if null_count > 0:
                percentage = (null_count / total_records) * 100
                st.write(f"  • {col}: {null_count} missing ({percentage:.1f}%)")
                issues_found = True
    
    # Check for reasonable data ranges
    if 'domain_avg' in df.columns:
        if df['domain_avg'].min() < 0 or df['domain_avg'].max() > 1:
            st.warning("⚠️ Domain averages outside expected range [0,1]")
            issues_found = True
    
    if not issues_found:
        st.success("✅ Data quality checks passed")
    
    return not issues_found

def show_data_summary(df: pd.DataFrame):
    """Show a summary of the loaded data."""
    
    with st.expander("📊 Data Summary", expanded=False):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Records", len(df))
            
        with col2:
            st.metric("Terms", df['term'].nunique())
            
        with col3:
            st.metric("Domains", df['domain'].nunique())
            
        with col4:
            st.metric("Last Updated", df['last_updated'].iloc[0].strftime("%Y-%m-%d %H:%M") if 'last_updated' in df.columns else "Unknown")
        
        # Show data distribution
        st.write("**Data Distribution:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("Terms:", list(df['term'].unique()))
            st.write("Domains:", list(df['domain'].unique()))
            
        with col2:
            if 'fellow_year' in df.columns:
                st.write("Fellow Years:", list(df['fellow_year'].unique()))
            if 'school_level' in df.columns:
                st.write("School Levels:", list(df['school_level'].unique()))

def run_diagnostics():
    """Run diagnostic queries to help troubleshoot data issues."""
    
    db = get_database_connection()
    
    if db is None:
        st.error("Cannot run diagnostics - no database connection")
        return
    
    try:
        st.write("🔍 **Running diagnostics...**")
        
        # Check source tables
        diagnostics = [
            ("Domain Scores", "SELECT COUNT(*) as count FROM domain_scores"),
            ("Observation Metadata", "SELECT COUNT(*) as count FROM observation_metadata"),
            ("Fellow Records", "SELECT COUNT(*) as count FROM fellow"),
            ("Terms Available", "SELECT DISTINCT term FROM domain_scores ORDER BY term"),
            ("Domains Available", "SELECT DISTINCT domain FROM domain_scores ORDER BY domain")
        ]
        
        for name, query in diagnostics:
            try:
                result = db.execute_query(query)
                if 'count' in result.columns:
                    st.write(f"• {name}: {result['count'].iloc[0]:,} records")
                else:
                    st.write(f"• {name}: {', '.join(result.iloc[:, 0].astype(str).tolist())}")
            except Exception as e:
                st.write(f"• {name}: ❌ Error - {str(e)}")
                
    except Exception as e:
        st.error(f"Diagnostics failed: {str(e)}")

def render_home_page():
    """Render the home page with overview."""
    st.title("🏠 Education Analytics Dashboard")
    st.write("Welcome to the comprehensive education analytics platform.")
    
    # Quick stats or overview
    with st.spinner("Loading overview data..."):
        df = load_tier_analysis_data()
        
        if df is not None:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Observations", df['total_observations'].sum())
                
            with col2:
                st.metric("Average Performance", f"{df['domain_avg'].mean():.2f}")
                
            with col3:
                latest_term = df['term'].max()
                avg_t3_pct = df[df['term'] == latest_term]['tier_mix_t3_pct'].mean()
                st.metric("Latest Tier 3%", f"{avg_t3_pct:.0f}%")

# Run the app
if __name__ == "__main__":
    main()