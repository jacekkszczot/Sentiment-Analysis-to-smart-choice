import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from pathlib import Path
import sys
import json
import time
import io

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

# Import our modules
from data_collector import DataCollector
from sentiment_analyzer import SentimentAnalyzer
from visualizer import SentimentVisualizer
from utils import *
import config

# Page configuration
st.set_page_config(
    page_title="Brand Sentiment Monitor",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for better contrast and readability
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .live-indicator {
        background: linear-gradient(90deg, #28a745, #20c997);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9em;
        display: inline-block;
        margin: 0.5rem 0;
    }
    
    .data-source-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #dee2e6;
        margin: 0.5rem 0;
        color: #333;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: #333;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #dee2e6;
    }
    
    .export-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 2px solid #dee2e6;
        margin: 2rem 0;
        color: #333;
    }
    
    .metric-highlight {
        background: #e7f3ff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 0.5rem 0;
        color: #333;
    }
    
    .stAlert > div {
        background-color: white !important;
        color: #333 !important;
        border: 1px solid #dee2e6 !important;
    }
    
    .stSuccess > div {
        background-color: #d4edda !important;
        color: #155724 !important;
        border: 1px solid #c3e6cb !important;
    }
    
    .stInfo > div {
        background-color: #d1ecf1 !important;
        color: #0c5460 !important;
        border: 1px solid #bee5eb !important;
    }
    
    .stWarning > div {
        background-color: #fff3cd !important;
        color: #856404 !important;
        border: 1px solid #ffeaa7 !important;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'analysis_data' not in st.session_state:
        st.session_state.analysis_data = None
    if 'summary_stats' not in st.session_state:
        st.session_state.summary_stats = None
    if 'last_brand' not in st.session_state:
        st.session_state.last_brand = ""
    if 'show_detailed' not in st.session_state:
        st.session_state.show_detailed = False
    if 'uploaded_data' not in st.session_state:
        st.session_state.uploaded_data = None

def create_csv_template():
    """Create downloadable CSV template"""
    template_data = {
        'title': [
            'Great experience with this brand',
            'Disappointed with customer service',
            'Mixed feelings about recent update',
            'Amazing product quality',
            'Price is too high for value'
        ],
        'text': [
            'This brand consistently delivers high-quality products. Very satisfied with my purchase.',
            'Customer support was unhelpful and took too long to respond. Frustrating experience.',
            'Some new features are good but others seem unnecessary. Not sure about direction.',
            'Outstanding build quality and attention to detail. Worth every penny spent.',
            'Product is decent but overpriced compared to competitors. Expected more for the cost.'
        ],
        'score': [145, -25, 30, 200, -10],
        'comments': [23, 8, 15, 45, 12],
        'date': ['2024-01-15', '2024-01-14', '2024-01-13', '2024-01-12', '2024-01-11'],
        'source': ['reddit', 'twitter', 'review_site', 'reddit', 'forum'],
        'brand': ['YourBrand', 'YourBrand', 'YourBrand', 'YourBrand', 'YourBrand']
    }
    df = pd.DataFrame(template_data)
    return df.to_csv(index=False)

def create_professional_report(df: pd.DataFrame, summary_stats: Dict, brand: str) -> str:
    """Create comprehensive HTML report for clients"""
    positive_pct = (df['final_sentiment'] == 'positive').mean() * 100
    negative_pct = (df['final_sentiment'] == 'negative').mean() * 100
    neutral_pct = (df['final_sentiment'] == 'neutral').mean() * 100
    trend = calculate_sentiment_trend(df)
    trend_emoji = get_trend_emoji(trend)
    data_source = "Live Google News" if df.iloc[0]['source'] == 'google_news_live' else "Sample Data Analysis"
    
    # Get top positive and negative examples
    positive_examples = df[df['final_sentiment'] == 'positive'].nlargest(3, 'final_confidence')
    negative_examples = df[df['final_sentiment'] == 'negative'].nlargest(3, 'final_confidence')
    
    html_report = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Brand Sentiment Analysis Report - {brand}</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ 
                font-family: 'Arial', sans-serif; 
                max-width: 1000px; 
                margin: 0 auto; 
                padding: 20px; 
                line-height: 1.6;
                background-color: #f8f9fa;
                color: #333;
            }}
            .container {{ 
                background: white; 
                padding: 40px; 
                border-radius: 15px; 
                box-shadow: 0 4px 6px rgba(0,0,0,0.1); 
            }}
            .header {{ 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                color: white; 
                padding: 40px; 
                border-radius: 15px; 
                text-align: center; 
                margin-bottom: 30px;
            }}
            .executive-summary {{
                background: #e7f3ff;
                padding: 30px;
                border-radius: 10px;
                margin: 30px 0;
                border-left: 5px solid #007bff;
            }}
            .metrics-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); 
                gap: 20px; 
                margin: 30px 0; 
            }}
            .metric {{ 
                background: #f8f9fa; 
                padding: 25px; 
                border-radius: 10px; 
                text-align: center; 
                border: 2px solid #e9ecef;
                transition: transform 0.3s ease;
            }}
            .metric:hover {{ transform: translateY(-5px); }}
            .metric-value {{ 
                font-size: 32px; 
                font-weight: bold; 
                margin-bottom: 8px; 
            }}
            .metric-label {{ 
                color: #6c757d; 
                font-size: 14px; 
                text-transform: uppercase;
                letter-spacing: 1px;
            }}
            .sentiment-positive {{ color: #28a745; }}
            .sentiment-negative {{ color: #dc3545; }}
            .sentiment-neutral {{ color: #6c757d; }}
            .insights {{ 
                background: #fff3cd; 
                padding: 25px; 
                border-radius: 10px; 
                margin: 30px 0; 
                border-left: 5px solid #ffc107;
            }}
            .examples {{
                background: #f8f9fa;
                padding: 25px;
                border-radius: 10px;
                margin: 20px 0;
            }}
            .example-item {{
                background: white;
                padding: 15px;
                margin: 10px 0;
                border-radius: 8px;
                border-left: 4px solid #007bff;
            }}
            .methodology {{
                background: #e9ecef;
                padding: 25px;
                border-radius: 10px;
                margin: 30px 0;
            }}
            .footer {{ 
                text-align: center; 
                margin-top: 40px; 
                padding-top: 20px; 
                border-top: 2px solid #e9ecef; 
                color: #6c757d; 
            }}
            .recommendations {{
                background: #d1ecf1;
                padding: 25px;
                border-radius: 10px;
                margin: 30px 0;
                border-left: 5px solid #17a2b8;
            }}
            .chart-placeholder {{
                background: #f8f9fa;
                border: 2px dashed #dee2e6;
                padding: 40px;
                text-align: center;
                border-radius: 10px;
                margin: 20px 0;
                color: #6c757d;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>📊 Brand Sentiment Analysis Report</h1>
                <h2>{brand}</h2>
                <p style="font-size: 1.1em; margin-top: 1rem;">
                    Professional sentiment analysis powered by AI and live news data
                </p>
                <p style="font-size: 0.9em; opacity: 0.9;">
                    Generated: {datetime.now().strftime('%B %d, %Y at %H:%M')}
                </p>
            </div>
            
            <div class="executive-summary">
                <h3>📋 Executive Summary</h3>
                <p><strong>Analysis Overview:</strong> This comprehensive sentiment analysis of {brand} examined {len(df):,} data points from {data_source.lower()}, providing insights into public perception and brand sentiment trends.</p>
                
                <p><strong>Key Finding:</strong> {brand} demonstrates {"predominantly positive sentiment" if positive_pct > 50 else "mixed sentiment with opportunities for improvement" if positive_pct > 30 else "challenging sentiment requiring strategic attention"} across analyzed content, with {positive_pct:.1f}% positive mentions and a {trend.replace('_', ' ')} trend trajectory.</p>
                
                <p><strong>Data Quality:</strong> Analysis confidence averaged {df['final_confidence'].mean():.3f} across all processed content, indicating {"high reliability" if df['final_confidence'].mean() > 0.7 else "good reliability" if df['final_confidence'].mean() > 0.5 else "moderate reliability"} in sentiment classification.</p>
            </div>
            
            <div class="metrics-grid">
                <div class="metric">
                    <div class="metric-value">{len(df):,}</div>
                    <div class="metric-label">Total Data Points</div>
                </div>
                <div class="metric">
                    <div class="metric-value sentiment-positive">{positive_pct:.1f}%</div>
                    <div class="metric-label">Positive Sentiment</div>
                </div>
                <div class="metric">
                    <div class="metric-value sentiment-negative">{negative_pct:.1f}%</div>
                    <div class="metric-label">Negative Sentiment</div>
                </div>
                <div class="metric">
                    <div class="metric-value sentiment-neutral">{neutral_pct:.1f}%</div>
                    <div class="metric-label">Neutral Sentiment</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{df['final_confidence'].mean():.3f}</div>
                    <div class="metric-label">Avg Confidence</div>
                </div>
                <div class="metric">
                    <div class="metric-value">{trend_emoji}</div>
                    <div class="metric-label">{trend.replace('_', ' ').title()}</div>
                </div>
            </div>
            
            <div class="chart-placeholder">
                <h4>📊 Sentiment Distribution Visualization</h4>
                <p>Interactive charts would be embedded here in the full implementation<br>
                Positive: {positive_pct:.1f}% | Negative: {negative_pct:.1f}% | Neutral: {neutral_pct:.1f}%</p>
            </div>
            
            <div class="insights">
                <h3>💡 Key Insights & Strategic Analysis</h3>
                <ul>
                    <li><strong>Overall Brand Perception:</strong> {brand} shows {"strong positive momentum" if positive_pct > 60 else "balanced perception with positive lean" if positive_pct > 45 else "mixed sentiment requiring attention" if positive_pct > 30 else "challenging brand perception"} in public discourse.</li>
                    
                    <li><strong>Sentiment Distribution:</strong> The {positive_pct:.1f}% positive sentiment rate {"exceeds industry benchmarks" if positive_pct > 50 else "aligns with industry standards" if positive_pct > 40 else "suggests room for improvement"} and indicates {"effective brand management" if positive_pct > negative_pct * 2 else "balanced but competitive landscape"}.</li>
                    
                    <li><strong>Trend Analysis:</strong> The {trend.replace('_', ' ')} sentiment trend {trend_emoji} suggests {"sustained positive momentum" if trend == "improving" else "stable brand perception" if trend == "stable" else "need for proactive brand management"}.</li>
                    
                    <li><strong>Data Reliability:</strong> With an average confidence score of {df['final_confidence'].mean():.3f}, our analysis provides {"high-confidence insights" if df['final_confidence'].mean() > 0.7 else "reliable insights" if df['final_confidence'].mean() > 0.5 else "directional insights"} suitable for strategic decision-making.</li>
                </ul>
            </div>
    """
    
    # Add examples if available
    if len(positive_examples) > 0:
        html_report += f"""
            <div class="examples">
                <h3>✅ Top Positive Sentiment Examples</h3>
        """
        for idx, row in positive_examples.iterrows():
            text_preview = (row['original_text'][:150] + "..." if len(row['original_text']) > 150 else row['original_text'])
            html_report += f"""
                <div class="example-item">
                    <strong>Confidence: {row['final_confidence']:.3f}</strong><br>
                    "{text_preview}"
                </div>
            """
        html_report += "</div>"
    
    if len(negative_examples) > 0:
        html_report += f"""
            <div class="examples">
                <h3>⚠️ Top Negative Sentiment Examples</h3>
        """
        for idx, row in negative_examples.iterrows():
            text_preview = (row['original_text'][:150] + "..." if len(row['original_text']) > 150 else row['original_text'])
            html_report += f"""
                <div class="example-item">
                    <strong>Confidence: {row['final_confidence']:.3f}</strong><br>
                    "{text_preview}"
                </div>
            """
        html_report += "</div>"
    
    html_report += f"""
            <div class="recommendations">
                <h3>🎯 Strategic Recommendations</h3>
                <ol>
                    <li><strong>{"Amplify Positive Messaging" if positive_pct > 50 else "Address Negative Sentiment"}:</strong> {"Leverage the strong positive sentiment by amplifying successful messaging and campaigns" if positive_pct > 50 else "Develop targeted communication strategies to address areas of concern highlighted in negative sentiment"}.</li>
                    
                    <li><strong>Monitoring Strategy:</strong> Implement {"weekly" if trend == "declining" or negative_pct > 30 else "bi-weekly"} sentiment monitoring to track brand perception changes and respond proactively to emerging trends.</li>
                    
                    <li><strong>Content Strategy:</strong> {"Focus on reinforcing positive themes that resonate with your audience" if positive_pct > 50 else "Develop content addressing specific concerns raised in negative feedback"}.</li>
                    
                    <li><strong>Stakeholder Communication:</strong> {"Share positive sentiment data with stakeholders to reinforce brand strength" if positive_pct > 50 else "Develop proactive communication plan for stakeholders regarding brand challenges and response strategies"}.</li>
                </ol>
            </div>
            
            <div class="methodology">
                <h3>🔬 Analysis Methodology</h3>
                <p><strong>Data Collection:</strong> {data_source} providing recent, relevant brand mentions and discussions.</p>
                <p><strong>Sentiment Analysis:</strong> Advanced Natural Language Processing using TextBlob sentiment analysis engine with confidence scoring.</p>
                <p><strong>Classification:</strong> Three-tier sentiment classification (Positive, Negative, Neutral) with confidence thresholds.</p>
                <p><strong>Trend Analysis:</strong> Temporal analysis of sentiment changes using linear regression on sentiment scores.</p>
                <p><strong>Quality Assurance:</strong> Multi-layer validation ensuring analysis accuracy and relevance.</p>
            </div>
            
            <div style="background: #f8f9fa; padding: 20px; border-radius: 10px; margin-top: 30px;">
                <h3>📊 Technical Summary</h3>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                    <div>
                        <p><strong>Sample Size:</strong> {len(df):,} data points</p>
                        <p><strong>Analysis Date:</strong> {datetime.now().strftime('%Y-%m-%d')}</p>
                        <p><strong>Data Source:</strong> {data_source}</p>
                    </div>
                    <div>
                        <p><strong>Confidence Range:</strong> {df['final_confidence'].min():.3f} - {df['final_confidence'].max():.3f}</p>
                        <p><strong>Processing Time:</strong> Real-time analysis</p>
                        <p><strong>Analysis Type:</strong> Comprehensive sentiment analysis</p>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <h3>📧 Brand Sentiment Monitor</h3>
                <p><strong>Professional AI-powered sentiment analysis platform</strong></p>
                <p>This report was generated using advanced natural language processing and machine learning techniques to provide actionable insights for strategic brand management.</p>
                <p style="font-size: 12px; margin-top: 20px; color: #999;">
                    Report generated on {datetime.now().strftime('%B %d, %Y')} | For questions about methodology or custom analysis requirements, please contact your analysis team.
                </p>
            </div>
        </div>
    </body>
    </html>
    """
    return html_report

def main():
    initialize_session_state()
    
    # Header
    st.markdown('''
    <div class="main-header">
        📊 Brand Sentiment Monitor
    </div>
    <div style="text-align: center; margin-bottom: 2rem; color: #6c757d; font-size: 1.1em;">
        <em>Professional AI-powered sentiment analysis with live data & comprehensive reporting</em>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Brand Analysis")
        
        # Brand selection method
        brand_input_method = st.radio(
            "Choose brand input method:",
            ["🔍 Select from popular brands", "✏️ Enter custom brand"],
            help="Choose how you want to specify the brand to analyze"
        )
        
        if brand_input_method == "🔍 Select from popular brands":
            brand = st.selectbox(
                "Select a brand to analyze:",
                options=load_sample_brands(),
                index=0,
                help="Choose from our curated list of popular brands"
            )
        else:
            brand = st.text_input(
                "Enter brand name:",
                value="Tesla",
                placeholder="e.g., McDonald's, Volkswagen, Spotify...",
                help="Enter any brand name - we'll search live news about it!"
            )
        
        # Validation
        if not validate_brand_input(brand):
            st.error("⚠️ Please enter a valid brand name")
            return
        
        # Data source options
        st.markdown("### 📡 Data Sources")
        
        data_source = st.radio(
            "Choose your data source:",
            [
                "📰 Live Google News (Recommended)",
                "📊 Dynamic sample data patterns",  
                "📁 Upload your own CSV file"
            ],
            help="Live news gives real articles about your brand!"
        )
        
        if data_source == "📰 Live Google News (Recommended)":
            st.markdown("""
            <div class="data-source-card">
                <h5>🔴 Live Google News</h5>
                <p>Real-time news articles about your brand from Google News RSS feed.</p>
                <ul style="font-size: 0.9em;">
                    <li>✅ Fresh articles (last 7 days)</li>
                    <li>✅ Multiple news sources</li>
                    <li>✅ Real headlines & content</li>
                    <li>✅ Works for ANY brand</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            days_back = st.slider("📅 Days to search back:", 1, 14, 7)
            use_live_news = True
            use_sample_data = False
            use_uploaded_data = False
            
        elif data_source == "📊 Dynamic sample data patterns":
            st.markdown("""
            <div class="data-source-card">
                <h5>🎲 Dynamic Sample Data</h5>
                <p>AI-generated realistic data with brand-specific patterns.</p>
                <ul style="font-size: 0.9em;">
                    <li>✅ Different results per brand</li>
                    <li>✅ Realistic sentiment patterns</li>
                    <li>✅ Variable post volumes</li>
                    <li>✅ Quick testing & demos</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            use_live_news = False
            use_sample_data = True
            use_uploaded_data = False
            days_back = 7
            
        else:  # Upload CSV
            st.markdown("### 📁 Upload Your Data")
            
            # CSV Template download
            template_csv = create_csv_template()
            st.download_button(
                label="📥 Download CSV Template",
                data=template_csv,
                file_name="sentiment_template.csv",
                mime="text/csv",
                use_container_width=True,
                help="Download template with correct column format"
            )
            
            # File uploader
            uploaded_file = st.file_uploader(
                "Choose CSV file",
                type=['csv'],
                help="Upload CSV with 'title' and 'text' columns (required). Optional: score, comments, date, source, brand"
            )
            
            if uploaded_file is not None:
                try:
                    df = pd.read_csv(uploaded_file)
                    st.success(f"✅ Uploaded {len(df)} rows successfully!")
                    
                    with st.expander("📋 Preview uploaded data", expanded=True):
                        st.dataframe(df.head(), use_container_width=True)
                        st.info(f"**Columns detected:** {', '.join(df.columns.tolist())}")
                    
                    st.session_state.uploaded_data = uploaded_file
                    use_live_news = False
                    use_sample_data = False
                    use_uploaded_data = True
                    
                except Exception as e:
                    st.error(f"❌ Error reading CSV: {str(e)}")
                    st.info("💡 Make sure your CSV has 'title' and 'text' columns")
                    use_live_news = False
                    use_sample_data = True
                    use_uploaded_data = False
            else:
                st.info("👆 Upload a CSV file to analyze your own data")
                use_live_news = False
                use_sample_data = True
                use_uploaded_data = False
            
            days_back = 7
        
        # Analysis settings
        st.markdown("### ⚙️ Analysis Settings")
        max_articles = st.slider("Maximum posts to analyze:", 10, 100, 50)
        confidence_threshold = st.slider("Confidence threshold:", 0.0, 1.0, 0.0, 0.1, 
                                       help="Filter out low-confidence predictions")
        
        # Run button
        st.markdown("---")
        run_analysis = st.button(
            "🚀 Run Comprehensive Analysis",
            type="primary",
            use_container_width=True
        )
    
    # Main content
    if run_analysis or st.session_state.last_brand != brand:
        st.session_state.last_brand = brand
        
        # Progress
        progress_bar = st.progress(0, text="Starting comprehensive analysis...")
        
        with st.spinner(f"🔍 Analyzing sentiment for {brand}..."):
            # Initialize
            progress_bar.progress(10, text="Loading AI components...")
            collector = DataCollector(config)
            analyzer = SentimentAnalyzer(config)
            visualizer = SentimentVisualizer(config)
            
            # Collect data
            progress_bar.progress(30, text="Collecting data...")
            
            if use_live_news:
                st.info(f"📰 Searching live Google News for: {brand}")
                progress_bar.progress(50, text=f"Searching Google News for {brand}...")
                
                raw_data = collector.collect_live_news(brand, days_back=days_back)
                
                if not raw_data or len(raw_data) < 5:
                    st.warning(f"⚠️ Found only {len(raw_data)} news articles for '{brand}'. Adding sample data for robust analysis.")
                    sample_backup = collector.collect_sample_data(brand)
                    raw_data.extend(sample_backup)
                else:
                    st.success(f"✅ Found {len(raw_data)} recent news articles about {brand}!")
                    
            elif use_uploaded_data and st.session_state.uploaded_data is not None:
                st.info(f"📁 Processing uploaded data for {brand}")
                temp_path = config.RAW_DATA_DIR / "temp_upload.csv"
                with open(temp_path, "wb") as f:
                    f.write(st.session_state.uploaded_data.getbuffer())
                raw_data = collector.load_custom_csv(temp_path)
                
                if not raw_data:
                    st.warning("⚠️ No valid data in uploaded file. Using sample data instead.")
                    raw_data = collector.collect_sample_data(brand)
            else:
                st.info(f"📊 Using dynamic sample data patterns for {brand}")
                raw_data = collector.collect_sample_data(brand)
            
            # Analyze sentiment
            progress_bar.progress(70, text="Analyzing sentiment with advanced AI...")
            if raw_data:
                # Limit to max_articles
                if len(raw_data) > max_articles:
                    raw_data = raw_data[:max_articles]
                    st.info(f"📊 Analyzing top {max_articles} most recent posts")
                
                analysis_df = analyzer.analyze_batch(raw_data)
                
                # Apply confidence filter
                if confidence_threshold > 0:
                    initial_count = len(analysis_df)
                    analysis_df = analysis_df[analysis_df['final_confidence'] >= confidence_threshold]
                    filtered_count = len(analysis_df)
                    
                    if filtered_count < initial_count:
                        st.info(f"🎯 Filtered {initial_count - filtered_count} low-confidence predictions (below {confidence_threshold:.1f})")
                
                summary_stats = analyzer.get_summary_stats(analysis_df)
                
                st.session_state.analysis_data = analysis_df
                st.session_state.summary_stats = summary_stats
                
                progress_bar.progress(100, text="Analysis complete!")
                
                # Show data source info
                data_source_info = "Live Google News" if use_live_news else "Custom Uploaded Data" if use_uploaded_data else "Dynamic Sample Data"
                st.success(f"✅ Comprehensive analysis complete! Processed {len(analysis_df)} posts from {data_source_info}")
                
                time.sleep(1)
                progress_bar.empty()
            else:
                st.error("❌ No data could be collected for analysis.")
                return
    
    # Display results
    if st.session_state.analysis_data is not None and not st.session_state.analysis_data.empty:
        display_analysis_results(
            st.session_state.analysis_data,
            st.session_state.summary_stats,
            brand
        )
    else:
        display_welcome_message()

def display_welcome_message():
    """Enhanced welcome message"""
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); border-radius: 15px; color: white; margin: 2rem auto; max-width: 800px;">
        <h2>🚀 Welcome to Brand Sentiment Monitor!</h2>
        <p>Enter ANY brand name and get live sentiment analysis from Google News!</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        #### 📰 Live Google News
        - Real news articles
        - Any brand, any company
        - Fresh content (last 7 days)
        - Multiple news sources
        """)
    
    with col2:
        st.markdown("""
        #### 📊 Sample Data Patterns
        - AI-generated realistic data
        - Brand-specific patterns
        - Different results per brand
        - Quick testing
        """)
    
    # Example brands
    st.markdown("---")
    st.markdown("### 💡 Try These Brands:")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("**🚗 Automotive:**\n- Tesla\n- Volkswagen\n- Toyota")
    
    with col2:
        st.markdown("**🍔 Food:**\n- McDonald's\n- Starbucks\n- KFC")
    
    with col3:
        st.markdown("**💻 Tech:**\n- Apple\n- Microsoft\n- Google")
    
    with col4:
        st.markdown("**🎵 Media:**\n- Netflix\n- Spotify\n- Disney")

def display_analysis_results(df: pd.DataFrame, summary_stats: Dict, brand: str):
    """Display results with safe column access"""
    
    visualizer = SentimentVisualizer(config)
    
    # Debug: Check what columns we have
    
    # Determine data source safely
    data_source_info = "Live Google News" if 'source' in df.columns and df.iloc[0]['source'] == 'google_news_live' else "Sample Data"
    
    # Header
    if data_source_info == "Live Google News":
        header_color = "linear-gradient(90deg, #ff6b6b, #ee5a24)"
        live_badge = "🔴 LIVE"
    else:
        header_color = "linear-gradient(90deg, #28a745, #20c997)"
        live_badge = "📊 DATA"
    
    st.markdown(f"""
    <div style="background: {header_color}; padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; text-align: center;">
        <h2 style="margin: 0;">{live_badge} Sentiment Analysis for {brand}</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">{len(df)} posts from {data_source_info}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    metrics = visualizer.create_dashboard_summary(summary_stats)
    trend = calculate_sentiment_trend(df)
    trend_emoji = get_trend_emoji(trend)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📊 Posts", metrics['total_posts'])
    with col2:
        st.metric("😊 Positive", metrics['positive_percentage'])
    with col3:
        st.metric("😞 Negative", metrics['negative_percentage'])
    with col4:
        st.metric("🎯 Confidence", metrics['avg_confidence'])
    with col5:
        st.metric(f"📈 Trend {trend_emoji}", trend.replace('_', ' ').title())
    
    st.markdown("---")
    
    # Charts
    st.markdown("## 📊 Dashboard")
    
    tab1, tab2 = st.tabs(["📈 Overview", "📊 Analysis"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            pie_chart = visualizer.create_sentiment_pie_chart(summary_stats)
            st.plotly_chart(pie_chart, use_container_width=True)
        with col2:
            bar_chart = visualizer.create_sentiment_bar_chart(df)
            st.plotly_chart(bar_chart, use_container_width=True)
    
    with tab2:
        timeline_chart = visualizer.create_sentiment_timeline(df)
        st.plotly_chart(timeline_chart, use_container_width=True)
    
    # Recent headlines for live news - SAFE VERSION
    if data_source_info == "Live Google News":
        st.markdown("---")
        st.markdown("## 📰 Recent Headlines")
        
        # Show first few rows with safe column access
        for idx in range(min(5, len(df))):
            row = df.iloc[idx]
            
            sentiment_color = {"positive": "🟢", "negative": "🔴", "neutral": "🟡"}[row['final_sentiment']]
            
            # Safe access to columns
            title = row.get('original_text', 'No title available')[:100] + "..." if len(str(row.get('original_text', ''))) > 100 else row.get('original_text', 'No title')
            
            date_str = row['created_utc'].strftime('%Y-%m-%d %H:%M') if 'created_utc' in df.columns else 'Unknown date'
            confidence = row['final_confidence'] if 'final_confidence' in df.columns else 0
            
            st.markdown(f"""
            **{sentiment_color} {title}**  
            *{date_str} | Confidence: {confidence:.3f}*
            """)
    
    # Export section
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        # CSV download
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📊 Download Analysis (CSV)",
            data=csv_data,
            file_name=f"{brand.lower()}_sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        if st.button("🔄 Analyze Different Brand", use_container_width=True):
            st.session_state.analysis_data = None
            st.session_state.summary_stats = None
            st.rerun()
    
    # Raw data debug
    with st.expander("🔍 Raw Data Debug", expanded=False):
        st.dataframe(df.head(), use_container_width=True)

if __name__ == "__main__":
    main()
