import os
import pandas as pd
from typing import Optional
from supabase import create_client, Client

# Optional: for local .env support
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

class SupabaseConnection:
    def __init__(self, config=None):
        """
        Handles Supabase connection. 
        Prefers Streamlit secrets if available, otherwise falls back to .env or config object.
        """
        self.client: Optional[Client] = None
        self._connect(config)

    def _connect(self, config=None):
        """Establish Supabase connection with fallback logic"""
        try:
            # 1. Prefer Streamlit secrets if running inside Streamlit
            supabase_url = None
            supabase_key = None
            try:
                import streamlit as st
                if "supabase" in st.secrets:
                    supabase_url = st.secrets["supabase"]["url"]
                    supabase_key = st.secrets["supabase"]["anon_key"]
            except Exception:
                pass

            # 2. If not, use environment variables (.env or system)
            if not supabase_url:
                supabase_url = os.getenv("SUPABASE_URL")
            if not supabase_key:
                supabase_key = os.getenv("SUPABASE_ANON_KEY")

            # 3. If still missing, fallback to config object
            if config and not supabase_url:
                supabase_url = getattr(config, "SUPABASE_URL", None)
            if config and not supabase_key:
                supabase_key = getattr(config, "SUPABASE_ANON_KEY", None)

            if not supabase_url or not supabase_key:
                raise ValueError("Supabase credentials not found (secrets, env, or config).")

            self.client = create_client(supabase_url, supabase_key)
            print("✅ Supabase connection established successfully")
        except Exception as e:
            print(f"❌ Failed to connect to Supabase: {e}")
            raise

    # --------------------------
    # Helpers
    # --------------------------
    def test_connection(self, table_name: str = "observations"):
        """Test Supabase connection with a lightweight query"""
        try:
            response = self.client.table(table_name).select("*").limit(1).execute()
            print(f"✅ Connection test successful ({len(response.data)} rows fetched from {table_name})")
            return True
        except Exception as e:
            print(f"❌ Connection test failed: {e}")
            return False

    def fetch_table(self, table_name: str, columns: str = "*", filters: dict = None, limit: int = None) -> pd.DataFrame:
        """Fetch any table/view from Supabase and return as DataFrame"""
        try:
            query = self.client.table(table_name).select(columns)
            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)
            if limit:
                query = query.limit(limit)

            response = query.execute()
            return pd.DataFrame(response.data) if response.data else pd.DataFrame()
        except Exception as e:
            print(f"❌ Failed to fetch {table_name}: {e}")
            return pd.DataFrame()
