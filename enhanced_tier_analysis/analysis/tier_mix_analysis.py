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

