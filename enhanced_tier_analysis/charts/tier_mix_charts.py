import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

from ..analysis import summaries, movement


def create_tier_distribution_chart(df: pd.DataFrame, segment_col: str, domain_colors: dict):
    """Tier distribution with option for stacked bar or panel view."""
 
    view_type = st.radio("Choose visualization style:", ["Stacked Bar", "Panels by Tier"], key="tier_dist_view")

    # --- Aggregate data ---
    if segment_col and segment_col != "both":
        agg = (
            df.groupby(['term', segment_col])[['tier_mix_t1_pct', 'tier_mix_t2_pct', 'tier_mix_t3_pct']]
            .mean()
            .reset_index()
        )
    else:
        agg = (
            df.groupby('term')[['tier_mix_t1_pct', 'tier_mix_t2_pct', 'tier_mix_t3_pct']]
            .mean()
            .reset_index()
        )

    # --- View A: Stacked Bar ---
    if view_type == "Stacked Bar":
        melt_df = agg.melt(
            id_vars=['term'] + ([segment_col] if segment_col and segment_col != "both" else []),
            value_vars=['tier_mix_t1_pct', 'tier_mix_t2_pct', 'tier_mix_t3_pct'],
            var_name='Tier',
            value_name='Percentage'
        )
        melt_df['Tier'] = melt_df['Tier'].map({
            'tier_mix_t1_pct': 'Tier 1',
            'tier_mix_t2_pct': 'Tier 2',
            'tier_mix_t3_pct': 'Tier 3'
        })

        fig = px.bar(
            melt_df,
            x="term",
            y="Percentage",
            color="Tier",
            barmode="stack",
            facet_col=segment_col if (segment_col and segment_col != "both") else None,
            category_orders={"Tier": ["Tier 1", "Tier 2", "Tier 3"]},
            title="Tier Mix Evolution (Stacked Bar)"
        )

        fig.update_layout(yaxis_title="Percentage", xaxis_title="Term", hovermode="x unified")
        st.plotly_chart(fig, use_container_width=True)

    # --- View B: Panels by Tier ---
    else:
        fig = make_subplots(
            rows=1, cols=3,
            subplot_titles=["Tier 1", "Tier 2", "Tier 3"],
            shared_xaxes=True, shared_yaxes=True
        )

        tier_map = {
            "Tier 1": "tier_mix_t1_pct",
            "Tier 2": "tier_mix_t2_pct",
            "Tier 3": "tier_mix_t3_pct"
        }

        for i, (tier_name, col) in enumerate(tier_map.items(), 1):
            if segment_col and segment_col != "both":
                for seg_val in sorted(agg[segment_col].unique()):
                    seg_data = agg[agg[segment_col] == seg_val]
                    fig.add_trace(
                        go.Bar(
                            x=seg_data['term'],
                            y=seg_data[col],
                            name=f"{tier_name} ({seg_val})",
                            showlegend=(i == 1)
                        ),
                        row=1, col=i
                    )
            else:
                fig.add_trace(
                    go.Bar(
                        x=agg['term'],
                        y=agg[col],
                        name=tier_name,
                        showlegend=(i == 1)
                    ),
                    row=1, col=i
                )

        fig.update_layout(
            title="Tier Distribution Panels",
            yaxis_title="Percentage",
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)


def create_dominant_index_chart(df: pd.DataFrame, segment_col: str, domain_colors: dict):
    """Create dominant index progression chart."""
    fig = go.Figure()

    if segment_col and segment_col != "both":
        for segment_val in sorted(df[segment_col].unique()):
            segment_data = df[df[segment_col] == segment_val]

            for domain in sorted(segment_data['domain'].unique()):
                domain_data = segment_data[segment_data['domain'] == domain]

                fig.add_trace(go.Scatter(
                    x=domain_data['term'],
                    y=domain_data['dominant_index'],
                    mode='lines+markers',
                    name=f"{domain} ({segment_val})",
                    line=dict(color=domain_colors.get(domain, '#888888'))
                ))
    else:
        for domain in sorted(df['domain'].unique()):
            domain_data = df[df['domain'] == domain].groupby('term')['dominant_index'].mean().reset_index()

            fig.add_trace(go.Scatter(
                x=domain_data['term'],
                y=domain_data['dominant_index'],
                mode='lines+markers',
                name=domain,
                line=dict(color=domain_colors.get(domain, '#888888'))
            ))

    fig.add_hline(y=2.0, line_dash="dash", line_color="gray", annotation_text="Balanced (2.0)")
    fig.add_hline(y=2.5, line_dash="dash", line_color="green", annotation_text="Strong (2.5)")

    fig.update_layout(
        title="Dominant Index Evolution (Higher = Better Tier Distribution)",
        xaxis_title="Term",
        yaxis_title="Dominant Index",
        yaxis=dict(range=[1.0, 3.0])
    )

    st.plotly_chart(fig, use_container_width=True)


