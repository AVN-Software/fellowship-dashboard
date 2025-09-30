# dash/fellow_wellbeing/fellow_wellbeing_dashboard.py
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import io
import sys

# --- make repo root importable ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

# External filters/topbar (your existing component)
import components.filters as fx

# Utils
from pages.teacher_wellbeing.utils import (
    TERMS, ALL_ITEMS, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX,
    load_wellbeing_data, risk_bucket, order_terms, dimension_scores
)

# Reuse your tab modules (we will render them in sections)
from pages.teacher_wellbeing.tabs import (
    overview,
    progression,
    domains,
    indicators,
    risk,
    fellows,
    data
)

# =========================
# Page Config
# =========================
st.set_page_config(
    page_title="Fellow Wellbeing Survey — Report View",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================
# Data
# =========================
df_surveys: pd.DataFrame = load_wellbeing_data()

# =========================
# Header & Filters
# =========================
fx.topbar(
    "🌱 Fellow Wellbeing Survey — Report",
    "Holistic wellbeing across terms with domain, indicator, and risk insights"
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


# =========================
# Report Recorder (Markdown + CSV exports)
# =========================
class ReportRecorder:
    def __init__(self):
        self.md_chunks: list[str] = []
        self.csv_namedframes: dict[str, pd.DataFrame] = {}

    def md(self, text: str):
        st.markdown(text)
        self.md_chunks.append(text if text.endswith("\n") else text + "\n")

    def hr(self): 
        st.write("---")
        self.md_chunks.append("\n---\n")

    def add_csv(self, name: str, df: pd.DataFrame):
        if isinstance(df, pd.DataFrame) and not df.empty:
            self.csv_namedframes[name] = df.copy()

    def export_markdown(self) -> bytes:
        return "".join(self.md_chunks).encode("utf-8")

    def export_zip_csv(self) -> bytes:
        # Create a simple zip of CSVs in-memory
        import zipfile, time
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for name, df in self.csv_namedframes.items():
                csv_bytes = df.to_csv(index=False).encode("utf-8")
                safe = name.replace(" ", "_")[:50] + ".csv"
                zf.writestr(safe, csv_bytes)
        buf.seek(0)
        return buf.getvalue()

rec = ReportRecorder()

# =========================
# Helper: quick insights from domains (comparative across terms)
# =========================
def _dim_scores_by_term(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or not set(["term"]).issubset(df.columns):
        return pd.DataFrame(columns=["Domain", "term", "Score"])
    rows = []
    for t, sub in df.groupby("term"):
        scores = dimension_scores(sub)
        for d, s in scores.items():
            rows.append({"Domain": d, "term": t, "Score": s})
    return pd.DataFrame(rows)

def _ordered_terms_in_df(df: pd.DataFrame):
    if "term" not in df.columns: return []
    present = sorted(df["term"].dropna().unique(), key=lambda t: {"Term 1":0,"Term 2":1,"Term 3":2}.get(t, 99))
    return present

def _domain_delta_table(by_term: pd.DataFrame, base: str, second: str) -> pd.DataFrame:
    if by_term.empty: return pd.DataFrame()
    wide = by_term.pivot_table(index="Domain", columns="term", values="Score", aggfunc="mean")
    for t in (base, second):
        if t not in wide.columns:
            wide[t] = np.nan
    wide["Delta (Second–Base)"] = wide[second] - wide[base]
    wide = wide.reset_index()
    return wide

# =========================
# Static preface
# =========================
st.caption("Scoring: 1 = Struggling · 2 = Coping · 3 = Confident • 63 indicators")
st.divider()

# =========================
# Table of Contents
# =========================
rec.md("## Table of Contents")
rec.md("""
- [1. Executive Summary](#1-executive-summary)
- [2. Domain Performance (Comparative)](#2-domain-performance-comparative)
- [3. Indicator Drilldown + Baseline vs Second](#3-indicator-drilldown--baseline-vs-second)
- [4. At-Risk Snapshot](#4-at-risk-snapshot)
- [5. Fellows Spotlight](#5-fellows-spotlight)
- [6. Data Appendix](#6-data-appendix)
""")
rec.hr()

# =========================
# 1) Executive Summary
# =========================
rec.md("## 1. Executive Summary")
if filtered.empty:
    rec.md("_No data available for selected filters._")
else:
    n_rows = len(filtered)
    terms_present = _ordered_terms_in_df(filtered)
    uniq_fellows = filtered["name_of_client"].nunique() if "name_of_client" in filtered.columns else None

    by_term = _dim_scores_by_term(filtered)
    rec.add_csv("Domain_Scores_by_Term", by_term)

    # simple KPIs row
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Records", n_rows)
    with c2: st.metric("Terms in View", len(terms_present))
    with c3: st.metric("Unique Fellows", uniq_fellows if uniq_fellows is not None else 0)
    with c4:
        overall = filtered[ALL_ITEMS].to_numpy().astype(float)
        overall = overall[~np.isnan(overall)]
        st.metric("Overall Avg Score", f"{np.mean(overall):.2f}" if overall.size else "—")

    # Top movers insight (if 2+ terms)
    if len(terms_present) >= 2:
        base, second = terms_present[0], terms_present[1]
        delta = _domain_delta_table(by_term, base, second)
        rec.add_csv("Domain_Delta_Table", delta)
        movers = delta.dropna(subset=["Delta (Second–Base)"]).sort_values("Delta (Second–Base)", ascending=False)
        improvers = movers.head(3)
        decliners = movers.tail(3)

        st.markdown("**Key Movements (Second − Base)**")
        cL, cR = st.columns(2)
        with cL:
            if not improvers.empty:
                for _, r in improvers.iterrows():
                    st.caption(f"• **{r['Domain']}**: +{r['Delta (Second–Base)']:.2f}")
            else:
                st.caption("• No improvements to highlight.")
        with cR:
            if not decliners.empty:
                for _, r in decliners.iterrows():
                    st.caption(f"• **{r['Domain']}**: {r['Delta (Second–Base)']:.2f}")
            else:
                st.caption("• No declines to highlight.")
    else:
        st.caption("_Add another term to see comparative movements._")

rec.hr()

# =========================
# 2) Domain Performance (Comparative)
# =========================
rec.md("## 2. Domain Performance (Comparative)")
# Reuse your upgraded domains module (comparative with charts + change table + insights)
domains.render(filtered, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX)
rec.hr()

# =========================
# 3) Indicator Drilldown + Baseline vs Second
# =========================
rec.md("## 3. Indicator Drilldown + Baseline vs Second")
# Uses your indicators module (drilldown + the Baseline vs Second section we added)
indicators.render(filtered, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX)
rec.hr()

# =========================
# 4) At-Risk Snapshot
# =========================
rec.md("## 4. At-Risk Snapshot")
risk.render(filtered, ALL_ITEMS, COLORS, risk_bucket)
rec.hr()

# =========================
# 5) Fellows Spotlight
# =========================
rec.md("## 5. Fellows Spotlight")
fellows.render(filtered, DIMENSIONS, COLORS, SCORE_MIN, SCORE_MAX, risk_bucket)
rec.hr()

# =========================
# 6) Data Appendix
# =========================
rec.md("## 6. Data Appendix")
data.render(filtered, ALL_ITEMS, risk_bucket)
rec.hr()

# =========================
# Export / Download
# =========================
st.subheader("⬇️ Export")
md_bytes = rec.export_markdown()
st.download_button(
    "Download Report (Markdown)",
    data=md_bytes,
    file_name="fellow_wellbeing_report.md",
    mime="text/markdown",
    use_container_width=True
)

zip_bytes = rec.export_zip_csv()
st.download_button(
    "Download Key Tables (CSV ZIP)",
    data=zip_bytes,
    file_name="fellow_wellbeing_report_tables.zip",
    mime="application/zip",
    use_container_width=True
)

st.caption("🌱 Fellow Wellbeing Survey • Report view • Streamlit")
