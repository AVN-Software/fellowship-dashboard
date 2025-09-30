# pages/Enhanced_Tier_Progression.py
from __future__ import annotations
import streamlit as st
import pandas as pd
import numpy as np
from typing import Optional, Dict, Any

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ---- repo-root import for database manager ----
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

try:
    from utils.supabase.database_manager import get_db
except Exception as e:
    get_db = None
    st.warning(f"Could not import DatabaseManager: {e}")

TERM_ORDER = ["Term 1", "Term 2", "Term 3", "Term 4"]

class EnhancedTierProgressionPage:
    """Comprehensive Tier progression analysis using materialized view data."""

    def __init__(self):
        # Harmonized domain palette (matches app)
        self.domain_colors = {
            "LE":  "#59A14F",
            "SE":  "#4E79A7",
            "KPC": "#9C755F",
            "AII": "#E15759",
            "IAL": "#F28E2B",
            "IAN": "#76B7B2",
        }
        self.tier_colors = {
            "Tier 1": "#E15759",
            "Tier 2": "#F1CE63",
            "Tier 3": "#59A14F",
        }

    # -----------------------------
    # Page entry
    # -----------------------------
    def render(self, df: Optional[pd.DataFrame]):
        st.set_page_config(page_title="Advanced Tier Progression", page_icon="📈", layout="wide")
        st.title("📈 Advanced Tier Progression Analysis")
        st.caption("Materialized view: mv_comprehensive_tier_analysis")

        # Validate data
        if df is None or df.empty:
            st.error("No materialized view data available. Ensure mv_comprehensive_tier_analysis is populated and RLS allows read.")
            return

        # Normalize/prepare columns
        df = self._prepare(df)

        # -----------------------------
        # Top bar filters
        # -----------------------------
        toolbar = st.container()
        with toolbar:
            st.markdown("### 🎛️ Filters")
            c1, c2, c3, c4, c5 = st.columns([1.3, 1.3, 1.3, 1.1, 0.8])

            # Segment selection
            segment_choice = c1.selectbox(
                "Segment",
                ["Overall", "School Level", "Fellowship Year", "Both"],
                index=0,
                key="tier_seg",
            )
            segment_map = {
                "Overall": None,
                "School Level": "school_level",
                "Fellowship Year": "fellow_year",
                "Both": "both",
            }
            segment_col = segment_map[segment_choice]

            # Domains
            domains = sorted(df["domain"].dropna().unique().tolist())
            sel_domains = c2.multiselect(
                "Domains",
                options=domains,
                default=domains,
                key="tier_domains",
            )

            # Terms
            terms_present = [t for t in TERM_ORDER if t in df["term"].unique()]
            sel_terms = c3.multiselect(
                "Terms",
                options=terms_present,
                default=terms_present,
                key="tier_terms",
            )

            # Analysis type
            analysis_type = c4.selectbox(
                "Analysis",
                ["Tier Mix Evolution", "Performance Trends", "Strategic Analysis", "Comparative Analysis"],
                index=0,
                key="tier_analysis",
            )

            if c5.button("♻️ Reset", use_container_width=True):
                for k in list(st.session_state.keys()):
                    if k.startswith("tier_"):
                        del st.session_state[k]
                st.rerun()

        # Apply filters
        work = df.copy()
        if sel_domains:
            work = work[work["domain"].isin(sel_domains)]
        if sel_terms:
            work = work[work["term"].isin(sel_terms)]

        if work.empty:
            st.warning("No rows after applying filters.")
            return

        # Dispatch to analysis
        if analysis_type == "Tier Mix Evolution":
            self._render_tier_mix_analysis(work, segment_col)
        elif analysis_type == "Performance Trends":
            self._render_performance_trends(work, segment_col)
        elif analysis_type == "Strategic Analysis":
            self._render_strategic_analysis(work, segment_col)
        elif analysis_type == "Comparative Analysis":
            self._render_comparative_analysis(work, segment_col)

    # -----------------------------
    # Prep
    # -----------------------------
    def _prepare(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        # Expected columns from the MV:
        # term, domain, fellow_year OR fellowship_year, school_level,
        # tier_mix_t1_pct, tier_mix_t2_pct, tier_mix_t3_pct,
        # domain_avg, dominant_index,
        # avg_tier_score_t1, avg_tier_score_t2, avg_tier_score_t3
        # strongest_tier, weakest_tier, strongest_index, weakest_index

        # Map fellowship_year→fellow_year if needed; convert to "Year X"
        if "fellow_year" not in df.columns and "fellowship_year" in df.columns:
            df["fellow_year"] = df["fellowship_year"]
        df["fellow_year"] = df.get("fellow_year")
        if "fellow_year" in df.columns:
            df["fellow_year"] = df["fellow_year"].apply(
                lambda x: f"Year {int(x)}" if pd.notna(x) else None
            )

        # Ensure term order
        if "term" in df.columns:
            df["term"] = pd.Categorical(df["term"], categories=TERM_ORDER, ordered=True)

        # Coerce numeric fields (ignore missing)
        for col in [
            "tier_mix_t1_pct", "tier_mix_t2_pct", "tier_mix_t3_pct",
            "domain_avg", "dominant_index",
            "avg_tier_score_t1", "avg_tier_score_t2", "avg_tier_score_t3",
        ]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Domain codes cleanup: sometimes "IA" sneaks in → split Literacy/Numeracy if present
        df["domain"] = df["domain"].replace({"IA": "IAL"})  # prefer IAL (if your MV uses IA, change mapping here)

        return df

    # -----------------------------
    # Tier Mix Evolution
    # -----------------------------
    def _render_tier_mix_analysis(self, df: pd.DataFrame, segment_col: Optional[str]):
        st.header("🎯 Tier Mix Evolution")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("📊 Tier 3% Progression by Domain")
            self._create_tier3_progression(df, segment_col)
        with c2:
            st.subheader("📈 Dominant Index Progression")
            self._create_dominant_index_chart(df, segment_col)

        st.subheader("📋 Detailed Tier Mix Analysis")
        self._create_tier_mix_table(df, segment_col)

        st.subheader("🔄 Term-to-Term Movement Analysis")
        self._create_movement_analysis(df, segment_col)

    def _create_tier3_progression(self, df: pd.DataFrame, segment_col: Optional[str]):
        fig = go.Figure()

        if segment_col and segment_col != "both":
            for seg in sorted(df[segment_col].dropna().unique()):
                seg_df = df[df[segment_col] == seg]
                for dom in sorted(seg_df["domain"].dropna().unique()):
                    dom_df = (
                        seg_df[seg_df["domain"] == dom]
                        .groupby("term", as_index=False)["tier_mix_t3_pct"]
                        .mean()
                        .sort_values("term")
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=dom_df["term"], y=dom_df["tier_mix_t3_pct"],
                            mode="lines+markers",
                            name=f"{dom} ({seg})",
                            line=dict(color=self.domain_colors.get(dom, "#888888")),
                        )
                    )
        else:
            for dom in sorted(df["domain"].dropna().unique()):
                dom_df = (
                    df[df["domain"] == dom]
                    .groupby("term", as_index=False)["tier_mix_t3_pct"]
                    .mean()
                    .sort_values("term")
                )
                fig.add_trace(
                    go.Scatter(
                        x=dom_df["term"], y=dom_df["tier_mix_t3_pct"],
                        mode="lines+markers",
                        name=dom,
                        line=dict(color=self.domain_colors.get(dom, "#888888")),
                    )
                )

        fig.update_layout(
            height=420,
            yaxis_title="Tier 3 (%)",
            xaxis_title="Term",
            hovermode="x unified",
            yaxis=dict(range=[0, 100]),
        )
        st.plotly_chart(fig, use_container_width=True)

    def _create_dominant_index_chart(self, df: pd.DataFrame, segment_col: Optional[str]):
        fig = go.Figure()

        if segment_col and segment_col != "both":
            for seg in sorted(df[segment_col].dropna().unique()):
                seg_df = df[df[segment_col] == seg]
                for dom in sorted(seg_df["domain"].dropna().unique()):
                    dom_df = (
                        seg_df[seg_df["domain"] == dom]
                        .groupby("term", as_index=False)["dominant_index"]
                        .mean()
                        .sort_values("term")
                    )
                    fig.add_trace(
                        go.Scatter(
                            x=dom_df["term"], y=dom_df["dominant_index"],
                            mode="lines+markers",
                            name=f"{dom} ({seg})",
                            line=dict(color=self.domain_colors.get(dom, "#888888")),
                        )
                    )
        else:
            for dom in sorted(df["domain"].dropna().unique()):
                dom_df = (
                    df[df["domain"] == dom]
                    .groupby("term", as_index=False)["dominant_index"]
                    .mean()
                    .sort_values("term")
                )
                fig.add_trace(
                    go.Scatter(
                        x=dom_df["term"], y=dom_df["dominant_index"],
                        mode="lines+markers",
                        name=dom,
                        line=dict(color=self.domain_colors.get(dom, "#888888")),
                    )
                )

        fig.add_hline(y=2.0, line_dash="dash", line_color="gray", annotation_text="Balanced (2.0)")
        fig.add_hline(y=2.5, line_dash="dash", line_color="green", annotation_text="Strong (2.5)")
        fig.update_layout(height=420, yaxis_title="Dominant Index", xaxis_title="Term", yaxis=dict(range=[1.0, 3.0]))
        st.plotly_chart(fig, use_container_width=True)

    def _create_tier_mix_table(self, df: pd.DataFrame, segment_col: Optional[str]):
        rows = []
        def add_row(frame: pd.DataFrame, domain: str, segment: str):
            g = (
                frame.groupby("term", as_index=False)[
                    ["tier_mix_t1_pct", "tier_mix_t2_pct", "tier_mix_t3_pct", "dominant_index"]
                ]
                .mean()
                .sort_values("term")
            )
            terms = g["term"].tolist()
            if len(terms) < 2:
                return
            row = {"Domain": domain, "Segment": segment}
            for _, r in g.iterrows():
                t = r["term"]
                row[f"{t} T1%"] = r["tier_mix_t1_pct"]
                row[f"{t} T2%"] = r["tier_mix_t2_pct"]
                row[f"{t} T3%"] = r["tier_mix_t3_pct"]
                row[f"{t} Index"] = r["dominant_index"]
            first, last = terms[0], terms[-1]
            r1 = g[g["term"] == first].iloc[0]
            r2 = g[g["term"] == last].iloc[0]
            row["T3 Change"] = r2["tier_mix_t3_pct"] - r1["tier_mix_t3_pct"]
            row["Index Change"] = r2["dominant_index"] - r1["dominant_index"]
            rows.append(row)

        if segment_col and segment_col != "both":
            for dom in sorted(df["domain"].dropna().unique()):
                dom_df = df[df["domain"] == dom]
                for seg in sorted(dom_df[segment_col].dropna().unique()):
                    add_row(dom_df[dom_df[segment_col] == seg], dom, str(seg))
        else:
            for dom in sorted(df["domain"].dropna().unique()):
                add_row(df[df["domain"] == dom], dom, "Overall")

        if rows:
            out = pd.DataFrame(rows)
            st.dataframe(
                out.style.format({c: "{:.1f}%" for c in out.columns if c.endswith("%")})
                        .format({c: "{:.2f}" for c in out.columns if c.endswith("Index") or "Change" in c}),
                use_container_width=True,
                hide_index=True,
            )

    def _create_movement_analysis(self, df: pd.DataFrame, segment_col: Optional[str]):
        moves = []
        def add_moves(frame: pd.DataFrame, domain: str, segment: str):
            g = (
                frame.groupby("term", as_index=False)[["tier_mix_t3_pct", "dominant_index"]]
                .mean()
                .sort_values("term")
            )
            terms = g["term"].tolist()
            for i in range(len(terms)-1):
                a, b = terms[i], terms[i+1]
                r1 = g[g["term"] == a].iloc[0]; r2 = g[g["term"] == b].iloc[0]
                d_t3 = r2["tier_mix_t3_pct"] - r1["tier_mix_t3_pct"]
                d_idx = r2["dominant_index"] - r1["dominant_index"]
                movement = "📈 Improvement" if d_t3 > 2 else ("📉 Decline" if d_t3 < -2 else "➡️ Stable")
                moves.append({
                    "Domain": domain, "Segment": segment, "Period": f"{a} → {b}",
                    "T3 Change": f"{d_t3:+.1f}%", "Index Change": f"{d_idx:+.2f}", "Movement": movement
                })

        if segment_col and segment_col != "both":
            for dom in sorted(df["domain"].dropna().unique()):
                dom_df = df[df["domain"] == dom]
                for seg in sorted(dom_df[segment_col].dropna().unique()):
                    add_moves(dom_df[dom_df[segment_col] == seg], dom, str(seg))
        else:
            for dom in sorted(df["domain"].dropna().unique()):
                add_moves(df[df["domain"] == dom], dom, "Overall")

        if moves:
            st.dataframe(pd.DataFrame(moves), use_container_width=True, hide_index=True)

    # -----------------------------
    # Performance Trends
    # -----------------------------
    def _render_performance_trends(self, df: pd.DataFrame, segment_col: Optional[str]):
        st.header("📊 Performance Trends Analysis")

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🎯 Domain Performance Evolution (Avg)")
            self._create_domain_performance_chart(df)
        with c2:
            st.subheader("🏆 Tier Performance Scores")
            self._create_tier_performance_chart(df)

        st.subheader("🔥 Performance Heatmap")
        self._create_performance_heatmap(df)

        st.subheader("💪 Recovery & Resilience Analysis")
        self._create_recovery_analysis(df)

    def _create_domain_performance_chart(self, df: pd.DataFrame):
        fig = go.Figure()
        for dom in sorted(df["domain"].dropna().unique()):
            dom_df = (
                df[df["domain"] == dom]
                .groupby("term", as_index=False)["domain_avg"]
                .mean()
                .sort_values("term")
            )
            fig.add_trace(
                go.Scatter(
                    x=dom_df["term"], y=dom_df["domain_avg"],
                    mode="lines+markers", name=dom,
                    line=dict(color=self.domain_colors.get(dom, "#888888")),
                )
            )
        # Domain averages are on a 1–4 scale in your app
        fig.update_layout(height=420, yaxis_title="Average Domain Score", xaxis_title="Term",
                          yaxis=dict(range=[1.0, 4.0]))
        st.plotly_chart(fig, use_container_width=True)

    def _create_tier_performance_chart(self, df: pd.DataFrame):
        fig = make_subplots(rows=1, cols=3, subplot_titles=["Tier 1", "Tier 2", "Tier 3"])
        for i, col in enumerate(["avg_tier_score_t1", "avg_tier_score_t2", "avg_tier_score_t3"], start=1):
            for dom in sorted(df["domain"].dropna().unique()):
                dom_df = (
                    df[df["domain"] == dom]
                    .groupby("term", as_index=False)[col]
                    .mean()
                    .sort_values("term")
                )
                fig.add_trace(
                    go.Scatter(
                        x=dom_df["term"], y=dom_df[col], mode="lines+markers",
                        name=dom, line=dict(color=self.domain_colors.get(dom, "#888888")),
                        showlegend=(i == 1),
                    ),
                    row=1, col=i,
                )
        fig.update_layout(height=420, yaxis=dict(range=[1.0, 4.0]), title="Tier Performance Scores by Domain")
        st.plotly_chart(fig, use_container_width=True)

    def _create_performance_heatmap(self, df: pd.DataFrame):
        heat = (
            df.groupby(["domain", "term"], as_index=False)["domain_avg"]
            .mean().pivot(index="domain", columns="term", values="domain_avg")
        )
        fig = go.Figure(
            data=go.Heatmap(z=heat.values, x=heat.columns, y=heat.index, colorscale="RdYlGn",
                            colorbar=dict(title="Avg Score (1–4)"))
        )
        fig.update_layout(height=420, xaxis_title="Term", yaxis_title="Domain")
        st.plotly_chart(fig, use_container_width=True)

    def _create_recovery_analysis(self, df: pd.DataFrame):
        rows = []
        for dom in sorted(df["domain"].dropna().unique()):
            d = df[df["domain"] == dom]
            t1 = d[d["term"] == "Term 1"]["domain_avg"].mean()
            t2 = d[d["term"] == "Term 2"]["domain_avg"].mean()
            t3 = d[d["term"] == "Term 3"]["domain_avg"].mean()
            if not np.isnan(t1) and not np.isnan(t2) and not np.isnan(t3):
                decline = t2 - t1
                recovery = t3 - t2
                net = t3 - t1
                tag = "🚀 Exceptional" if recovery > 0.25 else ("💪 Strong" if recovery > 0.15 else ("📈 Moderate" if recovery > 0 else "📉 Continued Decline"))
                rows.append({
                    "Domain": dom,
                    "T1": f"{t1:.2f}", "T2": f"{t2:.2f}", "T3": f"{t3:.2f}",
                    "T1→T2": f"{decline:+.2f}", "T2→T3": f"{recovery:+.2f}",
                    "Net": f"{net:+.2f}", "Recovery": tag
                })
        if rows:
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

    # -----------------------------
    # Strategic Analysis
    # -----------------------------
    def _render_strategic_analysis(self, df: pd.DataFrame, segment_col: Optional[str]):
        st.header("🎯 Strategic Analysis")
        c1, c2 = st.columns(2)
        with c1:
            st.subheader("🎪 Strategic Positioning")
            self._create_strategic_positioning_chart(df)
        with c2:
            st.subheader("⚡ Tier Strength Analysis")
            self._create_tier_strength_analysis(df, segment_col)

        st.subheader("🔍 Pattern Recognition")
        self._create_pattern_analysis(df)

        st.subheader("💡 Strategic Insights")
        self._create_strategic_recommendations(df)

    def _create_strategic_positioning_chart(self, df: pd.DataFrame):
        fig = go.Figure()
        for dom in sorted(df["domain"].dropna().unique()):
            d = df[df["domain"] == dom]
            fig.add_trace(go.Scatter(
                x=d["dominant_index"], y=d["domain_avg"],
                mode="markers+text", text=d["term"], textposition="top center",
                name=dom,
                marker=dict(
                    size=(d["tier_mix_t3_pct"].fillna(0) / 2.0).clip(4, 24),
                    color=self.domain_colors.get(dom, "#888888")
                ),
            ))
        fig.add_vline(x=2.0, line_dash="dash", line_color="gray")
        fig.add_hline(y=3.0, line_dash="dash", line_color="gray")
        fig.update_layout(
            height=460,
            xaxis_title="Dominant Index (1–3)",
            yaxis_title="Domain Performance (1–4)",
            xaxis=dict(range=[1.5, 3.0]),
            yaxis=dict(range=[1.0, 4.0]),
        )
        st.plotly_chart(fig, use_container_width=True)

    def _create_tier_strength_analysis(self, df: pd.DataFrame, segment_col: Optional[str]):
        rows = []
        for _, r in df.iterrows():
            ts = (
                (r.get("avg_tier_score_t1", np.nan) * r.get("tier_mix_t1_pct", 0) / 100 * 1) +
                (r.get("avg_tier_score_t2", np.nan) * r.get("tier_mix_t2_pct", 0) / 100 * 2) +
                (r.get("avg_tier_score_t3", np.nan) * r.get("tier_mix_t3_pct", 0) / 100 * 3)
            ) / 3
            rows.append({
                "Domain": r["domain"],
                "Term": r["term"],
                "Tier Strength": ts,
                "Segment": (r.get(segment_col) if segment_col and segment_col != "both" else "Overall")
            })
        if rows:
            df_ts = pd.DataFrame(rows)
            fig = px.bar(
                df_ts, x="Term", y="Tier Strength", color="Domain",
                facet_col=("Segment" if (segment_col and segment_col != "both") else None),
                title="Tier Strength Evolution (Performance × Distribution)"
            )
            st.plotly_chart(fig, use_container_width=True)

    def _create_pattern_analysis(self, df: pd.DataFrame):
        st.markdown("### Patterns")
        notes = []
        for dom in sorted(df["domain"].dropna().unique()):
            d = (
                df[df["domain"] == dom]
                .groupby("term", as_index=False)["tier_mix_t3_pct"]
                .mean()
                .sort_values("term")
            )
            if len(d) >= 3:
                a, b, c = d["tier_mix_t3_pct"].iloc[0:3]
                if b < a and c > b:
                    notes.append(f"📈 **{dom}**: U-shape recovery ({a:.0f}% → {b:.0f}% → {c:.0f}%).")
                elif c > b > a:
                    notes.append(f"🚀 **{dom}**: Consistent growth ({a:.0f}% → {b:.0f}% → {c:.0f}%).")
                elif a > b > c:
                    notes.append(f"📉 **{dom}**: Steady decline ({a:.0f}% → {b:.0f}% → {c:.0f}%).")
                elif abs(a - c) < 5:
                    notes.append(f"➡️ **{dom}**: Stable performance ({a:.0f}% ~ {c:.0f}%).")
                else:
                    notes.append(f"📊 **{dom}**: Volatile pattern.")
        if notes:
            for n in notes:
                st.markdown(f"- {n}")

    def _create_strategic_recommendations(self, df: pd.DataFrame):
        latest_term = df["term"].dropna().max()
        cur = df[df["term"] == latest_term]
        if cur.empty:
            st.info("No latest term records to recommend on.")
            return
        best = cur.loc[cur["tier_mix_t3_pct"].idxmax()]
        worst = cur.loc[cur["tier_mix_t3_pct"].idxmin()]
        st.markdown(
            f"- 🏆 **Replicate Success**: {best['domain']} strong Tier 3 share (**{best['tier_mix_t3_pct']:.0f}%**)."
        )
        st.markdown(
            f"- 🎯 **Focus Area**: {worst['domain']} lower Tier 3 (**{worst['tier_mix_t3_pct']:.0f}%**). Plan targeted support."
        )

    # -----------------------------
    # Comparative Analysis
    # -----------------------------
    def _render_comparative_analysis(self, df: pd.DataFrame, segment_col: Optional[str]):
        st.header("⚖️ Comparative Analysis")
        if not segment_col or segment_col == "both":
            st.info("Select **School Level** or **Fellowship Year** in the Segment filter to compare.")
            return

        # Box by segment
        fig = px.box(
            df, x=segment_col, y="domain_avg", color="domain",
            title=f"Performance Distribution by {segment_col.replace('_',' ').title()}",
        )
        fig.update_layout(yaxis=dict(range=[1.0, 4.0]))
        st.plotly_chart(fig, use_container_width=True)

        # Progression rate scatter
        rows = []
        for seg in sorted(df[segment_col].dropna().unique()):
            seg_df = df[df[segment_col] == seg]
            for dom in sorted(seg_df["domain"].dropna().unique()):
                d = (
                    seg_df[seg_df["domain"] == dom]
                    .groupby("term", as_index=False)["tier_mix_t3_pct"]
                    .mean()
                    .sort_values("term")
                )
                if len(d) >= 2:
                    start, end = d["tier_mix_t3_pct"].iloc[0], d["tier_mix_t3_pct"].iloc[-1]
                    rows.append({
                        "Segment": seg, "Domain": dom,
                        "Starting T3%": start, "Ending T3%": end,
                        "Total Change": end - start, "Progression Rate": (end - start) / (len(d) - 1),
                    })
        if rows:
            prog = pd.DataFrame(rows)
            fig2 = px.scatter(
                prog, x="Starting T3%", y="Ending T3%", size="Total Change", color="Segment",
                hover_data=["Domain", "Progression Rate"],
                title="Progression Trajectories by Segment",
            )
            fig2.add_shape(type="line", x0=0, y0=0, x1=100, y1=100, line=dict(color="gray", dash="dash"))
            st.plotly_chart(fig2, use_container_width=True)
            st.dataframe(
                prog.style.format({
                    "Progression Rate": "{:.2f}%/term",
                    "Starting T3%": "{:.1f}%", "Ending T3%": "{:.1f}%",
                    "Total Change": "{:+.1f}%",
                }),
                use_container_width=True, hide_index=True,
            )

# -----------------------------
# Bootstrapping and data fetch
# -----------------------------
def load_tier_mv() -> pd.DataFrame:
    if get_db is None:
        return pd.DataFrame()
    db = get_db()
    # This must read your materialized view:
    return db.get_tier_analysis()

def main():
    df = load_tier_mv()
    page = EnhancedTierProgressionPage()
    page.render(df)

if __name__ == "__main__":
    main()
