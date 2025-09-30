import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from utils.supabase.database_manager import get_db

st.set_page_config(page_title="Enhanced Tier Progression", page_icon="📈", layout="wide")

# Constants
TERM_ORDER = ["Term 1", "Term 2", "Term 3", "Term 4"]
DOMAIN_COLORS = {
    "LE": "#59A14F", "SE": "#4E79A7", "KPC": "#9C755F",
    "AII": "#E15759", "IAL": "#F28E2B", "IAN": "#76B7B2",
}
TIER_COLORS = {"Tier 1": "#E15759", "Tier 2": "#F1CE63", "Tier 3": "#59A14F"}

# Load and process data
@st.cache_data(ttl=3600)
def load_and_process_data():
    """Load observations and compute tier metrics"""
    db = get_db()
    df_raw = db.get_observations_full()
    
    if df_raw is None or df_raw.empty:
        return pd.DataFrame(), pd.DataFrame()
    
    # Keep domain-level rows
    df = df_raw[['observation_id', 'term', 'domain', 'score', 'classification', 
                 'fellowship_year', 'school_name', 'fellow_name']].copy()
    
    # Clean data
    df = df.dropna(subset=['domain', 'classification'])
    df['term'] = pd.Categorical(df['term'], categories=TERM_ORDER, ordered=True)
    df['fellowship_year'] = df['fellowship_year'].apply(lambda x: f"Year {int(x)}" if pd.notna(x) else None)
    
    # Derive school level from school name
    df['school_level'] = df['school_name'].apply(
        lambda x: 'High School' if any(term in str(x).lower() for term in ['high', 'secondary']) else 'Primary School'
    )
    
    # Compute aggregated metrics
    agg_list = []
    
    groups = [
        ('Overall', ['term', 'domain']),
        ('School Level', ['term', 'domain', 'school_level']),
        ('Fellowship Year', ['term', 'domain', 'fellowship_year']),
    ]
    
    for group_name, group_cols in groups:
        grouped = df.groupby(group_cols)
        
        for name, group in grouped:
            if len(group) < 3:
                continue
                
            # Parse group keys
            if group_name == 'Overall':
                term, domain = name
                segment_type, segment_value = None, None
            elif group_name == 'School Level':
                term, domain, segment_value = name
                segment_type = 'school_level'
            else:  # Fellowship Year
                term, domain, segment_value = name
                segment_type = 'fellowship_year'
            
            # Tier distribution
            tier_counts = group['classification'].value_counts()
            total = len(group)
            t1_pct = (tier_counts.get('Tier 1', 0) / total) * 100
            t2_pct = (tier_counts.get('Tier 2', 0) / total) * 100
            t3_pct = (tier_counts.get('Tier 3', 0) / total) * 100
            
            # Tier scores
            t1_score = group[group['classification'] == 'Tier 1']['score'].mean()
            t2_score = group[group['classification'] == 'Tier 2']['score'].mean()
            t3_score = group[group['classification'] == 'Tier 3']['score'].mean()
            
            # Domain average
            domain_avg = group['score'].mean()
            
            # Dominant index (weighted tier position: 1*T1% + 2*T2% + 3*T3%)
            dominant_index = (1 * t1_pct + 2 * t2_pct + 3 * t3_pct) / 100
            
            agg_list.append({
                'term': term,
                'domain': domain,
                'segment_type': segment_type,
                'segment_value': segment_value,
                'tier_mix_t1_pct': t1_pct,
                'tier_mix_t2_pct': t2_pct,
                'tier_mix_t3_pct': t3_pct,
                'avg_tier_score_t1': t1_score,
                'avg_tier_score_t2': t2_score,
                'avg_tier_score_t3': t3_score,
                'domain_avg': domain_avg,
                'dominant_index': dominant_index,
                'observation_count': total,
            })
    
    df_agg = pd.DataFrame(agg_list)
    return df, df_agg

# Load data
df_raw, df_agg = load_and_process_data()

if df_agg.empty:
    st.error("No observation data available. Please check your database connection.")
    st.stop()

# Header
st.title("📈 Enhanced Tier Progression Analysis")
st.caption("Derived from classroom observation data")

# Filters
with st.container():
    st.markdown("### 🎛️ Filters")
    c1, c2, c3, c4, c5 = st.columns([1.3, 1.3, 1.3, 1.1, 0.8])
    
    segment_choice = c1.selectbox(
        "Segment By",
        ["Overall", "School Level", "Fellowship Year"],
        key="tier_segment"
    )
    
    segment_map = {
        "Overall": None,
        "School Level": "school_level",
        "Fellowship Year": "fellowship_year"
    }
    segment_col = segment_map[segment_choice]
    
    domains = sorted(df_agg['domain'].unique())
    sel_domains = c2.multiselect("Domains", domains, default=domains, key="tier_domains")
    
    terms = [t for t in TERM_ORDER if t in df_agg['term'].unique()]
    sel_terms = c3.multiselect("Terms", terms, default=terms, key="tier_terms")
    
    analysis_type = c4.selectbox(
        "Analysis Type",
        ["Tier Mix Evolution", "Performance Trends", "Strategic Analysis"],
        key="tier_analysis"
    )
    
    if c5.button("♻️ Reset", use_container_width=True):
        for k in list(st.session_state.keys()):
            if k.startswith("tier_"):
                del st.session_state[k]
        st.rerun()

# Apply filters
work = df_agg.copy()
if segment_col:
    work = work[work['segment_type'] == segment_col]
else:
    work = work[work['segment_type'].isna()]

work = work[work['domain'].isin(sel_domains) & work['term'].isin(sel_terms)]

if work.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

st.divider()

# === TIER MIX EVOLUTION ===
if analysis_type == "Tier Mix Evolution":
    st.header("🎯 Tier Mix Evolution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Tier 3 Progression by Domain")
        fig = go.Figure()
        
        if segment_col:
            for seg in sorted(work['segment_value'].dropna().unique()):
                seg_df = work[work['segment_value'] == seg]
                for dom in sorted(seg_df['domain'].unique()):
                    dom_df = seg_df[seg_df['domain'] == dom].sort_values('term')
                    fig.add_trace(go.Scatter(
                        x=dom_df['term'], y=dom_df['tier_mix_t3_pct'],
                        mode='lines+markers', name=f"{dom} ({seg})",
                        line=dict(color=DOMAIN_COLORS.get(dom, '#888888'))
                    ))
        else:
            for dom in sorted(work['domain'].unique()):
                dom_df = work[work['domain'] == dom].sort_values('term')
                fig.add_trace(go.Scatter(
                    x=dom_df['term'], y=dom_df['tier_mix_t3_pct'],
                    mode='lines+markers', name=dom,
                    line=dict(color=DOMAIN_COLORS.get(dom, '#888888'))
                ))
        
        fig.update_layout(height=400, yaxis_title="Tier 3 (%)", yaxis=dict(range=[0, 100]))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Dominant Index Progression")
        fig = go.Figure()
        
        if segment_col:
            for seg in sorted(work['segment_value'].dropna().unique()):
                seg_df = work[work['segment_value'] == seg]
                for dom in sorted(seg_df['domain'].unique()):
                    dom_df = seg_df[seg_df['domain'] == dom].sort_values('term')
                    fig.add_trace(go.Scatter(
                        x=dom_df['term'], y=dom_df['dominant_index'],
                        mode='lines+markers', name=f"{dom} ({seg})",
                        line=dict(color=DOMAIN_COLORS.get(dom, '#888888'))
                    ))
        else:
            for dom in sorted(work['domain'].unique()):
                dom_df = work[work['domain'] == dom].sort_values('term')
                fig.add_trace(go.Scatter(
                    x=dom_df['term'], y=dom_df['dominant_index'],
                    mode='lines+markers', name=dom,
                    line=dict(color=DOMAIN_COLORS.get(dom, '#888888'))
                ))
        
        fig.add_hline(y=2.0, line_dash="dash", line_color="gray", annotation_text="Balanced")
        fig.add_hline(y=2.5, line_dash="dash", line_color="green", annotation_text="Strong")
        fig.update_layout(height=400, yaxis_title="Dominant Index", yaxis=dict(range=[1, 3]))
        st.plotly_chart(fig, use_container_width=True)
    
    # Summary table
    st.subheader("Tier Mix Summary")
    summary = work.groupby(['domain', 'term']).agg({
        'tier_mix_t1_pct': 'mean',
        'tier_mix_t2_pct': 'mean',
        'tier_mix_t3_pct': 'mean',
        'dominant_index': 'mean',
        'observation_count': 'sum'
    }).reset_index()
    
    st.dataframe(
        summary.style.format({
            'tier_mix_t1_pct': '{:.1f}%',
            'tier_mix_t2_pct': '{:.1f}%',
            'tier_mix_t3_pct': '{:.1f}%',
            'dominant_index': '{:.2f}',
            'observation_count': '{:.0f}'
        }),
        use_container_width=True
    )

# === PERFORMANCE TRENDS ===
elif analysis_type == "Performance Trends":
    st.header("📊 Performance Trends")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Domain Performance Evolution")
        fig = go.Figure()
        for dom in sorted(work['domain'].unique()):
            dom_df = work[work['domain'] == dom].sort_values('term')
            fig.add_trace(go.Scatter(
                x=dom_df['term'], y=dom_df['domain_avg'],
                mode='lines+markers', name=dom,
                line=dict(color=DOMAIN_COLORS.get(dom, '#888888'))
            ))
        fig.update_layout(height=400, yaxis_title="Average Score", yaxis=dict(range=[1, 4]))
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Performance Heatmap")
        heat = work.pivot_table(
            index='domain', columns='term', values='domain_avg', aggfunc='mean'
        )
        fig = go.Figure(
            data=go.Heatmap(
                z=heat.values, x=heat.columns, y=heat.index,
                colorscale="RdYlGn", colorbar=dict(title="Avg Score")
            )
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    st.subheader("Tier Performance Scores")
    fig = make_subplots(rows=1, cols=3, subplot_titles=["Tier 1", "Tier 2", "Tier 3"])
    
    for i, col_name in enumerate(['avg_tier_score_t1', 'avg_tier_score_t2', 'avg_tier_score_t3'], 1):
        for dom in sorted(work['domain'].unique()):
            dom_df = work[work['domain'] == dom].sort_values('term')
            fig.add_trace(
                go.Scatter(
                    x=dom_df['term'], y=dom_df[col_name],
                    mode='lines+markers', name=dom,
                    line=dict(color=DOMAIN_COLORS.get(dom, '#888888')),
                    showlegend=(i == 1)
                ),
                row=1, col=i
            )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)

# === STRATEGIC ANALYSIS ===
elif analysis_type == "Strategic Analysis":
    st.header("🎯 Strategic Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Strategic Positioning")
        fig = go.Figure()
        for dom in sorted(work['domain'].unique()):
            d = work[work['domain'] == dom]
            fig.add_trace(go.Scatter(
                x=d['dominant_index'], y=d['domain_avg'],
                mode='markers+text', text=d['term'], textposition='top center',
                name=dom,
                marker=dict(
                    size=d['tier_mix_t3_pct'] / 3,
                    color=DOMAIN_COLORS.get(dom, '#888888')
                )
            ))
        
        fig.add_vline(x=2.0, line_dash="dash", line_color="gray")
        fig.add_hline(y=3.0, line_dash="dash", line_color="gray")
        fig.update_layout(
            height=450,
            xaxis_title="Dominant Index",
            yaxis_title="Domain Performance",
            xaxis=dict(range=[1.5, 3]), yaxis=dict(range=[1, 4])
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("Key Insights")
        latest = work[work['term'] == work['term'].max()]
        
        if not latest.empty:
            best = latest.loc[latest['tier_mix_t3_pct'].idxmax()]
            worst = latest.loc[latest['tier_mix_t3_pct'].idxmin()]
            
            st.success(f"**Strongest Domain**: {best['domain']} with {best['tier_mix_t3_pct']:.1f}% Tier 3")
            st.warning(f"**Focus Area**: {worst['domain']} with {worst['tier_mix_t3_pct']:.1f}% Tier 3")
            
            st.info(f"**Average Performance**: {latest['domain_avg'].mean():.2f} across all domains")
            st.metric("Total Observations", f"{latest['observation_count'].sum():.0f}")

st.divider()
st.caption("📊 Enhanced Tier Progression • Derived from Classroom Observations • Streamlit")