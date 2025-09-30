import pandas as pd

def build_tier_mix_summary(df: pd.DataFrame, segment_col: str) -> pd.DataFrame:
    """Build summary dataframe for tier mix table."""
    summary_data = []

    for domain in sorted(df['domain'].unique()):
        domain_data = df[df['domain'] == domain]

        if segment_col and segment_col != "both":
            for segment_val in sorted(domain_data[segment_col].unique()):
                seg_data = domain_data[domain_data[segment_col] == segment_val]
                _add_progression_row(summary_data, seg_data, domain, segment_val)
        else:
            agg_data = domain_data.groupby('term').agg({
                'tier_mix_t1_pct': 'mean',
                'tier_mix_t2_pct': 'mean',
                'tier_mix_t3_pct': 'mean',
                'dominant_index': 'mean'
            }).reset_index()
            _add_progression_row(summary_data, agg_data, domain)

    return pd.DataFrame(summary_data)


def _add_progression_row(summary_data: list, data: pd.DataFrame, domain: str, segment_val: str = None):
    terms = sorted(data['term'].unique())

    if len(terms) < 2:
        return

    row = {
        'Domain': domain,
        'Segment': segment_val or 'Overall'
    }

    for term in terms:
        term_data = data[data['term'] == term].iloc[0] if len(data[data['term'] == term]) > 0 else None
        if term_data is not None:
            row[f'{term} T1%'] = term_data['tier_mix_t1_pct']
            row[f'{term} T2%'] = term_data['tier_mix_t2_pct']
            row[f'{term} T3%'] = term_data['tier_mix_t3_pct']
            row[f'{term} Index'] = term_data['dominant_index']

    if len(terms) >= 2:
        first_term = data[data['term'] == terms[0]].iloc[0]
        last_term = data[data['term'] == terms[-1]].iloc[0]

        row['T3 Change'] = last_term['tier_mix_t3_pct'] - first_term['tier_mix_t3_pct']
        row['Index Change'] = last_term['dominant_index'] - first_term['dominant_index']

    summary_data.append(row)
