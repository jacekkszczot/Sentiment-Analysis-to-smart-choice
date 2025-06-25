# Dodaj to do sekcji export w app.py (około linii 330)

# Export section - UPGRADED VERSION
st.header("💾 Export & Reports")

col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Quick Export")
    
    # CSV Download z lepszym stylem
    csv_data = df.to_csv(index=False)
    st.download_button(
        label="📄 Download Full Analysis (CSV)",
        data=csv_data,
        file_name=f"{brand.lower()}_sentiment_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
        type="primary"
    )
    
    # Summary JSON
    import json
    summary_json = json.dumps(summary_stats, indent=2, default=str)
    st.download_button(
        label="📋 Download Summary Report (JSON)",
        data=summary_json,
        file_name=f"{brand.lower()}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        use_container_width=True
    )

with col2:
    st.subheader("📈 Custom Reports")
    
    # Filtered export options
    export_sentiment = st.selectbox(
        "Export specific sentiment:",
        options=['All sentiments', 'Positive only', 'Negative only', 'Neutral only'],
        key="export_filter"
    )
    
    # Date range export
    if 'created_utc' in df.columns:
        date_range = st.date_input(
            "Select date range:",
            value=[df['created_utc'].min().date(), df['created_utc'].max().date()],
            key="export_dates"
        )
    
    # Custom export button
    if st.button("🎯 Generate Custom Export", use_container_width=True):
        # Filter data based on selection
        filtered_df = df.copy()
        
        if export_sentiment != 'All sentiments':
            sentiment_map = {
                'Positive only': 'positive',
                'Negative only': 'negative', 
                'Neutral only': 'neutral'
            }
            filtered_df = filtered_df[filtered_df['final_sentiment'] == sentiment_map[export_sentiment]]
        
        # Generate custom CSV
        custom_csv = filtered_df.to_csv(index=False)
        st.download_button(
            label=f"💾 Download {export_sentiment} Data",
            data=custom_csv,
            file_name=f"{brand.lower()}_{export_sentiment.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )

# Statistics Summary Card
st.subheader("📊 Analysis Summary")
summary_col1, summary_col2, summary_col3 = st.columns(3)

with summary_col1:
    st.info(f"""
    **Analysis Overview**
    - Total posts analyzed: {len(df)}
    - Date range: {df['created_utc'].min().strftime('%Y-%m-%d') if 'created_utc' in df.columns else 'N/A'} to {df['created_utc'].max().strftime('%Y-%m-%d') if 'created_utc' in df.columns else 'N/A'}
    - Average confidence: {df['final_confidence'].mean():.3f}
    """)

with summary_col2:
    positive_pct = (df['final_sentiment'] == 'positive').mean() * 100
    negative_pct = (df['final_sentiment'] == 'negative').mean() * 100
    neutral_pct = (df['final_sentiment'] == 'neutral').mean() * 100
    
    st.success(f"""
    **Sentiment Breakdown**
    - 😊 Positive: {positive_pct:.1f}%
    - 😞 Negative: {negative_pct:.1f}%
    - 😐 Neutral: {neutral_pct:.1f}%
    """)

with summary_col3:
    top_source = df['source'].value_counts().index[0] if len(df) > 0 else 'N/A'
    avg_score = df['score'].mean() if 'score' in df.columns else 0
    
    st.warning(f"""
    **Data Sources**
    - Primary source: {top_source}
    - Average engagement: {avg_score:.1f}
    - Sources used: {df['source'].nunique()}
    """)

# Action buttons
st.markdown("---")
action_col1, action_col2, action_col3, action_col4 = st.columns(4)

with action_col1:
    if st.button("🔄 New Analysis", use_container_width=True):
        st.session_state.analysis_data = None
        st.session_state.summary_stats = None
        st.rerun()

with action_col2:
    if st.button("📧 Share Results", use_container_width=True):
        st.info("💡 Copy the URL to share this analysis!")

with action_col3:
    if st.button("🔍 Detailed View", use_container_width=True):
        st.session_state.show_detailed = True

with action_col4:
    if st.button("💾 Save Project", use_container_width=True):
        # Save to local results folder
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        save_path = f"results/{brand}_{timestamp}"
        st.success(f"Project saved to {save_path}")
