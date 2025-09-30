# filters.py
from __future__ import annotations
import streamlit as st
from typing import Iterable, Dict, Any, Optional

GLOBAL_KEY = "global_filters"

# ---- low-level helpers (render to a target; default is st.sidebar)
def _multiselect(label: str, options: Iterable, default: Iterable, key: str, target=None):
    target = target or st.sidebar
    return target.multiselect(label, options=list(options), default=list(default), key=key)

def _radio(label: str, options: Iterable, key: str, horizontal: bool = True, index: int = 0, target=None):
    target = target or st.sidebar
    return target.radio(label, options=list(options), index=index, horizontal=horizontal, key=key)

def reset_button(label: str = "♻️ Reset filters", key: Optional[str] = None, target=None) -> bool:
    target = target or st.sidebar
    return target.button(label, use_container_width=True, key=key)

# ---- top bar (page header area)
def topbar(title: str, subtitle: Optional[str] = None, right_nodes: Optional[Dict[str, Any]] = None):
    c1, c2 = st.columns([6, 2], vertical_alignment="center")
    with c1:
        st.markdown(f"## {title}")
        if subtitle:
            st.caption(subtitle)
    with c2:
        if right_nodes:
            for label in right_nodes.keys():
                st.button(label, use_container_width=True)

# ---- global filters
def ensure_global_filters():
    if GLOBAL_KEY not in st.session_state:
        st.session_state[GLOBAL_KEY] = {"cycle_year": [], "terms": [], "coaches": []}

def reset_global_filters():
    if GLOBAL_KEY in st.session_state:
        del st.session_state[GLOBAL_KEY]
    ensure_global_filters()

def write_global_filters(target=None) -> Dict[str, Any]:
    """Renders Cycle Year, Term, Coach in the SIDEBAR (by default)."""
    target = target or st.sidebar
    ensure_global_filters()

    target.markdown("### 🌐 Global Filters")
    target.caption("These filters apply across the entire app.")

    opts = st.session_state.get(
        "global_filter_options",
        {
            "cycle_year": [2021, 2022, 2023, 2024, 2025],
            "terms": ["Term 1", "Term 2", "Term 3", "Term 4"],
            "coaches": [
                "Angie Nord", "Cindy Gamanie", "Robin Williams", "Correta Mkansi",
                "Bruce Oom", "Jo-anne Dreyer", "Tonia van Wyk",
            ],
        },
    )

    gf = st.session_state[GLOBAL_KEY]
    gf["cycle_year"] = _multiselect("Cycle Year", opts["cycle_year"], gf.get("cycle_year", []), "gf_cycle_year", target)
    gf["terms"]      = _multiselect("Term",        opts["terms"],      gf.get("terms", []),      "gf_terms",      target)
    gf["coaches"]    = _multiselect("Coach",       opts["coaches"],    gf.get("coaches", []),    "gf_coaches",    target)

    st.session_state[GLOBAL_KEY] = gf
    target.markdown("---")
    return gf

# ---- page-local filters: observations
def write_observation_filters(term_options: Iterable[str], subjects: Iterable[str], grades: Iterable[str], target=None) -> Dict[str, Any]:
    target = target or st.sidebar
    target.markdown("### 🎛️ Observation Filters")
    target.caption("Applies to the Observations dashboard.")

    flt_terms    = _multiselect("Term", term_options, term_options, "obs_terms", target)
    flt_subjects = _multiselect("Subject", sorted(set(subjects)), sorted(set(subjects)), "obs_subjects", target)

    try:
        grade_sorted = sorted(set(grades), key=lambda x: int(str(x).split()[-1]))
    except Exception:
        grade_sorted = sorted(set(grades))
    flt_grades = _multiselect("Grade", grade_sorted, grade_sorted, "obs_grades", target)

    flt_year = _radio("Fellowship Year", ["Both", "Year 1", "Year 2"], "obs_year", True, 0, target)

    target.markdown("---")
    return {"terms": flt_terms, "subjects": flt_subjects, "grades": flt_grades, "year": flt_year}

# ---- page-local filters: academic
def write_academic_filters(subjects: Iterable[str], phases: Iterable[str], grades: Iterable[str], target=None) -> Dict[str, Any]:
    target = target or st.sidebar
    target.markdown("### 🎛️ Academic Filters")
    target.caption("Applies to the Academic Results dashboard.")

    flt_subjects = _multiselect("Subject", sorted(set(subjects)), sorted(set(subjects)), "acad_subjects", target)
    flt_phases   = _multiselect("Phase",   sorted(set(phases)),   sorted(set(phases)),   "acad_phases",   target)

    try:
        grade_sorted = sorted(set(grades), key=lambda x: int(str(x).split()[-1]))
    except Exception:
        grade_sorted = sorted(set(grades))
    flt_grades = _multiselect("Grade", grade_sorted, grade_sorted, "acad_grades", target)

    target.markdown("---")
    return {"subjects": flt_subjects, "phases": flt_phases, "grades": flt_grades}

# ---- page-local filters: wellbeing
def write_wellbeing_filters(df, terms: Iterable[str], target=None) -> Dict[str, Any]:
    target = target or st.sidebar
    target.markdown("### 🎛️ Wellbeing Filters")
    target.caption("Applies to all Wellbeing tabs.")

    phase_opts = sorted(df["phase"].dropna().unique().tolist()) if "phase" in df else []
    fac_opts   = sorted(df["name_of_facilitator"].dropna().unique().tolist()) if "name_of_facilitator" in df else []

    flt_terms        = _multiselect("Term", list(terms), list(terms), "wb_terms", target)
    flt_phase        = _multiselect("School Phase", phase_opts, phase_opts, "wb_phase", target)
    flt_year         = _radio("Fellowship Year", ["Both", "Year 1", "Year 2"], "wb_year", True, 0, target)
    flt_facilitators = _multiselect("Facilitator", fac_opts, fac_opts, "wb_facilitators", target)

    target.markdown("---")
    return {"terms": flt_terms, "phase": flt_phase, "year": flt_year, "facilitators": flt_facilitators}
