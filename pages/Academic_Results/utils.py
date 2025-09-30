"""
Academic Results - Utility Functions
Shared data processing and calculations
"""

import pandas as pd
import numpy as np

PASS_THRESHOLD = 50.0

COLORS = {
    "primary": "#2E86AB",
    "secondary": "#A23B72",
    "success": "#06A77D",
    "warning": "#F18F01",
    "danger": "#C73E1D",
    "term1": "#4A90E2",
    "term2": "#50C878",
    "gradient": ["#C73E1D", "#F18F01", "#FDB462", "#06A77D", "#2E86AB"],
}

def prepare_data(df):
    """Clean and prepare academic results data."""
    df = df.copy()
    
    # Convert to numeric
    df['term_1_avg'] = pd.to_numeric(df['term_1_avg'], errors='coerce')
    df['term_2_avg'] = pd.to_numeric(df['term_2_avg'], errors='coerce')
    df['class_size'] = pd.to_numeric(df['class_size'], errors='coerce').fillna(0).astype(int)
    
    # Calculate percentages and improvement
    df['term_1_pct'] = df['term_1_avg'] * 100
    df['term_2_pct'] = df['term_2_avg'] * 100
    df['improvement'] = df['term_2_avg'] - df['term_1_avg']
    df['improvement_pct'] = df['improvement'] * 100
    
    # Pass/fail flags
    df['pass_term_1'] = df['term_1_pct'] >= PASS_THRESHOLD
    df['pass_term_2'] = df['term_2_pct'] >= PASS_THRESHOLD
    
    # Year display
    if 'fellowship_year_display' in df.columns:
        df['year_display'] = df['fellowship_year_display']
    elif 'fellowship_year' in df.columns:
        df['year_display'] = df['fellowship_year'].apply(
            lambda x: f"Year {x}" if pd.notna(x) else "Unknown"
        )
    else:
        df['year_display'] = "Unknown"
    
    # Phase and grade
    df['phase'] = df.get('phase_display', 'Unknown')
    df['grade'] = df.get('grade_display', df.get('grade', 'Unknown'))
    
    return df

def apply_filters(df, subjects, phases, grades):
    """Apply selected filters to dataframe."""
    filtered = df.copy()
    
    if subjects:
        filtered = filtered[filtered['subject'].isin(subjects)]
    if phases:
        filtered = filtered[filtered['phase'].isin(phases)]
    if grades:
        filtered = filtered[filtered['grade'].isin(grades)]
    
    return filtered

def weighted_mean(values, weights):
    """Calculate weighted mean."""
    v = pd.to_numeric(values, errors='coerce')
    w = pd.to_numeric(weights, errors='coerce').fillna(0)
    total_weight = w.sum()
    if total_weight > 0:
        return float((v.fillna(0) * w).sum() / total_weight)
    return np.nan

def calculate_metrics(df):
    """Calculate key metrics for a dataframe."""
    df_clean = df[df['class_size'] > 0].copy()
    
    return {
        'total_classes': len(df),
        'total_learners': int(df['class_size'].sum()),
        'total_fellows': df['fellow_name'].nunique() if 'fellow_name' in df else 0,
        'term_1_avg': weighted_mean(df_clean['term_1_avg'], df_clean['class_size']),
        'term_2_avg': weighted_mean(df_clean['term_2_avg'], df_clean['class_size']),
        'pass_count_t1': int(df['pass_term_1'].sum()),
        'pass_count_t2': int(df['pass_term_2'].sum()),
        'improvement': weighted_mean(df_clean['improvement'], df_clean['class_size']),
    }