# dash/fellow_wellbeing/fellow_wellbeing_dashboard.py
import streamlit as st
import pandas as pd
from pathlib import Path
import sys

# --- make repo root importable ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# External filters/topbar (your existing component)
import components.filters as fx

# Utils
from fellow_wellbeing.utils.wellbeing_utils import (
    TERMS, ALL_ITEMS, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX,
    load_wellbeing_data, risk_bucket, order_terms, dimension_scores
)

# Tabs
from fellow_wellbeing.tabs import overview, progression, domains, indicators, risk, fellows, data as data_tab

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Fellow Wellbeing Survey",
    page_icon="🌱",
    layout="wide",
)

# =========================
# Data
# =========================
df_surveys: pd.DataFrame = load_wellbeing_data()

# =========================
# Header & Filters
# =========================
fx.topbar(
    "🌱 Fellow Wellbeing Survey",
    "Tracking holistic wellbeing per term with progression by Phase and Year of Fellowship"
)

filters = fx.write_wellbeing_filters(df_surveys, TERMS, target=st.sidebar)

if fx.reset_button("♻️ Reset Filters", key="reset_wb", target=st.sidebar):
    for k in list(st.session_state.keys()):
        if k.startswith("wb_"):
            del st.session_state[k]
    st.rerun()

# =========================
# Apply Filters
# =========================
filtered = df_surveys.copy()

if filters["terms"]:
    filtered = filtered[filtered["term"].isin(filters["terms"])]

if filters["phase"]:
    filtered = filtered[filtered["phase"].isin(filters["phase"])]

if filters["year"] != "Both":
    year_num = 1 if filters["year"] == "Year 1" else 2
    filtered = filtered[filtered["fellowship_year"] == year_num]

if filters["facilitators"]:
    filtered = filtered[filtered["name_of_facilitator"].isin(filters["facilitators"])]

st.caption("Scoring: 1=Struggling, 2=Coping, 3=Confident • 63 indicators")
st.divider()

# =========================
# Tabs
# =========================
tab_overview, tab_progress, tab_domains, tab_indicators, tab_risk, tab_fellows, tab_data = st.tabs(
    ["📌 Overview", "📈 Progression", "🧭 Domains", "🧩 Indicators", "🚨 At-Risk", "👤 Fellows", "📋 Data"]
)

with tab_overview:
    overview.render(filtered, ALL_ITEMS, TERMS, COLORS, risk_bucket, order_terms)

with tab_progress:
    progression.render(filtered, ALL_ITEMS, TERMS)

with tab_domains:
    domains.render(filtered, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX)

with tab_indicators:
    indicators.render(filtered, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX)

with tab_risk:
    risk.render(filtered, ALL_ITEMS, COLORS, risk_bucket)

with tab_fellows:
    fellows.render(filtered, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX, risk_bucket)

with tab_data:
    data_tab.render(filtered, ALL_ITEMS, risk_bucket)
    
st.divider()
st.caption("🌱 Fellow Wellbeing Survey Dashboard • Streamlit • Term-focused (Overall first)")
