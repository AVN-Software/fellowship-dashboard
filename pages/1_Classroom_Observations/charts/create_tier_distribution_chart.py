import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import streamlit as st

def create_tier_distribution_chart(df: pd.DataFrame, segment_col: str, domain_colors: dict):
    """Enhanced tier distribution with multiple visualization options for comparing segments."""
    
    st.write("### 📊 Tier Distribution Analysis")
    
    # Visualization controls
    col1, col2 = st.columns(2)
    with col1:
        viz_type = st.selectbox(
            "Visualization Type:",
            ["Multi-Panel Comparison", "Stacked Area", "Side-by-Side Bars", "Heatmap Matrix"],
            key="tier_viz_type"
        )
    
    with col2:
        focus_tier = st.selectbox(
            "Focus on Tier:",
            ["All Tiers", "Tier 3 Only", "Tier 1 vs Tier 3"],
            key="tier_focus"
        )
    
    # Data aggregation
    if segment_col and segment_col != "both":
        # Group by term and segment
        agg_df = (
            df.groupby(['term', segment_col, 'domain'])[
                ['tier_mix_t1_pct', 'tier_mix_t2_pct', 'tier_mix_t3_pct']
            ].mean().reset_index()
        )
        
        # Overall segment averages
        segment_avg = (
            df.groupby(['term', segment_col])[
                ['tier_mix_t1_pct', 'tier_mix_t2_pct', 'tier_mix_t3_pct']
            ].mean().reset_index()
        )
    else:
        # Overall averages only
        agg_df = (
            df.groupby(['term', 'domain'])[
                ['tier_mix_t1_pct', 'tier_mix_t2_pct', 'tier_mix_t3_pct']
            ].mean().reset_index()
        )
        segment_avg = (
            df.groupby('term')[
                ['tier_mix_t1_pct', 'tier_mix_t2_pct', 'tier_mix_t3_pct']
            ].mean().reset_index()
        )
    
    # Render based on selected visualization
    if viz_type == "Multi-Panel Comparison":
        render_multi_panel_comparison(segment_avg, agg_df, segment_col, focus_tier, domain_colors)
    
    elif viz_type == "Stacked Area":
        render_stacked_area(segment_avg, segment_col, focus_tier)
    
    elif viz_type == "Side-by-Side Bars":
        render_side_by_side_bars(segment_avg, agg_df, segment_col, focus_tier, domain_colors)
    
    elif viz_type == "Heatmap Matrix":
        render_heatmap_matrix(agg_df, segment_col, focus_tier)

def render_multi_panel_comparison(segment_avg, agg_df, segment_col, focus_tier, domain_colors):
    """Multi-panel view comparing segments and showing domain breakdown."""
    
    if segment_col and segment_col != "both":
        # Create panels for each segment
        segments = sorted(segment_avg[segment_col].unique())
        fig = make_subplots(
            rows=len(segments), cols=2,
            subplot_titles=[f"{seg} - Overall" for seg in segments] + 
                          [f"{seg} - By Domain" for seg in segments],
            specs=[[{"secondary_y": False}, {"secondary_y": False}] for _ in segments],
            vertical_spacing=0.08,
            horizontal_spacing=0.1
        )
        
        tier_colors = {'Tier 1': '#FF6B6B', 'Tier 2': '#4ECDC4', 'Tier 3': '#45B7D1'}
        
        for i, segment_val in enumerate(segments, 1):
            segment_data = segment_avg[segment_avg[segment_col] == segment_val]
            domain_data = agg_df[agg_df[segment_col] == segment_val]
            
            # Left panel: Overall segment trends
            if focus_tier == "All Tiers":
                for tier, col, color in [('Tier 1', 'tier_mix_t1_pct', tier_colors['Tier 1']),
                                       ('Tier 2', 'tier_mix_t2_pct', tier_colors['Tier 2']),
                                       ('Tier 3', 'tier_mix_t3_pct', tier_colors['Tier 3'])]:
                    fig.add_trace(
                        go.Scatter(x=segment_data['term'], y=segment_data[col],
                                 mode='lines+markers', name=f"{tier} ({segment_val})",
                                 line=dict(color=color), showlegend=(i==1)),
                        row=i, col=1
                    )
            elif focus_tier == "Tier 3 Only":
                fig.add_trace(
                    go.Scatter(x=segment_data['term'], y=segment_data['tier_mix_t3_pct'],
                             mode='lines+markers', name=f"Tier 3 ({segment_val})",
                             line=dict(color=tier_colors['Tier 3']), showlegend=(i==1)),
                    row=i, col=1
                )
            else:  # Tier 1 vs Tier 3
                fig.add_trace(
                    go.Scatter(x=segment_data['term'], y=segment_data['tier_mix_t1_pct'],
                             mode='lines+markers', name=f"Tier 1 ({segment_val})",
                             line=dict(color=tier_colors['Tier 1']), showlegend=(i==1)),
                    row=i, col=1
                )
                fig.add_trace(
                    go.Scatter(x=segment_data['term'], y=segment_data['tier_mix_t3_pct'],
                             mode='lines+markers', name=f"Tier 3 ({segment_val})",
                             line=dict(color=tier_colors['Tier 3']), showlegend=(i==1)),
                    row=i, col=1
                )
            
            # Right panel: Domain breakdown
            for domain in sorted(domain_data['domain'].unique()):
                domain_subset = domain_data[domain_data['domain'] == domain]
                
                if focus_tier == "Tier 3 Only":
                    y_col = 'tier_mix_t3_pct'
                elif focus_tier == "Tier 1 vs Tier 3":
                    y_col = 'tier_mix_t3_pct'  # Show tier 3 for domain comparison
                else:
                    y_col = 'tier_mix_t3_pct'  # Default to tier 3 for clarity
                
                fig.add_trace(
                    go.Scatter(x=domain_subset['term'], y=domain_subset[y_col],
                             mode='lines+markers', name=f"{domain} ({segment_val})",
                             line=dict(color=domain_colors.get(domain, '#888888')),
                             showlegend=(i==1)),
                    row=i, col=2
                )
        
        fig.update_layout(
            title=f"Tier Distribution Comparison by {segment_col.replace('_', ' ').title()}",
            height=300 * len(segments),
            showlegend=True
        )
        
    else:
        # Single overall view
        fig = go.Figure()
        tier_colors = {'Tier 1': '#FF6B6B', 'Tier 2': '#4ECDC4', 'Tier 3': '#45B7D1'}
        
        if focus_tier == "All Tiers":
            for tier, col, color in [('Tier 1', 'tier_mix_t1_pct', tier_colors['Tier 1']),
                                   ('Tier 2', 'tier_mix_t2_pct', tier_colors['Tier 2']),
                                   ('Tier 3', 'tier_mix_t3_pct', tier_colors['Tier 3'])]:
                fig.add_trace(
                    go.Scatter(x=segment_avg['term'], y=segment_avg[col],
                             mode='lines+markers', name=tier, line=dict(color=color))
                )
        elif focus_tier == "Tier 3 Only":
            fig.add_trace(
                go.Scatter(x=segment_avg['term'], y=segment_avg['tier_mix_t3_pct'],
                         mode='lines+markers', name="Tier 3",
                         line=dict(color=tier_colors['Tier 3']))
            )
        
        fig.update_layout(title="Overall Tier Distribution Trends")
    
    st.plotly_chart(fig, use_container_width=True)

def render_stacked_area(segment_avg, segment_col, focus_tier):
    """Stacked area chart showing tier composition over time."""
    
    if segment_col and segment_col != "both":
        fig = make_subplots(
            rows=1, cols=len(segment_avg[segment_col].unique()),
            subplot_titles=[f"{seg}" for seg in sorted(segment_avg[segment_col].unique())],
            shared_yaxes=True
        )
        
        for i, segment_val in enumerate(sorted(segment_avg[segment_col].unique()), 1):
            segment_data = segment_avg[segment_avg[segment_col] == segment_val]
            
            if focus_tier == "All Tiers":
                # Stacked area for all tiers
                fig.add_trace(
                    go.Scatter(x=segment_data['term'], y=segment_data['tier_mix_t1_pct'],
                             mode='lines', fill='tonexty' if i>1 else 'tozeroy',
                             name=f"Tier 1", line=dict(color='#FF6B6B'), showlegend=(i==1)),
                    row=1, col=i
                )
                fig.add_trace(
                    go.Scatter(x=segment_data['term'], 
                             y=segment_data['tier_mix_t1_pct'] + segment_data['tier_mix_t2_pct'],
                             mode='lines', fill='tonexty',
                             name=f"Tier 2", line=dict(color='#4ECDC4'), showlegend=(i==1)),
                    row=1, col=i
                )
                fig.add_trace(
                    go.Scatter(x=segment_data['term'], 
                             y=segment_data['tier_mix_t1_pct'] + segment_data['tier_mix_t2_pct'] + segment_data['tier_mix_t3_pct'],
                             mode='lines', fill='tonexty',
                             name=f"Tier 3", line=dict(color='#45B7D1'), showlegend=(i==1)),
                    row=1, col=i
                )
            else:
                # Just show Tier 3 progression
                fig.add_trace(
                    go.Scatter(x=segment_data['term'], y=segment_data['tier_mix_t3_pct'],
                             mode='lines+markers', fill='tozeroy',
                             name=f"Tier 3", line=dict(color='#45B7D1'), showlegend=(i==1)),
                    row=1, col=i
                )
        
        fig.update_layout(title=f"Tier Composition Over Time by {segment_col.replace('_', ' ').title()}")
    
    else:
        # Single stacked area
        fig = go.Figure()
        
        if focus_tier == "All Tiers":
            fig.add_trace(go.Scatter(
                x=segment_avg['term'], y=segment_avg['tier_mix_t1_pct'],
                mode='lines', fill='tozeroy', name='Tier 1',
                line=dict(color='#FF6B6B')
            ))
            fig.add_trace(go.Scatter(
                x=segment_avg['term'], 
                y=segment_avg['tier_mix_t1_pct'] + segment_avg['tier_mix_t2_pct'],
                mode='lines', fill='tonexty', name='Tier 2',
                line=dict(color='#4ECDC4')
            ))
            fig.add_trace(go.Scatter(
                x=segment_avg['term'], 
                y=segment_avg['tier_mix_t1_pct'] + segment_avg['tier_mix_t2_pct'] + segment_avg['tier_mix_t3_pct'],
                mode='lines', fill='tonexty', name='Tier 3',
                line=dict(color='#45B7D1')
            ))
        
        fig.update_layout(title="Overall Tier Composition")
    
    st.plotly_chart(fig, use_container_width=True)

def render_side_by_side_bars(segment_avg, agg_df, segment_col, focus_tier, domain_colors):
    """Side-by-side bar comparison of segments."""
    
    if segment_col and segment_col != "both":
        # Melt data for easier plotting
        if focus_tier == "All Tiers":
            melt_df = segment_avg.melt(
                id_vars=['term', segment_col],
                value_vars=['tier_mix_t1_pct', 'tier_mix_t2_pct', 'tier_mix_t3_pct'],
                var_name='Tier', value_name='Percentage'
            )
            melt_df['Tier'] = melt_df['Tier'].str.replace('tier_mix_', '').str.replace('_pct', '').str.title()
            
            fig = px.bar(
                melt_df, x='term', y='Percentage', color='Tier',
                facet_col=segment_col, barmode='group',
                title=f"Tier Distribution by {segment_col.replace('_', ' ').title()}",
                category_orders={"Tier": ["Tier 1", "Tier 2", "Tier 3"]}
            )
        
        else:  # Focus on Tier 3 or Tier 1 vs 3
            y_col = 'tier_mix_t3_pct' if focus_tier == "Tier 3 Only" else ['tier_mix_t1_pct', 'tier_mix_t3_pct']
            
            if focus_tier == "Tier 3 Only":
                fig = px.bar(
                    segment_avg, x='term', y='tier_mix_t3_pct',
                    color=segment_col, barmode='group',
                    title=f"Tier 3 Distribution by {segment_col.replace('_', ' ').title()}"
                )
            else:  # Tier 1 vs 3
                melt_df = segment_avg.melt(
                    id_vars=['term', segment_col],
                    value_vars=['tier_mix_t1_pct', 'tier_mix_t3_pct'],
                    var_name='Tier', value_name='Percentage'
                )
                melt_df['Tier'] = melt_df['Tier'].str.replace('tier_mix_', '').str.replace('_pct', '').str.title()
                
                fig = px.bar(
                    melt_df, x='term', y='Percentage', color='Tier',
                    facet_col=segment_col, barmode='group',
                    title=f"Tier 1 vs Tier 3 by {segment_col.replace('_', ' ').title()}"
                )
        
        st.plotly_chart(fig, use_container_width=True)

def render_heatmap_matrix(agg_df, segment_col, focus_tier):
    """Heatmap showing tier performance across domains and segments."""
    
    if segment_col and segment_col != "both":
        # Create pivot for heatmap
        y_col = 'tier_mix_t3_pct' if focus_tier != "Tier 1 vs Tier 3" else 'tier_mix_t3_pct'
        
        # Latest term data for heatmap
        latest_term = agg_df['term'].max()
        heatmap_data = agg_df[agg_df['term'] == latest_term]
        
        pivot_df = heatmap_data.pivot_table(
            index='domain', columns=segment_col, values=y_col, fill_value=0
        )
        
        fig = go.Figure(data=go.Heatmap(
            z=pivot_df.values,
            x=pivot_df.columns,
            y=pivot_df.index,
            colorscale='RdYlGn',
            colorbar=dict(title="Tier 3 %")
        ))
        
        fig.update_layout(
            title=f"Tier 3 Performance Heatmap ({latest_term}) by Domain vs {segment_col.replace('_', ' ').title()}",
            xaxis_title=segment_col.replace('_', ' ').title(),
            yaxis_title="Domain"
        )
        
        st.plotly_chart(fig, use_container_width=True)

# Usage example
def example_usage():
    """Show how to use the improved visualization."""
    
    # Sample data structure
    sample_data = pd.DataFrame({
        'term': ['Term 1', 'Term 2', 'Term 3'] * 20,
        'domain': ['AII', 'KPC', 'LE', 'SE', 'IA'] * 12,
        'school_level': ['Primary School'] * 30 + ['High School'] * 30,
        'fellow_year': ['Year 1'] * 30 + ['Year 2'] * 30,
        'tier_mix_t1_pct': [25, 30, 20] * 20,
        'tier_mix_t2_pct': [35, 25, 30] * 20,
        'tier_mix_t3_pct': [40, 45, 50] * 20,
    })
    
    domain_colors = {
        'AII': '#FF9999', 'KPC': '#99FF99', 'LE': '#9999FF',
        'SE': '#FFFF99', 'IA': '#FF99FF'
    }
    
    # Call the function
    create_improved_tier_distribution_chart(sample_data, 'school_level', domain_colors)