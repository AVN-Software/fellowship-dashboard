import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st
import numpy as np
from typing import Optional, Dict, Any


class EnhancedTierProgressionPage:
    """Comprehensive Tier progression analysis using materialized view data."""

    def __init__(self):
        self.tier_colors = {
            'Tier 1': '#FF6B6B',  # Red - needs improvement
            'Tier 2': '#4ECDC4',  # Teal - progressing
            'Tier 3': '#45B7D1'   # Blue - strong performance
        }
        self.domain_colors = {
            'AII': '#FF9999',
            'IA': '#66B2FF', 
            'KPC': '#99FF99',
            'LE': '#FFCC99',
            'SE': '#FF99CC'
        }

    def render(self, df: Optional[pd.DataFrame], raw_df: Optional[pd.DataFrame] = None,
               config: Dict[str, Any] = None):
        st.title("📈 Advanced Tier Progression Analysis")
        st.caption("Comprehensive analysis of tier progression using pre-computed metrics from materialized view")

        if df is None or df.empty:
            st.error("No materialized view data available.")
            return

        # Sidebar controls
        with st.sidebar:
            st.header("🎛️ Analysis Controls")
            
            # Segment selection
            segment_options = {
                "Overall": None,
                "School Level": "school_level", 
                "Fellowship Year": "fellow_year",
                "Both": "both"
            }
            segment_choice = st.selectbox("Segment Analysis", list(segment_options.keys()))
            segment_col = segment_options[segment_choice]
            
            # Domain selection
            available_domains = sorted(df['domain'].unique()) if 'domain' in df.columns else []
            selected_domains = st.multiselect(
                "Select Domains", 
                available_domains, 
                default=available_domains,
                key="domain_filter"
            )
            
            # Analysis type
            analysis_type = st.radio(
                "Analysis Focus",
                ["Tier Mix Evolution", "Performance Trends", "Strategic Analysis", "Comparative Analysis"],
                key="analysis_type"
            )

        # Filter data
        filtered_df = df[df['domain'].isin(selected_domains)] if selected_domains else df

        # Main analysis dispatch
        if analysis_type == "Tier Mix Evolution":
            self._render_tier_mix_analysis(filtered_df, segment_col)
        elif analysis_type == "Performance Trends":
            self._render_performance_trends(filtered_df, segment_col)
        elif analysis_type == "Strategic Analysis":
            self._render_strategic_analysis(filtered_df, segment_col)
        elif analysis_type == "Comparative Analysis":
            self._render_comparative_analysis(filtered_df, segment_col)

    def _render_tier_mix_analysis(self, df: pd.DataFrame, segment_col: str):
        """Analyze tier mix evolution across terms."""
        st.header("🎯 Tier Mix Evolution")
        
        # Aggregate data if needed
        if segment_col == "both":
            group_cols = ['term', 'domain', 'school_level', 'fellow_year']
        elif segment_col:
            group_cols = ['term', 'domain', segment_col]
        else:
            group_cols = ['term', 'domain']
            
        # Create tier progression charts
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📊 Tier Distribution Over Time")
            self._create_tier_distribution_chart(df, segment_col)
            
        with col2:
            st.subheader("📈 Dominant Index Progression")
            self._create_dominant_index_chart(df, segment_col)
        
        # Tier mix table with progression indicators
        st.subheader("📋 Detailed Tier Mix Analysis")
        self._create_tier_mix_table(df, segment_col)
        
        # Movement analysis
        st.subheader("🔄 Term-to-Term Movement Analysis")
        self._create_movement_analysis(df, segment_col)

    def _render_performance_trends(self, df: pd.DataFrame, segment_col: str):
        """Analyze performance trends across tiers and terms."""
        st.header("📊 Performance Trends Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎯 Domain Performance Evolution")
            self._create_domain_performance_chart(df, segment_col)
            
        with col2:
            st.subheader("🏆 Tier Performance Scores")
            self._create_tier_performance_chart(df, segment_col)
        
        # Performance heatmap
        st.subheader("🔥 Performance Heatmap")
        self._create_performance_heatmap(df, segment_col)
        
        # Recovery analysis
        st.subheader("💪 Recovery & Resilience Analysis")
        self._create_recovery_analysis(df, segment_col)

    def _render_strategic_analysis(self, df: pd.DataFrame, segment_col: str):
        """Strategic insights and pattern analysis."""
        st.header("🎯 Strategic Analysis")
        
        # Strategic positioning
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🎪 Strategic Positioning")
            self._create_strategic_positioning_chart(df, segment_col)
            
        with col2:
            st.subheader("⚡ Tier Strength Analysis")
            self._create_tier_strength_analysis(df, segment_col)
        
        # Pattern recognition
        st.subheader("🔍 Pattern Recognition")
        self._create_pattern_analysis(df, segment_col)
        
        # Strategic recommendations
        st.subheader("💡 Strategic Insights")
        self._create_strategic_recommendations(df, segment_col)

    def _render_comparative_analysis(self, df: pd.DataFrame, segment_col: str):
        """Comparative analysis across segments."""
        st.header("⚖️ Comparative Analysis")
        
        if not segment_col or segment_col == "both":
            st.info("Select a specific segment (School Level or Fellowship Year) for comparative analysis.")
            return
            
        # Segment comparison
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader(f"📊 Performance by {segment_col.replace('_', ' ').title()}")
            self._create_segment_comparison_chart(df, segment_col)
            
        with col2:
            st.subheader("🏃‍♂️ Progression Rates")
            self._create_progression_rate_analysis(df, segment_col)
        
        # Statistical significance testing
        st.subheader("📈 Trend Analysis")
        self._create_trend_analysis(df, segment_col)

    # Chart creation methods
    def _create_tier_distribution_chart(self, df: pd.DataFrame, segment_col: str):
        """Create stacked area chart for tier distribution."""
        # Prepare data for stacked area chart
        if segment_col and segment_col != "both":
            fig = make_subplots(
                rows=len(df[segment_col].unique()), cols=1,
                subplot_titles=[f"{segment_col.replace('_', ' ').title()}: {val}" 
                              for val in sorted(df[segment_col].unique())],
                shared_xaxes=True, vertical_spacing=0.1
            )
            
            for i, segment_val in enumerate(sorted(df[segment_col].unique()), 1):
                segment_data = df[df[segment_col] == segment_val]
                
                for domain in sorted(segment_data['domain'].unique()):
                    domain_data = segment_data[segment_data['domain'] == domain]
                    
                    fig.add_trace(
                        go.Scatter(
                            x=domain_data['term'],
                            y=domain_data['tier_mix_t3_pct'],
                            mode='lines+markers',
                            name=f"{domain} - Tier 3",
                            line=dict(color=self.domain_colors.get(domain, '#888888')),
                            showlegend=(i == 1)
                        ),
                        row=i, col=1
                    )
        else:
            # Overall view
            fig = go.Figure()
            
            for domain in sorted(df['domain'].unique()):
                domain_data = df[df['domain'] == domain].groupby('term').agg({
                    'tier_mix_t1_pct': 'mean',
                    'tier_mix_t2_pct': 'mean', 
                    'tier_mix_t3_pct': 'mean'
                }).reset_index()
                
                fig.add_trace(go.Scatter(
                    x=domain_data['term'],
                    y=domain_data['tier_mix_t3_pct'],
                    mode='lines+markers',
                    name=f"{domain} - Tier 3",
                    line=dict(color=self.domain_colors.get(domain, '#888888'))
                ))
        
        fig.update_layout(
            title="Tier 3 Progression by Domain",
            xaxis_title="Term",
            yaxis_title="Tier 3 Percentage",
            hovermode='x unified'
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _create_dominant_index_chart(self, df: pd.DataFrame, segment_col: str):
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
                        line=dict(color=self.domain_colors.get(domain, '#888888'))
                    ))
        else:
            for domain in sorted(df['domain'].unique()):
                domain_data = df[df['domain'] == domain].groupby('term')['dominant_index'].mean().reset_index()
                
                fig.add_trace(go.Scatter(
                    x=domain_data['term'],
                    y=domain_data['dominant_index'],
                    mode='lines+markers',
                    name=domain,
                    line=dict(color=self.domain_colors.get(domain, '#888888'))
                ))
        
        fig.add_hline(y=2.0, line_dash="dash", line_color="gray", 
                      annotation_text="Balanced (2.0)")
        fig.add_hline(y=2.5, line_dash="dash", line_color="green", 
                      annotation_text="Strong (2.5)")
        
        fig.update_layout(
            title="Dominant Index Evolution (Higher = Better Tier Distribution)",
            xaxis_title="Term",
            yaxis_title="Dominant Index",
            yaxis=dict(range=[1.0, 3.0])
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _create_tier_mix_table(self, df: pd.DataFrame, segment_col: str):
        """Create detailed tier mix table with progression indicators."""
        if segment_col and segment_col != "both":
            pivot_cols = ['domain', segment_col]
        else:
            pivot_cols = ['domain']
            
        # Create summary table
        summary_data = []
        
        for domain in sorted(df['domain'].unique()):
            domain_data = df[df['domain'] == domain]
            
            if segment_col and segment_col != "both":
                for segment_val in sorted(domain_data[segment_col].unique()):
                    seg_data = domain_data[domain_data[segment_col] == segment_val]
                    self._add_progression_row(summary_data, seg_data, domain, segment_val)
            else:
                agg_data = domain_data.groupby('term').agg({
                    'tier_mix_t1_pct': 'mean',
                    'tier_mix_t2_pct': 'mean',
                    'tier_mix_t3_pct': 'mean',
                    'dominant_index': 'mean'
                }).reset_index()
                self._add_progression_row(summary_data, agg_data, domain)
        
        summary_df = pd.DataFrame(summary_data)
        
        # Style the dataframe
        if not summary_df.empty:
            st.dataframe(
                summary_df.style.format({
                    col: '{:.1f}%' for col in summary_df.columns if 'pct' in col or 'T' in col
                }).format({
                    col: '{:.2f}' for col in summary_df.columns if 'index' in col.lower()
                }),
                use_container_width=True
            )

    def _add_progression_row(self, summary_data: list, data: pd.DataFrame, domain: str, segment_val: str = None):
        """Add a progression row to summary data."""
        terms = sorted(data['term'].unique())
        
        if len(terms) < 2:
            return
            
        row = {
            'Domain': domain,
            'Segment': segment_val or 'Overall'
        }
        
        # Add term-specific data
        for term in terms:
            term_data = data[data['term'] == term].iloc[0] if len(data[data['term'] == term]) > 0 else None
            if term_data is not None:
                row[f'{term} T1%'] = term_data['tier_mix_t1_pct']
                row[f'{term} T2%'] = term_data['tier_mix_t2_pct'] 
                row[f'{term} T3%'] = term_data['tier_mix_t3_pct']
                row[f'{term} Index'] = term_data['dominant_index']
        
        # Calculate changes
        if len(terms) >= 2:
            first_term = data[data['term'] == terms[0]].iloc[0]
            last_term = data[data['term'] == terms[-1]].iloc[0]
            
            row['T3 Change'] = last_term['tier_mix_t3_pct'] - first_term['tier_mix_t3_pct']
            row['Index Change'] = last_term['dominant_index'] - first_term['dominant_index']
        
        summary_data.append(row)

    def _create_movement_analysis(self, df: pd.DataFrame, segment_col: str):
        """Analyze term-to-term movements."""
        movement_data = []
        
        for domain in sorted(df['domain'].unique()):
            domain_data = df[df['domain'] == domain].sort_values('term')
            
            if segment_col and segment_col != "both":
                for segment_val in sorted(domain_data[segment_col].unique()):
                    seg_data = domain_data[domain_data[segment_col] == segment_val]
                    self._calculate_movements(movement_data, seg_data, domain, segment_val)
            else:
                agg_data = domain_data.groupby('term').agg({
                    'tier_mix_t1_pct': 'mean',
                    'tier_mix_t2_pct': 'mean', 
                    'tier_mix_t3_pct': 'mean',
                    'dominant_index': 'mean'
                }).reset_index()
                self._calculate_movements(movement_data, agg_data, domain)
        
        if movement_data:
            movement_df = pd.DataFrame(movement_data)
            st.dataframe(movement_df, use_container_width=True)

    def _calculate_movements(self, movement_data: list, data: pd.DataFrame, domain: str, segment_val: str = None):
        """Calculate term-to-term movements for a domain/segment."""
        terms = sorted(data['term'].unique())
        
        for i in range(len(terms) - 1):
            current_term = data[data['term'] == terms[i]].iloc[0]
            next_term = data[data['term'] == terms[i + 1]].iloc[0]
            
            t3_change = next_term['tier_mix_t3_pct'] - current_term['tier_mix_t3_pct']
            index_change = next_term['dominant_index'] - current_term['dominant_index']
            
            movement_type = "📈 Improvement" if t3_change > 2 else "📉 Decline" if t3_change < -2 else "➡️ Stable"
            
            movement_data.append({
                'Domain': domain,
                'Segment': segment_val or 'Overall',
                'Period': f"{terms[i]} → {terms[i+1]}",
                'T3 Change': f"{t3_change:+.1f}%",
                'Index Change': f"{index_change:+.2f}",
                'Movement': movement_type
            })

    def _create_domain_performance_chart(self, df: pd.DataFrame, segment_col: str):
        """Create domain performance evolution chart."""
        fig = go.Figure()
        
        for domain in sorted(df['domain'].unique()):
            domain_data = df[df['domain'] == domain].groupby('term')['domain_avg'].mean().reset_index()
            
            fig.add_trace(go.Scatter(
                x=domain_data['term'],
                y=domain_data['domain_avg'],
                mode='lines+markers',
                name=domain,
                line=dict(color=self.domain_colors.get(domain, '#888888'))
            ))
        
        fig.update_layout(
            title="Domain Performance Evolution",
            xaxis_title="Term",
            yaxis_title="Average Domain Score",
            yaxis=dict(range=[0, 1])
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _create_tier_performance_chart(self, df: pd.DataFrame, segment_col: str):
        """Create tier performance scores chart."""
        fig = make_subplots(rows=1, cols=3, subplot_titles=["Tier 1", "Tier 2", "Tier 3"])
        
        tier_cols = ['avg_tier_score_t1', 'avg_tier_score_t2', 'avg_tier_score_t3']
        
        for i, tier_col in enumerate(tier_cols, 1):
            for domain in sorted(df['domain'].unique()):
                domain_data = df[df['domain'] == domain].groupby('term')[tier_col].mean().reset_index()
                
                fig.add_trace(
                    go.Scatter(
                        x=domain_data['term'],
                        y=domain_data[tier_col],
                        mode='lines+markers',
                        name=domain,
                        line=dict(color=self.domain_colors.get(domain, '#888888')),
                        showlegend=(i == 1)
                    ),
                    row=1, col=i
                )
        
        fig.update_layout(title="Tier Performance Scores by Domain")
        st.plotly_chart(fig, use_container_width=True)

    def _create_performance_heatmap(self, df: pd.DataFrame, segment_col: str):
        """Create performance heatmap."""
        # Aggregate data for heatmap
        heatmap_data = df.groupby(['domain', 'term'])['domain_avg'].mean().reset_index()
        heatmap_pivot = heatmap_data.pivot(index='domain', columns='term', values='domain_avg')
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_pivot.values,
            x=heatmap_pivot.columns,
            y=heatmap_pivot.index,
            colorscale='RdYlGn',
            colorbar=dict(title="Performance Score")
        ))
        
        fig.update_layout(
            title="Domain Performance Heatmap",
            xaxis_title="Term",
            yaxis_title="Domain"
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _create_recovery_analysis(self, df: pd.DataFrame, segment_col: str):
        """Analyze recovery patterns from Term 2 to Term 3."""
        recovery_data = []
        
        for domain in sorted(df['domain'].unique()):
            domain_data = df[df['domain'] == domain]
            
            t1_data = domain_data[domain_data['term'] == 'Term 1']
            t2_data = domain_data[domain_data['term'] == 'Term 2'] 
            t3_data = domain_data[domain_data['term'] == 'Term 3']
            
            if not (t1_data.empty or t2_data.empty or t3_data.empty):
                t1_avg = t1_data['domain_avg'].mean()
                t2_avg = t2_data['domain_avg'].mean()
                t3_avg = t3_data['domain_avg'].mean()
                
                decline = t2_avg - t1_avg
                recovery = t3_avg - t2_avg
                net_change = t3_avg - t1_avg
                
                recovery_strength = "🚀 Exceptional" if recovery > 0.10 else "💪 Strong" if recovery > 0.05 else "📈 Moderate" if recovery > 0 else "📉 Continued Decline"
                
                recovery_data.append({
                    'Domain': domain,
                    'T1 Score': f"{t1_avg:.2f}",
                    'T2 Score': f"{t2_avg:.2f}",
                    'T3 Score': f"{t3_avg:.2f}",
                    'T1→T2 Change': f"{decline:+.2f}",
                    'T2→T3 Recovery': f"{recovery:+.2f}",
                    'Net Change': f"{net_change:+.2f}",
                    'Recovery Pattern': recovery_strength
                })
        
        if recovery_data:
            recovery_df = pd.DataFrame(recovery_data)
            st.dataframe(recovery_df, use_container_width=True)

    def _create_strategic_positioning_chart(self, df: pd.DataFrame, segment_col: str):
        """Create strategic positioning scatter plot."""
        fig = go.Figure()
        
        for domain in sorted(df['domain'].unique()):
            domain_data = df[df['domain'] == domain]
            
            fig.add_trace(go.Scatter(
                x=domain_data['dominant_index'],
                y=domain_data['domain_avg'],
                mode='markers+text',
                name=domain,
                text=domain_data['term'],
                textposition="top center",
                marker=dict(
                    size=domain_data['tier_mix_t3_pct'] / 2,  # Size by T3 percentage
                    color=self.domain_colors.get(domain, '#888888')
                )
            ))
        
        fig.add_vline(x=2.0, line_dash="dash", line_color="gray", annotation_text="Balanced")
        fig.add_hline(y=0.6, line_dash="dash", line_color="gray", annotation_text="Target Performance")
        
        fig.update_layout(
            title="Strategic Positioning: Performance vs Distribution",
            xaxis_title="Dominant Index (Distribution Quality)",
            yaxis_title="Domain Performance",
            xaxis=dict(range=[1.5, 3.0]),
            yaxis=dict(range=[0.3, 0.8])
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _create_tier_strength_analysis(self, df: pd.DataFrame, segment_col: str):
        """Create tier strength indicator analysis."""
        strength_data = []
        
        for domain in sorted(df['domain'].unique()):
            domain_data = df[df['domain'] == domain]
            
            for _, row in domain_data.iterrows():
                # Calculate tier strength (weighted performance)
                tier_strength = (
                    row['avg_tier_score_t1'] * row['tier_mix_t1_pct'] / 100 * 1 +
                    row['avg_tier_score_t2'] * row['tier_mix_t2_pct'] / 100 * 2 +
                    row['avg_tier_score_t3'] * row['tier_mix_t3_pct'] / 100 * 3
                ) / 3  # Normalize
                
                strength_data.append({
                    'Domain': domain,
                    'Term': row['term'],
                    'Tier Strength': tier_strength,
                    'Segment': row.get(segment_col, 'Overall') if segment_col else 'Overall'
                })
        
        if strength_data:
            strength_df = pd.DataFrame(strength_data)
            
            fig = px.bar(
                strength_df,
                x='Term',
                y='Tier Strength', 
                color='Domain',
                facet_col='Segment' if segment_col else None,
                title="Tier Strength Evolution (Performance × Distribution Quality)"
            )
            
            st.plotly_chart(fig, use_container_width=True)

    def _create_pattern_analysis(self, df: pd.DataFrame, segment_col: str):
        """Identify and display patterns."""
        st.markdown("### 🔍 Identified Patterns")
        
        patterns = []
        
        for domain in sorted(df['domain'].unique()):
            domain_data = df[df['domain'] == domain].sort_values('term')
            
            if len(domain_data) >= 3:  # Need at least 3 terms
                t1_t3 = domain_data.iloc[0]['tier_mix_t3_pct']
                t2_t3 = domain_data.iloc[1]['tier_mix_t3_pct'] 
                t3_t3 = domain_data.iloc[2]['tier_mix_t3_pct']
                
                # Pattern recognition
                if t2_t3 < t1_t3 and t3_t3 > t2_t3:
                    pattern = "U-Shape Recovery"
                    emoji = "📈"
                elif t3_t3 > t2_t3 > t1_t3:
                    pattern = "Consistent Growth"
                    emoji = "🚀"
                elif t1_t3 > t2_t3 > t3_t3:
                    pattern = "Steady Decline"
                    emoji = "📉"
                elif abs(t1_t3 - t3_t3) < 5:  # Within 5%
                    pattern = "Stable Performance"
                    emoji = "➡️"
                else:
                    pattern = "Volatile"
                    emoji = "📊"
                
                patterns.append(f"{emoji} **{domain}**: {pattern} (T3%: {t1_t3:.0f}% → {t2_t3:.0f}% → {t3_t3:.0f}%)")
        
        for pattern in patterns:
            st.markdown(f"- {pattern}")

    def _create_strategic_recommendations(self, df: pd.DataFrame, segment_col: str):
        """Generate strategic recommendations based on data."""
        st.markdown("### 💡 Strategic Recommendations")
        
        # Find best and worst performing domains
        latest_term_data = df[df['term'] == df['term'].max()]
        
        if not latest_term_data.empty:
            best_domain = latest_term_data.loc[latest_term_data['tier_mix_t3_pct'].idxmax()]
            worst_domain = latest_term_data.loc[latest_term_data['tier_mix_t3_pct'].idxmin()]
            
            recommendations = [
                f"🏆 **Replicate Success**: {best_domain['domain']} shows strong Tier 3 performance ({best_domain['tier_mix_t3_pct']:.0f}%). Study and replicate successful practices.",
                f"🎯 **Focus Area**: {worst_domain['domain']} needs attention with only {worst_domain['tier_mix_t3_pct']:.0f}% in Tier 3. Consider targeted interventions.",
            ]
            
            # Recovery analysis
            recovery_domains = []
            for domain in df['domain'].unique():
                domain_data = df[df['domain'] == domain].sort_values('term')
                if len(domain_data) >= 2:
                    improvement = domain_data.iloc[-1]['tier_mix_t3_pct'] - domain_data.iloc[-2]['tier_mix_t3_pct']
                    if improvement > 10:
                        recovery_domains.append((domain, improvement))
            
            if recovery_domains:
                best_recovery = max(recovery_domains, key=lambda x: x[1])
                recommendations.append(f"💪 **Recovery Champion**: {best_recovery[0]} showed excellent recovery (+{best_recovery[1]:.1f}% in Tier 3). Document recovery strategies.")
            
            for rec in recommendations:
                st.markdown(f"- {rec}")

    def _create_segment_comparison_chart(self, df: pd.DataFrame, segment_col: str):
        """Create segment comparison chart."""
        fig = px.box(
            df,
            x=segment_col,
            y='domain_avg',
            color='domain',
            title=f"Performance Distribution by {segment_col.replace('_', ' ').title()}"
        )
        
        st.plotly_chart(fig, use_container_width=True)

    def _create_progression_rate_analysis(self, df: pd.DataFrame, segment_col: str):
        """Analyze progression rates across segments."""
        progression_data = []
        
        for segment_val in sorted(df[segment_col].unique()):
            segment_data = df[df[segment_col] == segment_val]
            
            for domain in sorted(segment_data['domain'].unique()):
                domain_data = segment_data[segment_data['domain'] == domain].sort_values('term')
                
                if len(domain_data) >= 2:
                    first_term = domain_data.iloc[0]
                    last_term = domain_data.iloc[-1]
                    
                    progression_rate = (last_term['tier_mix_t3_pct'] - first_term['tier_mix_t3_pct']) / len(domain_data)
                    
                    progression_data.append({
                        'Segment': segment_val,
                        'Domain': domain,
                        'Progression Rate': progression_rate,
                        'Starting T3%': first_term['tier_mix_t3_pct'],
                        'Ending T3%': last_term['tier_mix_t3_pct'],
                        'Total Change': last_term['tier_mix_t3_pct'] - first_term['tier_mix_t3_pct']
                    })
        
        if progression_data:
            progression_df = pd.DataFrame(progression_data)
            
            fig = px.scatter(
                progression_df,
                x='Starting T3%',
                y='Ending T3%',
                size='Total Change',
                color='Segment',
                hover_data=['Domain', 'Progression Rate'],
                title="Progression Trajectories by Segment"
            )
            
            # Add diagonal line for no change
            fig.add_shape(
                type="line",
                x0=0, y0=0, x1=100, y1=100,
                line=dict(color="gray", dash="dash")
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Show progression table
            st.dataframe(
                progression_df.style.format({
                    'Progression Rate': '{:.2f}%/term',
                    'Starting T3%': '{:.1f}%',
                    'Ending T3%': '{:.1f}%',
                    'Total Change': '{:+.1f}%'
                }),
                use_container_width=True
            )

    def _create_trend_analysis(self, df: pd.DataFrame, segment_col: str):
        """Create trend analysis with statistical insights."""
        st.markdown("### 📈 Statistical Trend Analysis")
        
        trend_data = []
        
        for segment_val in sorted(df[segment_col].unique()):
            segment_data = df[df[segment_col] == segment_val]
            
            for domain in sorted(segment_data['domain'].unique()):
                domain_data = segment_data[segment_data['domain'] == domain].sort_values('term')
                
                if len(domain_data) >= 3:  # Need at least 3 points for trend
                    # Simple linear trend calculation
                    x_vals = range(len(domain_data))
                    y_vals = domain_data['tier_mix_t3_pct'].values
                    
                    # Calculate slope (trend)
                    if len(x_vals) > 1:
                        slope = np.polyfit(x_vals, y_vals, 1)[0]
                        
                        # Trend classification
                        if slope > 5:
                            trend = "📈 Strong Upward"
                        elif slope > 2:
                            trend = "📈 Moderate Upward" 
                        elif slope > -2:
                            trend = "➡️ Stable"
                        elif slope > -5:
                            trend = "📉 Moderate Downward"
                        else:
                            trend = "📉 Strong Downward"
                        
                        # Calculate volatility (standard deviation)
                        volatility = np.std(y_vals)
                        
                        trend_data.append({
                            'Segment': segment_val,
                            'Domain': domain,
                            'Trend': trend,
                            'Slope': slope,
                            'Volatility': volatility,
                            'Latest T3%': y_vals[-1],
                            'Change Range': f"{y_vals.min():.0f}% - {y_vals.max():.0f}%"
                        })
        
        if trend_data:
            trend_df = pd.DataFrame(trend_data)
            
            # Create trend visualization
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.scatter(
                    trend_df,
                    x='Slope',
                    y='Latest T3%',
                    size='Volatility',
                    color='Segment',
                    hover_data=['Domain', 'Trend'],
                    title="Trend Analysis: Slope vs Current Performance"
                )
                
                fig.add_vline(x=0, line_dash="dash", line_color="gray")
                fig.add_hline(y=50, line_dash="dash", line_color="gray") 
                
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Trend summary
                trend_summary = trend_df.groupby('Trend').size().reset_index(name='Count')
                
                fig = px.pie(
                    trend_summary,
                    values='Count',
                    names='Trend',
                    title="Distribution of Trend Patterns"
                )
                
                st.plotly_chart(fig, use_container_width=True)
            
            # Show detailed trend table
            st.subheader("📊 Detailed Trend Analysis")
            st.dataframe(
                trend_df.style.format({
                    'Slope': '{:+.2f}%/term',
                    'Volatility': '{:.1f}%',
                    'Latest T3%': '{:.1f}%'
                }),
                use_container_width=True
            )
            
            # Key insights
            self._generate_trend_insights(trend_df)

    def _generate_trend_insights(self, trend_df: pd.DataFrame):
        """Generate key insights from trend analysis."""
        st.subheader("🔍 Key Trend Insights")
        
        insights = []
        
        # Find strongest trends
        strongest_upward = trend_df.loc[trend_df['Slope'].idxmax()] if not trend_df.empty else None
        strongest_downward = trend_df.loc[trend_df['Slope'].idxmin()] if not trend_df.empty else None
        
        if strongest_upward is not None:
            insights.append(f"🚀 **Strongest Growth**: {strongest_upward['Domain']} ({strongest_upward['Segment']}) with {strongest_upward['Slope']:+.1f}% improvement per term")
        
        if strongest_downward is not None and strongest_downward['Slope'] < -2:
            insights.append(f"⚠️ **Needs Attention**: {strongest_downward['Domain']} ({strongest_downward['Segment']}) declining by {strongest_downward['Slope']:+.1f}% per term")
        
        # Find most volatile
        most_volatile = trend_df.loc[trend_df['Volatility'].idxmax()] if not trend_df.empty else None
        if most_volatile is not None:
            insights.append(f"📊 **Most Volatile**: {most_volatile['Domain']} ({most_volatile['Segment']}) with {most_volatile['Volatility']:.1f}% volatility - needs stability focus")
        
        # Segment comparison
        if 'Segment' in trend_df.columns and len(trend_df['Segment'].unique()) > 1:
            segment_trends = trend_df.groupby('Segment')['Slope'].mean()
            best_segment = segment_trends.idxmax()
            insights.append(f"🏆 **Best Performing Segment**: {best_segment} with average trend of {segment_trends[best_segment]:+.1f}% per term")
        
        # Display insights
        for insight in insights:
            st.markdown(f"- {insight}")
        
        # Recommendations based on trends
        st.subheader("💡 Trend-Based Recommendations")
        
        upward_trends = len(trend_df[trend_df['Slope'] > 2])
        stable_trends = len(trend_df[(trend_df['Slope'] >= -2) & (trend_df['Slope'] <= 2)])
        downward_trends = len(trend_df[trend_df['Slope'] < -2])
        
        total_trends = len(trend_df)
        
        if upward_trends / total_trends > 0.6:
            st.success("✅ **System Health**: Strong positive trends across most domains. Continue current strategies.")
        elif downward_trends / total_trends > 0.4:
            st.error("⚠️ **System Alert**: Multiple domains showing negative trends. Immediate strategic review needed.")
        else:
            st.info("📊 **Mixed Signals**: Performance varies significantly across domains. Focus on targeted interventions.")

# Usage example and additional helper functions
def create_sample_usage():
    """Example of how to use the enhanced tier progression page."""
    
    # Sample data structure that would come from your materialized view
    sample_data = {
        'term': ['Term 1', 'Term 2', 'Term 3'] * 10,
        'domain': ['AII', 'IA', 'KPC', 'LE', 'SE'] * 6,
        'fellow_year': ['Year 1'] * 15 + ['Year 2'] * 15,
        'school_level': ['Primary School'] * 20 + ['High School'] * 10,
        'tier_mix_t1_pct': np.random.uniform(20, 50, 30),
        'tier_mix_t2_pct': np.random.uniform(10, 30, 30), 
        'tier_mix_t3_pct': np.random.uniform(30, 70, 30),
        'domain_avg': np.random.uniform(0.4, 0.8, 30),
        'dominant_index': np.random.uniform(1.8, 2.8, 30),
        'avg_tier_score_t1': np.random.uniform(0.5, 0.8, 30),
        'avg_tier_score_t2': np.random.uniform(0.5, 0.8, 30),
        'avg_tier_score_t3': np.random.uniform(0.5, 0.8, 30),
        'strongest_tier': np.random.choice(['Tier 1', 'Tier 2', 'Tier 3'], 30),
        'weakest_tier': np.random.choice(['Tier 1', 'Tier 2', 'Tier 3'], 30),
        'strongest_index': np.random.uniform(2.0, 3.0, 30),
        'weakest_index': np.random.uniform(1.0, 2.0, 30)
    }
    
    return pd.DataFrame(sample_data)

# Integration function for your Streamlit app
def integrate_enhanced_tier_page(df: pd.DataFrame):
    """
    Integration function to use the enhanced tier progression page in your app.
    
    Args:
        df: DataFrame from your materialized view mv_comprehensive_tier_analysis
    """
    
    # Initialize the enhanced page
    tier_page = EnhancedTierProgressionPage()
    
    # Render the page
    tier_page.render(df)
    
    return tier_page