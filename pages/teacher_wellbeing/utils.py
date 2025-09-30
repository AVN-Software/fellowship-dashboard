# dash/fellow_wellbeing/utils/wellbeing_utils.py
from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from pathlib import Path
import sys

# Repo root import (for DatabaseManager)
ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    from utils.supabase.database_manager import DatabaseManager
except Exception as e:
    DatabaseManager = None
    st.warning(f"DatabaseManager import failed ({e}). Using sample data.")

# =========================
# Constants & Palettes
# =========================
TERMS = ["Term 1", "Term 2"]
SCORE_MIN, SCORE_MAX = 1, 3

COLORS = {
    "terms": {"Term 1": "#4E79A7", "Term 2": "#59A14F"},
    "years": {"Year 1": "#4E79A7", "Year 2": "#59A14F"},
    "traffic": {"bad": "#E15759", "warn": "#F1CE63", "good": "#59A14F", "neutral": "#4E79A7"},
    "gradient": ['#E15759', '#F28E2B', '#F1CE63', '#59A14F'],
}

DIMENSIONS = {
    "School Environment & Participation": [
        "common_vision_and_mission","sense_of_confidence_in_management","autonomy_as_professional_teacher",
        "feedback_on_performance","support_for_professional_development","co_curricular_activities",
        "authenticity_able_to_be_myself_at_school","influence_on_classroom_culture",
        "deep_engagement_in_teaching_process","respect_and_being_valued"
    ],
    "Learning (Others)": [
        "pedagogy_for_effective_performance","stimulating_sense_of_purpose_in_learners",
        "open_communication_on_non_school_topics","role_model_at_school"
    ],
    "Meaning (Self)": [
        "conviction_about_choice_of_career","fulfilment_derived_from_work","perceived_value_in_society_as_teacher",
        "proactive_teaching_approaches","pride_in_work","alignment_of_personal_and_school_values",
        "workload","creative_freedom_to_accomplish_work"
    ],
    "Income & Employment": [
        "income_and_earnings_to_meet_needs","remuneration_aligned_with_responsibilities","employment_contract",
        "access_to_credit_facilities","personal_savings","budgeting_and_planning","management_of_debt"
    ],
    "Health & Environment": [
        "nutrition","ability_to_deal_with_stress","physical_health_and_personal_hygiene","sleep","access_to_health_care",
        "caring_and_loving_relationships","family_unity","drugs_and_alcohol"
    ],
    "Home Environment & Community": [
        "house_structure","sanitation_and_sewage","electricity","separate_sleeping_spaces","stove_fridge_and_kitchen",
        "regular_means_of_transportation","distance_and_time_to_work","home_and_community_security"
    ],
    "Education & Culture": [
        "educational_opportunities","sensitivity_to_different_socio_economic_backgrounds","advice_and_mentorship",
        "social_networks"
    ],
    "Relationships": [
        "self_confidence","sense_of_belonging_inclusion","self_esteem_and_trust","effective_communication",
        "supportive_relationships_with_colleagues","influence_on_colleagues_and_school_culture",
        "reputation_with_colleagues_and_learners","ability_to_solve_problems_and_conflict"
    ],
    "Awareness & Emotions": [
        "joy_in_teaching","self_awareness","aspiration","motivated","sense_of_control","thriving"
    ],
}

ALL_ITEMS = [i for items in DIMENSIONS.values() for i in items]

# =========================
# Risk & Helper Functions
# =========================
def risk_bucket(score: float) -> str:
    if np.isnan(score): return "—"
    if score < 1.8: return "🚨 High Risk"
    if score < 2.2: return "⚠️ At Risk"
    if score < 2.6: return "⚡ Moderate"
    return "✅ Thriving"

def order_terms(values):
    order = {t: i for i, t in enumerate(TERMS)}
    return sorted(values, key=lambda t: order.get(t, 999))

def dimension_scores(df: pd.DataFrame) -> dict:
    out = {}
    for dim, items in DIMENSIONS.items():
        vals = df[items].values.flatten()
        out[dim] = float(np.mean(vals)) if len(vals) else float("nan")
    return out

# =========================
# Data Fetch
# =========================
@st.cache_data
def load_wellbeing_data() -> pd.DataFrame:
    if DatabaseManager:
        db = DatabaseManager()
        df = db.get_teacher_wellbeing()
        # ensure count columns exist
        for col in ("doing_well", "trying_but_struggling", "stuck"):
            if col not in df.columns:
                df[col] = 0
        return df

    # Fallback sample data
    st.info("Using sample data (DatabaseManager not available)")
    n = 100
    rng = np.random.default_rng(42)
    data = {
        "name_of_client": [f"Fellow_{i%20}" for i in range(n)],
        "term": rng.choice(TERMS, n),
        "date_of_survey": pd.date_range("2024-01-01", periods=n, freq="3D"),
        "phase": rng.choice(["Foundation", "Intermediate", "Senior"], n),
        "fellowship_year": rng.choice([1, 2], n),
        "name_of_facilitator": rng.choice(["Facilitator A", "Facilitator B", "Facilitator C"], n),
        "category": rng.choice(["Cat1", "Cat2"], n),
    }
    for item in ALL_ITEMS:
        data[item] = rng.integers(1, 4, n)  # 1..3

    df = pd.DataFrame(data)
    df["doing_well"] = (df[ALL_ITEMS] == 3).sum(axis=1)
    df["trying_but_struggling"] = (df[ALL_ITEMS] == 2).sum(axis=1)
    df["stuck"] = (df[ALL_ITEMS] == 1).sum(axis=1)
    return df



