# Dodaj do app.py - zamień sekcję export na tę ulepszoną wersję

def create_shareable_report(df: pd.DataFrame, summary_stats: Dict, brand: str) -> str:
    """Create shareable HTML report"""
    
    positive_pct = (df['final_sentiment'] == 'positive').mean() * 100
    negative_pct = (df['final_sentiment'] == 'negative').mean() * 100
    neutral_pct = (df['final_sentiment'] == 'neutral').mean() * 100
    trend = calculate_sentiment_trend(df)
    trend_emoji = get_trend_emoji(trend)
    
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sentiment Analysis Report - {brand}</title>
        <style>
            body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(90deg, #4CAF50, #45a049); color: white; padding: 20px; border-radius: 10px; text-align: center; }}
            .metrics {{ display: flex; justify-content: space-around; margin: 20px 0; }}
            .metric {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; border: 1px solid #dee2e6; }}
            .metric-value {{ font-size: 24px; font-weight: bold; color: #007bff; }}
            .sentiment-positive {{ color: #28a745; }}
            .sentiment-negative {{ color: #dc3545; }}
            .sentiment-neutral {{ color: #6c757d; }}
            .footer {{ text-align: center; margin-top: 30px; color: #666; border-top: 1px solid #eee; padding-top: 15px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Brand Sentiment Analysis Report</h1>
            <h2>{brand}</h2>
            <p>Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}</p>
        </div>
        
        <div class="metrics">
            <div class="metric">
                <div class="metric-value">{len(df):,}</div>
                <div>Total Posts</div>
            </div>
            <div class="metric">
                <div class="metric-value sentiment-positive">{positive_pct:.1f}%</div>
                <div>Positive</div>
            </div>
            <div class="metric">
                <div class="metric-value sentiment-negative">{negative_pct:.1f}%</div>
                <div>Negative</div>
            </div>
            <div class="metric">
                <div class="metric-value sentiment-neutral">{neutral_pct:.1f}%</div>
                <div>Neutral</div>
            </div>
            <div class="metric">
                <div class="metric-value">{trend_emoji}</div>
                <div>{trend.replace('_', ' ').title()}</div>
            </div>
        </div>
        
        <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin: 20px 0;">
            <h3>📈 Key Insights</h3>
            <ul>
                <li><strong>Overall Sentiment:</strong> {"Positive" if positive_pct > negative_pct else "Negative" if negative_pct > positive_pct else "Neutral"} leaning</li>
                <li><strong>Confidence Level:</strong> {df['final_confidence'].mean():.3f}</li>
                <li><strong>Trend Direction:</strong> {trend.replace('_', ' ').title()}</li>
                <li><strong>Sample Size:</strong> {len(df):,} posts analyzed</li>
            </ul>
        </div>
        
        <div class="footer">
            <p><strong>Brand Sentiment Monitor</strong></p>
            <p>AI-powered sentiment analysis tool</p>
        </div>
    </body>
    </html>
    """
    return html_report

# UPGRADED EXPORT SECTION - zamień w display_analysis_results()
def display_enhanced_export_section(df, summary_stats, brand):
    st.markdown("---")
    st.markdown("## 💾 Export & Share Options")
    
    # Export tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📄 Data Export", "📊 Reports", "🔗 Share", "📱 Mobile"])
    
    with tab1:
        st.markdown("### 📄 Raw Data Downloads")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Full CSV
            csv_data = df.to_csv(index=False)
            st.download_button(
                label="📊 Complete Dataset (CSV)",
                data=csv_data,
                file_name=f"{brand.lower()}_complete_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv",
                help="Full analysis data with all columns",
                use_container_width=True,
                type="primary"
            )
            
            # Positive only
            positive_df = df[df['final_sentiment'] == 'positive']
            if len(positive_df) > 0:
                positive_csv = positive_df.to_csv(index=False)
                st.download_button(
                    label=f"😊 Positive Posts Only ({len(positive_df)} posts)",
                    data=positive_csv,
                    file_name=f"{brand.lower()}_positive_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with col2:
            # Summary JSON
            summary_json = json.dumps(summary_stats, indent=2, default=str)
            st.download_button(
                label="📋 Executive Summary (JSON)",
                data=summary_json,
                file_name=f"{brand.lower()}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                help="Key metrics and statistics",
                use_container_width=True
            )
            
            # Negative only
            negative_df = df[df['final_sentiment'] == 'negative']
            if len(negative_df) > 0:
                negative_csv = negative_df.to_csv(index=False)
                st.download_button(
                    label=f"😞 Negative Posts Only ({len(negative_df)} posts)",
                    data=negative_csv,
                    file_name=f"{brand.lower()}_negative_only_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv",
                    use_container_width=True
                )
    
    with tab2:
        st.markdown("### 📊 Professional Reports")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # HTML Report
            if st.button("📄 Generate HTML Report", use_container_width=True, type="primary"):
                html_report = create_shareable_report(df, summary_stats, brand)
                st.download_button(
                    label="💾 Download HTML Report",
                    data=html_report,
                    file_name=f"{brand.lower()}_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                    mime="text/html",
                    use_container_width=True
                )
                st.success("✅ HTML report generated!")
            
            # PowerPoint-ready data
            if st.button("📊 PowerPoint Data", use_container_width=True):
                ppt_data = f"""BRAND SENTIMENT ANALYSIS - {brand.upper()}

KEY METRICS:
- Total Posts: {len(df):,}
- Positive: {(df['final_sentiment'] == 'positive').mean()*100:.1f}%
- Negative: {(df['final_sentiment'] == 'negative').mean()*100:.1f}%
- Neutral: {(df['final_sentiment'] == 'neutral').mean()*100:.1f}%
- Confidence: {df['final_confidence'].mean():.3f}
- Trend: {calculate_sentiment_trend(df).replace('_', ' ').title()}

TOP POSITIVE PHRASES:
{', '.join(df[df['final_sentiment'] == 'positive']['cleaned_text'].str.split().explode().value_counts().head(5).index.tolist())}

TOP NEGATIVE PHRASES:
{', '.join(df[df['final_sentiment'] == 'negative']['cleaned_text'].str.split().explode().value_counts().head(5).index.tolist())}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Source: Brand Sentiment Monitor"""
                
                st.download_button(
                    label="💾 Download PPT Data",
                    data=ppt_data,
                    file_name=f"{brand.lower()}_ppt_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        with col2:
            # Executive Summary
            st.markdown("#### 📋 Executive Summary Preview")
            
            positive_pct = (df['final_sentiment'] == 'positive').mean() * 100
            negative_pct = (df['final_sentiment'] == 'negative').mean() * 100
            neutral_pct = (df['final_sentiment'] == 'neutral').mean() * 100
            
            st.info(f"""
            **{brand} Sentiment Analysis**
            
            📊 **Overview:**
            - {len(df):,} posts analyzed
            - {positive_pct:.1f}% positive sentiment
            - {negative_pct:.1f}% negative sentiment
            - {neutral_pct:.1f}% neutral sentiment
            
            📈 **Trend:** {calculate_sentiment_trend(df).replace('_', ' ').title()}
            
            🎯 **Confidence:** {df['final_confidence'].mean():.3f}
            """)
    
    with tab3:
        st.markdown("### 🔗 Share Your Analysis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📱 Quick Share")
            
            # Generate shareable text
            positive_pct = (df['final_sentiment'] == 'positive').mean() * 100
            negative_pct = (df['final_sentiment'] == 'negative').mean() * 100
            trend_emoji = get_trend_emoji(calculate_sentiment_trend(df))
            
            share_text = f"""📊 Brand Sentiment Analysis: {brand}

📈 Results:
- 😊 Positive: {positive_pct:.1f}%
- 😞 Negative: {negative_pct:.1f}%
- 📊 Total: {len(df):,} posts
- 🎯 Trend: {trend_emoji}

Generated with Brand Sentiment Monitor
{datetime.now().strftime('%Y-%m-%d %H:%M')}"""
            
            st.text_area(
                "Copy this summary:",
                share_text,
                height=150,
                help="Copy and paste this summary anywhere"
            )
            
            # Social media formatted
            if st.button("📱 Social Media Format", use_container_width=True):
                social_text = f"""🔥 Just analyzed {brand} sentiment! 

📊 {len(df):,} posts analyzed
😊 {positive_pct:.1f}% positive
😞 {negative_pct:.1f}% negative  
📈 Trend: {trend_emoji}

#SentimentAnalysis #{brand.replace(' ', '')} #DataScience #AI"""
                
                st.text_area("Social media ready:", social_text, height=100)
        
        with col2:
            st.markdown("#### 🔗 URL Sharing")
            
            # Create URL-friendly summary
            url_params = f"brand={brand}&positive={positive_pct:.1f}&negative={negative_pct:.1f}&total={len(df)}"
            
            st.code(f"http://localhost:8501?{url_params}", language="text")
            st.caption("Share this URL to show your analysis parameters")
            
            # QR Code placeholder
            if st.button("📱 Generate QR Code", use_container_width=True):
                st.info("💡 QR Code generation would require additional library (qrcode)")
                st.code("pip install qrcode[pil]", language="bash")
            
            # Email template
            if st.button("📧 Email Template", use_container_width=True):
                email_text = f"""Subject: {brand} Sentiment Analysis Results

Hi [Name],

I've completed the sentiment analysis for {brand}. Here are the key findings:

📊 OVERVIEW:
- Total posts analyzed: {len(df):,}
- Sentiment breakdown:
  - Positive: {positive_pct:.1f}%
  - Negative: {negative_pct:.1f}%
  - Neutral: {(100-positive_pct-negative_pct):.1f}%

📈 TREND: {calculate_sentiment_trend(df).replace('_', ' ').title()}

The full analysis data is attached as CSV files.

Best regards,
[Your Name]

Generated with Brand Sentiment Monitor"""
                
                st.text_area("Email template:", email_text, height=200)
    
    with tab4:
        st.markdown("### 📱 Mobile-Friendly Export")
        
        # Mobile summary
        st.markdown("#### 📱 Mobile Summary")
        
        mobile_summary = f"""{brand} Analysis 📊

Results:
😊 {positive_pct:.1f}% positive
😞 {negative_pct:.1f}% negative  
📊 {len(df):,} total posts
📈 {calculate_sentiment_trend(df).title()}

{datetime.now().strftime('%m/%d/%Y')}"""
        
        st.code(mobile_summary, language="text")
        
        # SMS-ready format
        if st.button("💬 SMS Format", use_container_width=True):
            sms_text = f"{brand}: {positive_pct:.0f}% pos, {negative_pct:.0f}% neg, {len(df)} posts. Trend: {get_trend_emoji(calculate_sentiment_trend(df))}"
            st.text_input("SMS ready (160 chars):", sms_text)
            st.caption(f"Length: {len(sms_text)} characters")
