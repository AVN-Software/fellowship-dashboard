import pandas as pd

def calculate_movements(df: pd.DataFrame, segment_col: str) -> pd.DataFrame:
    """Calculate term-to-term movements for a domain/segment."""
    movement_data = []

    for domain in sorted(df['domain'].unique()):
        domain_data = df[df['domain'] == domain].sort_values('term')

        if segment_col and segment_col != "both":
            for segment_val in sorted(domain_data[segment_col].unique()):
                seg_data = domain_data[domain_data[segment_col] == segment_val]
                _calculate_domain_movements(movement_data, seg_data, domain, segment_val)
        else:
            agg_data = domain_data.groupby('term').agg({
                'tier_mix_t1_pct': 'mean',
                'tier_mix_t2_pct': 'mean',
                'tier_mix_t3_pct': 'mean',
                'dominant_index': 'mean'
            }).reset_index()
            _calculate_domain_movements(movement_data, agg_data, domain)

    return pd.DataFrame(movement_data)


def _calculate_domain_movements(movement_data: list, data: pd.DataFrame, domain: str, segment_val: str = None):
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
