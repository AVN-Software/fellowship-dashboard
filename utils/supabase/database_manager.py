# utils/supabase/database_manager.py
from __future__ import annotations

import os
from datetime import datetime
from typing import Optional, Dict, Any

import pandas as pd

# Streamlit is optional at import-time; we only use it if present.
try:
    import streamlit as st
    _HAS_ST = True
except Exception:
    _HAS_ST = False
    st = None  # type: ignore

# Supabase SDK
try:
    from supabase import create_client, Client
except Exception as e:  # pragma: no cover
    Client = object  # type: ignore
    create_client = None  # type: ignore
    _SUPABASE_IMPORT_ERROR = e
else:
    _SUPABASE_IMPORT_ERROR = None


# -----------------------------
# Helpers
# -----------------------------
def _warn(msg: str):
    if _HAS_ST:
        st.warning(msg)
    else:
        print(f"[WARN] {msg}")


def _error(msg: str):
    if _HAS_ST:
        st.error(msg)
    else:
        print(f"[ERROR] {msg}")


def _info(msg: str):
    if _HAS_ST:
        st.info(msg)
    else:
        print(f"[INFO] {msg}")


# -----------------------------
# Client factory (cached)
# -----------------------------
def _resolve_supabase_creds() -> tuple[Optional[str], Optional[str]]:
    """Order: Streamlit secrets -> env vars -> (None, None)."""
    url = key = None
    if _HAS_ST:
        try:
            url = st.secrets["supabase"]["url"]
            key = st.secrets["supabase"]["anon_key"]
        except Exception:
            pass
    if not url:
        url = os.getenv("SUPABASE_URL")
    if not key:
        key = os.getenv("SUPABASE_ANON_KEY")
    return url, key


def _build_client() -> Optional[Client]:
    """Create the Supabase client or return None with a visible error."""
    if _SUPABASE_IMPORT_ERROR is not None or create_client is None:
        _error(
            "Supabase SDK is not installed. Add `supabase` (or `supabase==2.*`) to requirements.txt."
        )
        return None

    url, key = _resolve_supabase_creds()
    if not url or not key:
        _error(
            "Missing Supabase credentials. Add to Streamlit **secrets.toml** as\n"
            "[supabase]\nurl = \"https://YOUR-PROJECT.supabase.co\"\nanon_key = \"...\"\n"
            "or set env vars SUPABASE_URL / SUPABASE_ANON_KEY."
        )
        return None

    try:
        return create_client(url, key)
    except Exception as e:
        _error(f"Failed to create Supabase client: {e}")
        return None


if _HAS_ST:
    @st.cache_resource(show_spinner=False)
    def get_supabase_client() -> Optional[Client]:
        return _build_client()
else:
    # Non-Streamlit fallback (tests/CLIs)
    _CACHED_CLIENT: Optional[Client] = None
    def get_supabase_client() -> Optional[Client]:
        global _CACHED_CLIENT
        if _CACHED_CLIENT is None:
            _CACHED_CLIENT = _build_client()
        return _CACHED_CLIENT


# -----------------------------
# Database Manager
# -----------------------------
class DatabaseManager:
    """Unified interface for querying Supabase/Postgres."""

    def __init__(self, client: Optional[Client] = None):
        self.client: Optional[Client] = client or get_supabase_client()

    def _empty(self, table_name: str) -> pd.DataFrame:
        _warn(f"No Supabase client available; returning empty DataFrame for '{table_name}'.")
        return pd.DataFrame()

    # ---- Generic loaders
    def load_table(self, table_name: str, columns: str = "*") -> pd.DataFrame:
        if self.client is None:
            return self._empty(table_name)
        try:
            resp = self.client.table(table_name).select(columns).execute()  # type: ignore[attr-defined]
            # supabase-py v2 returns .data (list[dict])
            data = getattr(resp, "data", None)
            if data is None:
                _warn(f"Table '{table_name}' returned no data.")
                return pd.DataFrame()
            return pd.DataFrame(data)
        except Exception as e:
            _error(f"Failed to load '{table_name}': {e}")
            return pd.DataFrame()

    def run_sql(self, query: str) -> pd.DataFrame:
        """Run raw SQL via RPC function (Postgres function `execute_sql` must exist)."""
        if self.client is None:
            return self._empty("rpc.execute_sql")
        try:
            resp = self.client.rpc("execute_sql", {"query": query}).execute()  # type: ignore[attr-defined]
            data = getattr(resp, "data", None)
            return pd.DataFrame(data) if data else pd.DataFrame()
        except Exception as e:
            _error(f"SQL execution failed: {e}")
            return pd.DataFrame()

    # ---- Specific views / datasets
    def get_observations_full(self): return self.load_table("v_observation_full")
    def get_teacher_wellbeing(self): return self.load_table("teacher_wellbeing")
    def get_academic_results(self): return self.load_table("report_academic_results")
    def get_tier_analysis(self):    return self.load_table("mv_comprehensive_tier_analysis")
    def get_coach_feedback(self):   return self.load_table("mv_coach_feedback")
    def get_fellows(self):          return self.load_table("fellows")
    def get_observations(self):     return self.load_table("observations")
    def get_feedback(self):         return self.load_table("feedback")
    def get_domain_scores(self):    return self.load_table("domain_scores")

    # ---- Batch
    def load_all(self) -> Dict[str, Any]:
        return {
            "observations_full": self.get_observations_full(),
            "teacher_wellbeing": self.get_teacher_wellbeing(),
            "academic_results":  self.get_academic_results(),
            "tier_analysis":     self.get_tier_analysis(),
            "coach_feedback":    self.get_coach_feedback(),
            "fellows":           self.get_fellows(),
            "observations":      self.get_observations(),
            "feedback":          self.get_feedback(),
            "domain_scores":     self.get_domain_scores(),
            "timestamp":         datetime.now().isoformat(),
        }

    # ---- Health check
    def test_connection(self) -> bool:
        if self.client is None:
            return False
        try:
            self.client.table("observations").select("*").limit(1).execute()  # type: ignore[attr-defined]
            return True
        except Exception as e:
            _warn(f"Connection test failed: {e}")
            return False


# -----------------------------
# Optional Streamlit helper
# -----------------------------
if _HAS_ST:
    @st.cache_resource(show_spinner=False)
    def get_db() -> DatabaseManager:
        """Cached DB manager for pages: from utils.supabase.database_manager import get_db"""
        return DatabaseManager()
