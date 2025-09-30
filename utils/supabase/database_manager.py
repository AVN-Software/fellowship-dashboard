# utils/supabase/database_manager.py
from __future__ import annotations
from typing import Optional, Dict
from datetime import datetime

import pandas as pd
import streamlit as st
from supabase import create_client, Client

# ======================================================
# Client factory (secrets only – no getenv)
# ======================================================
def _build_supabase_client() -> Optional[Client]:
    """
    Create Supabase client from Streamlit secrets:
        st.secrets["supabase"]["url"]
        st.secrets["supabase"]["anon_key"]
    Returns None if not configured.
    """
    try:
        url = st.secrets["supabase"]["url"]        # type: ignore[attr-defined]
        key = st.secrets["supabase"]["anon_key"]   # type: ignore[attr-defined]
    except Exception:
        st.warning(
            "Missing Supabase credentials. Add to `.streamlit/secrets.toml` as:\n"
            "[supabase]\nurl = \"https://YOUR-PROJECT.supabase.co\"\n"
            "anon_key = \"YOUR_ANON_KEY\""
        )
        return None

    try:
        return create_client(url, key)
    except Exception as e:
        st.error(f"Failed to create Supabase client: {e}")
        return None


# ======================================================
# Database Manager (shared by all pages)
# ======================================================
class DatabaseManager:
    """
    Minimal DB layer for dashboards.
    Fetches:
      - v_observation_full
      - mv_teacher_wellbeing_dashboard (fallback: teacher_wellbeing)
      - report_academic_results
      - fellows (demographics subset only)
    """

    def __init__(self, client: Optional[Client] = None):
        self.client: Optional[Client] = client or _build_supabase_client()

    # ---------- internals ----------
    def _safe_table(self, table: str, columns: str = "*") -> pd.DataFrame:
        if self.client is None:
            st.info(f"No Supabase client available; returning empty DataFrame for '{table}'.")
            return pd.DataFrame()
        try:
            resp = self.client.table(table).select(columns).execute()
            return pd.DataFrame(resp.data) if getattr(resp, "data", None) else pd.DataFrame()
        except Exception as e:
            st.error(f"Error loading '{table}': {e}")
            return pd.DataFrame()

    # ---------- datasets ----------
    def get_observations_full(self) -> pd.DataFrame:
        """Comprehensive observations view (domains + feedback)."""
        return self._safe_table("v_observation_full")

    def get_teacher_wellbeing(self) -> pd.DataFrame:
        """
        Wellbeing survey MV optimized for the dashboard.
        Falls back to the raw table if MV is missing or blocked by RLS.
        """
        mv = self._safe_table("mv_teacher_wellbeing_dashboard")
        if not mv.empty:
            return mv
        st.warning("mv_teacher_wellbeing_dashboard returned no rows; falling back to 'teacher_wellbeing'.")
        return self._safe_table("teacher_wellbeing")

    def get_academic_results(self) -> pd.DataFrame:
        """Academic results report."""
        return self._safe_table("report_academic_results")

    def get_fellow_demographics(self) -> pd.DataFrame:
        """Demographics-only subset from fellows table (safe for dashboards; excludes ID numbers)."""
        cols = (
            "id, full_name, email, cellphone, gender, race, "
            "province_of_origin, year_of_entry, year_of_fellowship, "
            "fellow_category, cohort_name, partner_organization, status"
        )
        return self._safe_table("fellows", columns=cols)

    # ---------- batch convenience ----------
    def load_all_dashboard(self) -> Dict[str, pd.DataFrame]:
        """Load the four dashboard datasets at once."""
        return {
            "observations_full": self.get_observations_full(),
            "teacher_wellbeing": self.get_teacher_wellbeing(),
            "academic_results": self.get_academic_results(),
            "fellows_demo": self.get_fellow_demographics(),
            "timestamp": datetime.now().isoformat(),
        }

    # ---------- health check ----------
    def test_connection(self) -> bool:
        if self.client is None:
            return False
        try:
            self.client.table("v_observation_full").select("*").limit(1).execute()
            return True
        except Exception:
            return False


# ======================================================
# Streamlit singleton (resource, not data)
# ======================================================
@st.cache_resource(show_spinner=False)
def get_db() -> DatabaseManager:
    """Shared, cached DB instance for all pages (not pickled)."""
    return DatabaseManager()


__all__ = ["DatabaseManager", "get_db"]
