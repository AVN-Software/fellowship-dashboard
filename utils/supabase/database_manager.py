import pandas as pd
import streamlit as st
from datetime import datetime
from supabase import create_client, Client


# ======================================================
# Configuration (move to secrets.toml in production)
# ======================================================
SUPABASE_URL = "https://ztxfqtefsgiazwxxxksi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI..."  # ⚠️ replace with env var in production


# ======================================================
# Database Manager
# ======================================================
class DatabaseManager:
    """
    Unified interface for querying Supabase/Postgres.
    Keeps connection logic in one place and provides
    generic + specialized loaders.
    """

    def __init__(self, url: str = SUPABASE_URL, key: str = SUPABASE_KEY):
        self.client: Client = create_client(url, key)

    # --------------------------
    # Generic Loaders
    # --------------------------
    def load_table(self, table_name: str, columns: str = "*") -> pd.DataFrame:
        """Load any table or view by name."""
        try:
            response = self.client.table(table_name).select(columns).execute()
            if hasattr(response, "error") and response.error:
                st.error(f"Error loading {table_name}: {response.error}")
                return pd.DataFrame()
            return pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception as e:
            st.error(f"Failed to load {table_name}: {e}")
            return pd.DataFrame()

    def run_sql(self, query: str) -> pd.DataFrame:
        """
        Run raw SQL via Supabase RPC (requires
        a Postgres function `execute_sql` defined).
        """
        try:
            response = self.client.rpc("execute_sql", {"query": query}).execute()
            return pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception as e:
            st.error(f"SQL execution failed: {e}")
            return pd.DataFrame()

    # --------------------------
    # Specific Views / Datasets
    # --------------------------
    def get_observations_full(self): 
        return self.load_table("v_observation_full")

    def get_teacher_wellbeing(self): 
        return self.load_table("teacher_wellbeing")

    def get_academic_results(self): 
        return self.load_table("report_academic_results")

    def get_tier_analysis(self): 
        return self.load_table("mv_comprehensive_tier_analysis")

    def get_coach_feedback(self): 
        return self.load_table("mv_coach_feedback")

    def get_fellows(self): 
        return self.load_table("fellows")

    def get_observations(self): 
        return self.load_table("observations")

    def get_feedback(self): 
        return self.load_table("feedback")

    def get_domain_scores(self): 
        return self.load_table("domain_scores")

    # --------------------------
    # Batch Loader
    # --------------------------
    def load_all(self):
        """Load all main datasets at once (for dashboards)."""
        return {
            "observations_full": self.get_observations_full(),
            "teacher_wellbeing": self.get_teacher_wellbeing(),
            "academic_results": self.get_academic_results(),
            "tier_analysis": self.get_tier_analysis(),
            "coach_feedback": self.get_coach_feedback(),
            "fellows": self.get_fellows(),
            "observations": self.get_observations(),
            "feedback": self.get_feedback(),
            "domain_scores": self.get_domain_scores(),
            "timestamp": datetime.now().isoformat(),
        }

    # --------------------------
    # Connection Test
    # --------------------------
    def test_connection(self) -> bool:
        """Quick check to confirm Supabase connection is alive."""
        try:
            self.client.table("observations").select("*").limit(1).execute()
            return True
        except Exception as e:
            st.error(f"Connection test failed: {e}")
            return False


# ======================================================
# Streamlit Integration
# ======================================================
@st.cache_data
def get_db() -> DatabaseManager:
    """Cached singleton DB connection for Streamlit."""
    return DatabaseManager()


db = get_db()

st.title("📊 Supabase Data Preview")

st.subheader("🌱 Teacher Wellbeing")
st.dataframe(db.get_teacher_wellbeing().head(10), use_container_width=True)

st.subheader("👩‍🏫 Observations (Raw)")
st.dataframe(db.get_observations().head(10), use_container_width=True)

st.subheader("📝 Feedback")
st.dataframe(db.get_feedback().head(10), use_container_width=True)

st.subheader("📐 Domain Scores")
st.dataframe(db.get_domain_scores().head(10), use_container_width=True)

st.subheader("🎓 Academic Results (Report)")
st.dataframe(db.get_academic_results().head(10), use_container_width=True)

st.subheader("🧑 Fellows")
st.dataframe(db.get_fellows().head(10), use_container_width=True)

st.subheader("🔗 Full Observations (with Feedback & Domain Scores)")
st.dataframe(db.get_observations_full().head(20), use_container_width=True)
