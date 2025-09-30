# pages/program_scale.py
# ------------------------------------------------------------
# Program Scale Component (Live Data / No Test Fixtures)
# Story: Scale & Reach → Growth Journey → Diverse & Representative
# Depends on: utils.supabase.database_manager.get_db()
# ------------------------------------------------------------

import streamlit as st
import pandas as pd
import numpy as np

from typing import Optional, Dict, Any, List

# Altair is optional; table fallback if missing
try:
    import altair as alt
    ALT_AVAILABLE = True
except Exception:
    ALT_AVAILABLE = False

# === Your existing helper (already in your repo) ===
from utils.supabase.database_manager import get_db


# -------------------------------
# Data Loading (Supabase)
# -------------------------------
@st.cache_data(show_spinner=False)
def _fetch_table_names() -> List[str]:
    """
    Best-effort discovery of available tables/views to enable graceful fallbacks.
    Requires PostgREST schema browsing to be enabled. If not, we’ll just guess.
    """
    try:
        sb = get_db()
        # Some PostgREST installations expose / or rpc to list; if not, we catch and move on
        # We use a tiny probe: try a few common tables to see which respond.
        candidates = [
            "fellows",
            "academic_results",
            "classes",
            "program_stats_yearly",
        ]
        available = []
        for t in candidates:
            try:
                # lightweight select 1
                resp = sb.table(t).select("*", count="exact").range(0, 0).execute()
                if resp.data is not None:
                    available.append(t)
            except Exception:
                pass
        return available
    except Exception:
        return []


@st.cache_data(show_spinner=True)
def load_fellows_df() -> pd.DataFrame:
    """
    Loads fellows with key columns used by the component.
    Required table: public.fellows
    Expected columns (some optional):
      - id (uuid/text)
      - status (e.g., 'Active')
      - year_of_fellowship (int)
      - gender (text)
      - province_of_origin (text)
      - school_assignment_id (uuid/text)  # optional but used for school counts
      - year_of_entry (text/int)          # optional; used for growth if available
    """
    sb = get_db()
    cols = [
        "id",
        "status",
        "year_of_fellowship",
        "gender",
        "province_of_origin",
        "school_assignment_id",
        "year_of_entry",
    ]
    # Select only columns that exist; if select fails, we retry with fewer columns
    try:
        resp = sb.table("fellows").select(",".join(cols)).execute()
        df = pd.DataFrame(resp.data or [])
    except Exception:
        # Minimal must-haves
        fallback_cols = ["id", "status", "year_of_fellowship", "gender", "province_of_origin"]
        resp = sb.table("fellows").select(",".join(fallback_cols)).execute()
        df = pd.DataFrame(resp.data or [])
        # ensure optional columns exist (as NaN) for downstream code
        for c in set(cols) - set(df.columns):
            df[c] = pd.NA
    return df


@st.cache_data(show_spinner=True)
def load_learners_df() -> Optional[pd.DataFrame]:
    """
    Tries to load a dataframe that can yield class_size sums for total learners.
    Preferred tables/views (first hit wins):
      1) academic_results (expects column class_size)
      2) classes (expects column class_size)
    Returns None if nothing usable is found.
    """
    sb = get_db()
    table_order = [
        ("academic_results", ["class_size"]),
        ("classes", ["class_size"]),
    ]
    for table, need_cols in table_order:
        try:
            resp = sb.table(table).select(",".join(need_cols)).execute()
            df = pd.DataFrame(resp.data or [])
            if not df.empty and all(c in df.columns for c in need_cols):
                return df
        except Exception:
            continue
    return None


@st.cache_data(show_spinner=True)
def load_program_stats_yearly() -> Optional[pd.DataFrame]:
    """
    Optional: if you maintain a yearly stats table/view (program_stats_yearly) with:
      - year (int)
      - fellows (int)
      - provinces (int)
      - schools (int)  [optional]
    we’ll use it for the Growth Journey. Otherwise we’ll derive from fellows.
    """
    sb = get_db()
    try:
        resp = sb.table("program_stats_yearly").select("year,fellows,provinces,schools").order("year", desc=False).execute()
        df = pd.DataFrame(resp.data or [])
        if not df.empty and "year" in df.columns and "fellows" in df.columns:
            # ensure int typing if possible
            for c in ["year", "fellows", "provinces", "schools"]:
                if c in df.columns:
                    df[c] = pd.to_numeric(df[c], errors="coerce")
            df = df.sort_values("year")
            return df
    except Exception:
        pass
    return None


# -------------------------------
# Metrics
# -------------------------------
def calculate_program_scale_metrics(fellows_df: pd.DataFrame, learners_df: Optional[pd.DataFrame]) -> Dict[str, Any]:
    # Active filter
    active = fellows_df.copy()
    if "status" in fellows_df.columns:
        active = fellows_df[fellows_df["status"].str.lower() == "active"].copy()

    metrics = {
        "total_fellows": int(len(active)),
        "total_schools": int(active["school_assignment_id"].nunique()) if "school_assignment_id" in active.columns else None,
        "total_provinces": int(active["province_of_origin"].nunique()) if "province_of_origin" in active.columns else None,
        "year_1_fellows": int((active["year_of_fellowship"] == 1).sum()) if "year_of_fellowship" in active.columns else None,
        "year_2_fellows": int((active["year_of_fellowship"] == 2).sum()) if "year_of_fellowship" in active.columns else None,
        "female_count": int((active["gender"] == "Female").sum()) if "gender" in active.columns else None,
        "male_count": int((active["gender"] == "Male").sum()) if "gender" in active.columns else None,
        "total_learners": None,
        "total_classes": None,
    }

    if learners_df is not None and not learners_df.empty and "class_size" in learners_df.columns:
        metrics["total_learners"] = int(pd.to_numeric(learners_df["class_size"], errors="coerce").fillna(0).sum())
        metrics["total_classes"] = int(len(learners_df))

    return metrics


def build_growth_from_fellows(fellows_df: pd.DataFrame) -> Optional[pd.DataFrame]:
    """
    If you don’t have program_stats_yearly, we approximate growth by grouping fellows
    by year_of_entry (preferred) or by inferring from year_of_fellowship if possible.
    """
    df = fellows_df.copy()
    # Prefer explicit year_of_entry
    if "year_of_entry" in df.columns and df["year_of_entry"].notna().any():
        df["year"] = pd.to_numeric(df["year_of_entry"], errors="coerce")
    else:
        # Fallback heuristic: if you only have year_of_fellowship (1 or 2),
        # map to rough calendar years with assumption that current year is latest cohort year.
        # Adjust base year as needed.
        base_year = pd.Timestamp.today().year  # 2025 at time of writing
        if "year_of_fellowship" not in df.columns:
            return None
        # Assume Year 2 => base_year, Year 1 => base_year (same calendar), but you can tweak:
        df["year"] = base_year  # simplest; all current snapshot → one point
        # If you track alumni in fellows, you’ll get multiple years; if not, this will be single-point.

    grouped = []
    for y, g in df.groupby("year"):
        if pd.isna(y):
            continue
        fellows = int(g.shape[0])
        provinces = int(g["province_of_origin"].nunique()) if "province_of_origin" in g.columns else np.nan
        schools = int(g["school_assignment_id"].nunique()) if "school_assignment_id" in g.columns else np.nan
        grouped.append({"year": int(y), "fellows": fellows, "provinces": provinces, "schools": schools})

    if not grouped:
        return None

    out = pd.DataFrame(grouped).dropna(subset=["year"]).sort_values("year")
    # De-dup/aggregate if multiple entries per year_of_entry exist
    out = out.groupby("year", as_index=False).agg({"fellows": "sum", "provinces": "max", "schools": "max"})
    return out


# -------------------------------
# UI Rendering
# -------------------------------
def render_program_scale_story(fellows_df: pd.DataFrame, learners_df: Optional[pd.DataFrame], historical_data: Optional[pd.DataFrame] = None):
    st.markdown("## 📊 Program Scale & Reach")
    st.caption("The fellowship journey: From pioneers to a national movement")

    metrics = calculate_program_scale_metrics(fellows_df, learners_df)

    # === ARC 1: SCALE & REACH ===
    st.markdown("### 🎯 Current Active Cohort")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric("👥 Fellows", f"{metrics['total_fellows']:,}", help="Active fellows in the program")
        if metrics.get("year_1_fellows") is not None and metrics.get("year_2_fellows") is not None:
            st.caption(f"**{metrics['year_1_fellows']}** Year 1 • **{metrics['year_2_fellows']}** Year 2")

    with c2:
        st.metric("🏫 Schools", "-" if metrics["total_schools"] in (None, 0) else f"{metrics['total_schools']:,}",
                  help="Schools with fellow placements")

    with c3:
        st.metric("🌍 Provinces", "-" if metrics["total_provinces"] in (None, 0) else f"{metrics['total_provinces']}",
                  help="Provinces represented by fellows")

    with c4:
        learners_val = metrics["total_learners"]
        st.metric("🎓 Learners", "-" if learners_val in (None, 0) else f"{learners_val:,}",
                  help="Estimated learners reached (sum of class sizes)")

    # === ARC 2: GROWTH JOURNEY ===
    st.markdown("---")
    st.markdown("### 📈 Growth Trajectory")
    st.caption("Building a movement over time")

    hist = historical_data
    if hist is None or hist.empty:
        hist = build_growth_from_fellows(fellows_df)

    if hist is not None and not hist.empty:
        cL, cR = st.columns([2, 1])
        with cL:
            if ALT_AVAILABLE:
                upper = max(5, int(hist["fellows"].max() * 1.1))
                chart = (
                    alt.Chart(hist)
                    .mark_line(point=True, strokeWidth=3)
                    .encode(
                        x=alt.X("year:O", title="Year", axis=alt.Axis(labelAngle=0)),
                        y=alt.Y("fellows:Q", title="Number of Fellows", scale=alt.Scale(domain=[0, upper])),
                        tooltip=[
                            alt.Tooltip("year:O", title="Year"),
                            alt.Tooltip("fellows:Q", title="Fellows"),
                            alt.Tooltip("provinces:Q", title="Provinces"),
                            alt.Tooltip("schools:Q", title="Schools"),
                        ],
                    )
                    .properties(height=300)
                )
                st.altair_chart(chart, use_container_width=True)
            else:
                st.dataframe(hist, use_container_width=True)
        with cR:
            first_year = hist.iloc[0]
            last_year = hist.iloc[-1]
            growth = int(last_year["fellows"] - first_year["fellows"])
            growth_pct = (growth / max(1, int(first_year["fellows"])) * 100.0)
            st.metric("Fellows Growth", f"+{growth}", f"{growth_pct:.0f}% increase")
            if "provinces" in hist.columns and pd.notna(first_year.get("provinces", np.nan)) and pd.notna(last_year.get("provinces", np.nan)):
                st.metric(
                    "Provincial Expansion",
                    f"{int(first_year['provinces'])} → {int(last_year['provinces'])}",
                    f"+{int(last_year['provinces'] - first_year['provinces'])} provinces"
                )
            st.info(
                f"**{int(first_year['year'])}:** {int(first_year['fellows'])} fellows"
                + (f" in {int(first_year['provinces'])} province(s)" if pd.notna(first_year.get('provinces', np.nan)) else "")
                + f"\n\n**{int(last_year['year'])}:** {int(last_year['fellows'])} fellows"
                + (f" across {int(last_year['provinces'])} provinces" if pd.notna(last_year.get('provinces', np.nan)) else "")
            )
    else:
        st.info("💡 No historical series available yet. Add a `program_stats_yearly` table/view or ensure `year_of_entry` is populated in `fellows`.")

    # === ARC 3: DIVERSE & REPRESENTATIVE ===
    st.markdown("---")
    st.markdown("### 👥 Fellow Composition")
    st.caption("Who our fellows are: Gender diversity and geographic reach")

    # Split control
    split_option = st.radio(
        "View by:",
        ["Combined (All Fellows)", "Year 1", "Year 2", "Year 1 vs Year 2 Comparison"],
        horizontal=True,
        key="composition_split",
    )

    df = fellows_df.copy()
    if "status" in df.columns:
        df = df[df["status"].str.lower() == "active"].copy()

    if split_option == "Year 1":
        display_df = df[df["year_of_fellowship"] == 1].copy() if "year_of_fellowship" in df.columns else df.iloc[0:0].copy()
    elif split_option == "Year 2":
        display_df = df[df["year_of_fellowship"] == 2].copy() if "year_of_fellowship" in df.columns else df.iloc[0:0].copy()
    else:
        display_df = df

    c1, c2 = st.columns(2)

    # Gender
    with c1:
        st.markdown("#### Gender Distribution")
        if "gender" in display_df.columns and not display_df.empty:
            if split_option == "Year 1 vs Year 2 Comparison" and "year_of_fellowship" in display_df.columns:
                g = (
                    display_df.groupby(["year_of_fellowship", "gender"])
                    .size()
                    .reset_index(name="count")
                )
                if ALT_AVAILABLE and not g.empty:
                    chart = (
                        alt.Chart(g)
                        .mark_bar()
                        .encode(
                            x=alt.X("gender:N", title="Gender"),
                            y=alt.Y("count:Q", title="Number of Fellows"),
                            color=alt.Color("year_of_fellowship:N", title="Year", scale=alt.Scale(scheme="tableau10")),
                            xOffset="year_of_fellowship:N",
                            tooltip=["year_of_fellowship", "gender", "count"],
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.dataframe(g, use_container_width=True)
            else:
                g = (
                    display_df["gender"].value_counts(dropna=False)
                    .rename_axis("gender")
                    .reset_index(name="count")
                )
                g["percentage"] = (g["count"] / max(1, g["count"].sum()) * 100).round(1)
                if ALT_AVAILABLE and not g.empty:
                    chart = (
                        alt.Chart(g)
                        .mark_bar()
                        .encode(
                            x=alt.X("gender:N", title="Gender"),
                            y=alt.Y("count:Q", title="Number of Fellows"),
                            color=alt.Color("gender:N", legend=None),
                            tooltip=["gender", "count", "percentage"],
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.dataframe(g, use_container_width=True)

                try:
                    female_pct = float(g.loc[g["gender"] == "Female", "percentage"].values[0])
                    st.caption(f"**{female_pct:.0f}%** of fellows are women")
                except Exception:
                    pass
        else:
            st.info("Gender data not available")

    # Province
    with c2:
        st.markdown("#### Province of Origin")
        if "province_of_origin" in display_df.columns and not display_df.empty:
            if split_option == "Year 1 vs Year 2 Comparison" and "year_of_fellowship" in display_df.columns:
                p = (
                    display_df.groupby(["year_of_fellowship", "province_of_origin"])
                    .size()
                    .reset_index(name="count")
                )
                if ALT_AVAILABLE and not p.empty:
                    chart = (
                        alt.Chart(p)
                        .mark_bar()
                        .encode(
                            y=alt.Y("province_of_origin:N", title="Province", sort="-x"),
                            x=alt.X("count:Q", title="Number of Fellows"),
                            color=alt.Color("year_of_fellowship:N", title="Year", scale=alt.Scale(scheme="tableau10")),
                            yOffset="year_of_fellowship:N",
                            tooltip=["year_of_fellowship", "province_of_origin", "count"],
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.dataframe(p, use_container_width=True)
            else:
                p = (
                    display_df["province_of_origin"].value_counts(dropna=False)
                    .rename_axis("province")
                    .reset_index(name="count")
                )
                if ALT_AVAILABLE and not p.empty:
                    chart = (
                        alt.Chart(p)
                        .mark_bar()
                        .encode(
                            y=alt.Y("province:N", title="Province", sort="-x"),
                            x=alt.X("count:Q", title="Number of Fellows"),
                            color=alt.Color("province:N", legend=None),
                            tooltip=["province", "count"],
                        )
                        .properties(height=300)
                    )
                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.dataframe(p, use_container_width=True)

                if not p.empty:
                    top_row = p.iloc[0]
                    st.caption(f"**{top_row['province']}** has the most fellows ({int(top_row['count'])})")
        else:
            st.info("Province data not available")

    # Story summary
    st.markdown("---")
    t_f = metrics.get("total_fellows")
    f_c = metrics.get("female_count")
    t_l = metrics.get("total_learners")
    t_s = metrics.get("total_schools")
    if t_f:
        if f_c is not None and t_f > 0:
            female_pct = (f_c / t_f) * 100
            learners_txt = f"{t_l:,}" if isinstance(t_l, int) and t_l > 0 else "—"
            schools_txt = f"{t_s}" if isinstance(t_s, int) and t_s > 0 else "—"
            st.success(
                f"💡 **Fellowship Impact:** {t_f} diverse educators "
                f"({female_pct:.0f}% women) reaching **{learners_txt}** learners across **{schools_txt}** schools."
            )
        else:
            st.success(f"💡 **Fellowship Impact:** {t_f} diverse educators reaching learners across South Africa.")


# -------------------------------
# Page Entrypoint
# -------------------------------
def main():
    st.set_page_config(page_title="Program Scale", page_icon="📊", layout="wide")
    st.title("Program Scale Component")

    available = _fetch_table_names()
    if "fellows" not in available:
        st.error("Table `fellows` is required for this component.")
        st.stop()

    fellows_df = load_fellows_df()
    learners_df = load_learners_df()
    yearly_df = load_program_stats_yearly()

    if fellows_df.empty:
        st.warning("No fellows found. Check your Supabase connection/filters.")
        st.stop()

    render_program_scale_story(fellows_df, learners_df, yearly_df)


if __name__ == "__main__":
    main()
