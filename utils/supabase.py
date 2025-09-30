import streamlit as st
import pandas as pd
from supabase import create_client, Client

# --- Hardcoded credentials ---
SUPABASE_URL = "https://ztxfqtefsgiazwxxxksi.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp0eGZxdGVmc2dpYXp3eHh4a3NpIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTQ2ODA5MDUsImV4cCI6MjA3MDI1NjkwNX0.jMrCrvOK7OBuuzIEMaaBC1gfvku16fsn8kL2jLy7qnA"

# --- Initialize client ---
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Generic loader ---
@st.cache_data
def load_table(table_name: str):
    """
    Pulls an entire table (or view) from Supabase.
    Returns a pandas DataFrame.
    """
    response = supabase.table(table_name).select("*").execute()
    if response.error:
        st.error(f"Error loading {table_name}: {response.error}")
        return pd.DataFrame()
    return pd.DataFrame(response.data)

# --- Loaders for your schema ---
def load_teacher_wellbeing():
    return load_table("teacher_wellbeing")

def load_observations():
    return load_table("observations")

def load_feedback():
    return load_table("feedback")

def load_domain_scores():
    return load_table("domain_scores")

def load_report_academic_results():
    return load_table("report_academic_results")

def load_fellows():
    return load_table("fellows")

# 🚀 NEW: Full observations (observations + feedback + domain_scores)
def load_observations_full():
    return load_table("v_observation_full")   # <-- the SQL view you created

# --- Example preview in Streamlit ---
st.title("📊 Supabase Data Preview")

st.subheader("🌱 Teacher Wellbeing")
st.dataframe(load_teacher_wellbeing().head(10), use_container_width=True)

st.subheader("👩‍🏫 Observations (Raw)")
st.dataframe(load_observations().head(10), use_container_width=True)

st.subheader("📝 Feedback")
st.dataframe(load_feedback().head(10), use_container_width=True)

st.subheader("📐 Domain Scores")
st.dataframe(load_domain_scores().head(10), use_container_width=True)

st.subheader("🎓 Academic Results (Report)")
st.dataframe(load_report_academic_results().head(10), use_container_width=True)

st.subheader("🧑 Fellows")
st.dataframe(load_fellows().head(10), use_container_width=True)

st.subheader("🔗 Full Observations (with Feedback & Domain Scores)")
st.dataframe(load_observations_full().head(20), use_container_width=True)
