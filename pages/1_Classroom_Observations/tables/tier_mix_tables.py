# enhanced_tier_analysis/tables/tier_mix_tables.py
import re
import pandas as pd
import streamlit as st

from ..analysis import summaries, movement


# ---------- Tier Mix Analysis (SPLIT BY TERM) ----------
def create_tier_mix_table(df: pd.DataFrame, segment_col: str):
    """
    Render Tier Mix Analysis split into separate subtables by TERM.
    Each subtable shows: Tier 1%, Tier 2%, Tier 3%, Index (optionally per-segment columns).
    Uses the raw df to guarantee we can group by 'term', regardless of summary structure.
    """
    if df is None or df.empty:
        st.info("No data available for Tier Mix Analysis.")
        return

    # Validate needed columns
    required = {"domain", "term", "tier_mix_t1_pct", "tier_mix_t2_pct", "tier_mix_t3_pct", "dominant_index"}
    missing = [c for c in required if c not in df.columns]
    if missing:
        st.warning(f"Missing columns for Tier Mix Analysis: {', '.join(missing)}")
        return

    # Sort terms numerically if labeled like "Term 1", "Term 2", ...
    def _term_key(t: str) -> int:
        m = re.search(r"\d+", str(t))
        return int(m.group()) if m else 0

    terms = sorted(df["term"].dropna().unique(), key=_term_key)
    if not terms:
        st.info("No terms found.")
        return

    st.subheader("Tier Mix Analysis by Term")

    # Common styling
    def _highlight_cells(styler: pd.io.formats.style.Styler):
        def _apply(data: pd.DataFrame) -> pd.DataFrame:
            styles = pd.DataFrame("", index=data.index, columns=data.columns)
            for col in data.columns:
                if "Tier 3%" in col:
                    # Highest Tier 3 is best
                    max_val = pd.to_numeric(data[col], errors="coerce").max()
                    styles.loc[data[col] == max_val, col] = "background-color: #d4edda; font-weight: 600"
                elif "Tier 1%" in col:
                    # Lowest Tier 1 is best
                    min_val = pd.to_numeric(data[col], errors="coerce").min()
                    styles.loc[data[col] == min_val, col] = "background-color: #fff3cd"
                elif "Index" in col:
                    num = pd.to_numeric(data[col], errors="coerce")
                    styles.loc[num >= 2.5, col] = "background-color: #d1ecf1"
            return styles
        return styler.apply(_apply, axis=None)

    def _fmt_for(table: pd.DataFrame):
        fmt = {}
        for c in table.columns:
            if "%" in c:
                fmt[c] = "{:.1f}%"
            elif "Index" in c:
                fmt[c] = "{:.2f}"
        return fmt

    def _term_subtable(term_value: str) -> pd.DataFrame:
        """Build a single term subtable (optionally segmented)."""
        subset = df[df["term"] == term_value]
        if subset.empty:
            return pd.DataFrame()

        # Aggregate: per domain (and per segment, if specified)
        if segment_col and segment_col != "both" and segment_col in subset.columns:
            grp = subset.groupby(["domain", segment_col]).agg(
                t1=("tier_mix_t1_pct", "mean"),
                t2=("tier_mix_t2_pct", "mean"),
                t3=("tier_mix_t3_pct", "mean"),
                idx=("dominant_index", "mean"),
            ).round(1)

            # Pivot to columns like "<segment> Tier 1%", "<segment> Tier 2%", ...
            wide = grp.unstack(segment_col)
            # Flatten multiindex columns
            wide.columns = [f"{lvl2} {label}".strip() for (label, lvl2) in wide.columns]
            # Rename metric labels inside names
            wide = wide.rename(columns={
                "t1": "Tier 1%",
                "t2": "Tier 2%",
                "t3": "Tier 3%",
                "idx": "Index"
            })
            # After rename, ensure final names make sense:
            wide.columns = [c.replace("t1", "Tier 1%").replace("t2", "Tier 2%").replace("t3", "Tier 3%").replace("idx", "Index")
                            for c in wide.columns]

            # Sort domains by Tier 3 average across segments (desc)
            t3_cols = [c for c in wide.columns if "Tier 3%" in c]
            if t3_cols:
                wide = wide.assign(_t3avg=wide[t3_cols].mean(axis=1)).sort_values("_t3avg", ascending=False).drop(columns="_t3avg")

            return wide

        else:
            # Overall (no segmentation)
            wide = subset.groupby("domain").agg(
                **{
                    "Tier 1%": ("tier_mix_t1_pct", "mean"),
                    "Tier 2%": ("tier_mix_t2_pct", "mean"),
                    "Tier 3%": ("tier_mix_t3_pct", "mean"),
                    "Index": ("dominant_index", "mean"),
                }
            ).round(1)

            # Sort by Tier 3 desc
            if "Tier 3%" in wide.columns:
                wide = wide.sort_values("Tier 3%", ascending=False)

            return wide

    # Render a subtable for each term
    for term in terms:
        st.markdown(f"**{term}**")
        table = _term_subtable(term)
        if table.empty:
            st.info(f"No data for {term}.")
            continue

        styled = table.style.pipe(_highlight_cells).format(_fmt_for(table))
        st.dataframe(styled, use_container_width=True)

        # Quick insights for each term (based on Tier 3 column(s))
        _show_term_insights(table, term)

    st.caption("Legend: Green = best Tier 3 · Yellow = best Tier 1 (lowest) · Blue = high Index (≥2.5)")


def _show_term_insights(table: pd.DataFrame, term_label: str):
    """Small callouts per term table, keyed off Tier 3% columns."""
    t3_cols = [c for c in table.columns if "Tier 3%" in c]
    if not t3_cols:
        return

    # If multiple Tier 3 columns (segmented), take the mean across them for ranking
    if len(t3_cols) > 1:
        t3_series = table[t3_cols].mean(axis=1, skipna=True)
    else:
        t3_series = table[t3_cols[0]]

    best_domain = t3_series.idxmax()
    best_val = t3_series.loc[best_domain]

    worst_domain = t3_series.idxmin()
    worst_val = t3_series.loc[worst_domain]

    html = f"""
    <style>
      .ins-card {{
        padding: 12px 14px; border-radius: 6px; margin: 6px 0 14px 0;
        box-shadow: 0 1px 3px rgba(0,0,0,.08); font-family: "Segoe UI","Helvetica Neue",sans-serif;
      }}
      .ins-good {{ background:#eaf7ea; border-left:6px solid #28a745; }}
      .ins-bad  {{ background:#fbeaea; border-left:6px solid #dc3545; }}
      .ins-title {{ margin:0 0 4px 0; font-weight:600; font-size:14px; }}
      .ins-body  {{ margin:0; font-size:13px; color:#333; }}
    </style>
    <div class="ins-card ins-good">
      <p class="ins-title">{term_label} — Top Performer (Tier 3)</p>
      <p class="ins-body"><b>{best_domain}</b> — {best_val:.1f}%</p>
    </div>
    <div class="ins-card ins-bad">
      <p class="ins-title">{term_label} — Needs Focus (Tier 3)</p>
      <p class="ins-body"><b>{worst_domain}</b> — {worst_val:.1f}%</p>
    </div>
    """
    st.markdown(html, unsafe_allow_html=True)


# ---------- Movement Analysis Table ----------
def create_movement_analysis(df: pd.DataFrame, segment_col: str):
    """
    Professional Movement Analysis table with semantic highlighting.
    Expects movement.calculate_movements to return readable labels (e.g., 'Improvement', 'Decline', 'Stable').
    """
    movement_df = movement.calculate_movements(df, segment_col)

    if movement_df is None or movement_df.empty:
        st.info("No data available for Movement Analysis.")
        return

    def highlight_movement(styler: pd.io.formats.style.Styler):
        def _apply_colors(data: pd.DataFrame) -> pd.DataFrame:
            styles = pd.DataFrame("", index=data.index, columns=data.columns)
            for col in data.columns:
                if "Movement" in col:
                    improve = data[col].astype(str).str.contains("Improvement", na=False)
                    decline = data[col].astype(str).str.contains("Decline", na=False)
                    stable = data[col].astype(str).str.contains("Stable", na=False)
                    styles.loc[improve, col] = "background-color: #d4edda; font-weight: 600"
                    styles.loc[decline, col] = "background-color: #f8d7da"
                    styles.loc[stable, col] = "background-color: #fff3cd"
                elif "Change" in col and "%" in col:
                    plus = data[col].astype(str).str.contains(r"\+", na=False)
                    minus = data[col].astype(str).str.contains(r"-", na=False)
                    styles.loc[plus, col] = "color: #28a745; font-weight: 600"
                    styles.loc[minus, col] = "color: #dc3545; font-weight: 600"
            return styles
        return styler.apply(_apply_colors, axis=None)

    styled = movement_df.style.pipe(highlight_movement)
    st.dataframe(styled, use_container_width=True)
    st.caption("Green: Improvement · Red: Decline · Yellow: Stable")


# ---------- Domain Performance Summary (unchanged, single latest-term view) ----------
def show_domain_performance_table(df: pd.DataFrame, segment_col: str, tier_focus: str = "All Tiers"):
    """
    Domain performance summary (latest term): shows Tier 1%, Tier 2%, Tier 3%, Index.
    Kept as-is; if you want this split by term as well, call create_tier_mix_table instead.
    """
    if df is None or df.empty:
        st.info("No data for domain summary.")
        return

    def _term_sort_key(t: str) -> int:
        m = re.search(r"\d+", str(t))
        return int(m.group()) if m else 0

    terms = sorted(df["term"].dropna().unique(), key=_term_sort_key)
    if not terms:
        st.info("No terms found.")
        return

    latest_term = terms[-1]
    latest_df = df[df["term"] == latest_term].copy()
    if latest_df.empty:
        st.info("No rows in latest term.")
        return

    # Overall or segmented
    if segment_col and segment_col != "both" and segment_col in df.columns:
        summary = (
            latest_df.groupby(["domain", segment_col])
            .agg(
                t1=("tier_mix_t1_pct", "mean"),
                t2=("tier_mix_t2_pct", "mean"),
                t3=("tier_mix_t3_pct", "mean"),
                idx=("dominant_index", "mean"),
            )
            .round(1)
        ).unstack(segment_col)
        summary.columns = [f"{seg} {m}".replace("t1", "Tier 1%").replace("t2", "Tier 2%").replace("t3", "Tier 3%").replace("idx", "Index")
                           for (m, seg) in summary.columns]
    else:
        summary = (
            latest_df.groupby("domain")
            .agg(
                **{
                    "Tier 1%": ("tier_mix_t1_pct", "mean"),
                    "Tier 2%": ("tier_mix_t2_pct", "mean"),
                    "Tier 3%": ("tier_mix_t3_pct", "mean"),
                    "Index": ("dominant_index", "mean"),
                }
            )
            .round(1)
        )

    # Style
    def _highlight(styler: pd.io.formats.style.Styler):
        def _apply(data: pd.DataFrame) -> pd.DataFrame:
            styles = pd.DataFrame("", index=data.index, columns=data.columns)
            for col in data.columns:
                if "Tier 3%" in col:
                    max_val = pd.to_numeric(data[col], errors="coerce").max()
                    styles.loc[data[col] == max_val, col] = "background-color: #d4edda; font-weight: 600"
                elif "Tier 1%" in col:
                    min_val = pd.to_numeric(data[col], errors="coerce").min()
                    styles.loc[data[col] == min_val, col] = "background-color: #fff3cd"
                elif "Index" in col:
                    num = pd.to_numeric(data[col], errors="coerce")
                    styles.loc[num >= 2.5, col] = "background-color: #d1ecf1"
            return styles
        return styler.apply(_apply, axis=None)

    st.subheader(f"Domain Performance Summary (Latest Term: {latest_term})")
    st.dataframe(summary.style.pipe(_highlight).format(_auto_fmt(summary)), use_container_width=True)
    st.caption("Legend: Green = best Tier 3 · Yellow = best Tier 1 (lowest) · Blue = high Index (≥2.5)")


# ---------- Helpers ----------
def _auto_fmt(table: pd.DataFrame):
    fmt = {}
    for c in table.columns:
        if isinstance(c, tuple):
            label = " ".join(str(x) for x in c)
        else:
            label = str(c)
        if "%" in label:
            fmt[c] = "{:.1f}%"
        elif "Index" in label:
            fmt[c] = "{:.2f}"
    return fmt


# ---------- Backwards compatibility alias ----------
def create_tier_mix_table_legacy(df: pd.DataFrame, segment_col: str):
    """Legacy function name for backwards compatibility."""
    return create_tier_mix_table(df, segment_col)
