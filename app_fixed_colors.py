import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import datetime, timedelta
import base64
from pathlib import Path
import sys
import json
import time

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

# FIXED CSS with better colors and contrast
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
    
    /* Fix for progress section - better contrast */
    .stProgress > div > div {
        background-color: #1f77b4;
    }
    
    /* Better info boxes */
    .stAlert[data-baseweb="notification"] {
        background-color: #f0f8ff !important;
        border: 1px solid #1f77b4 !important;
        color: #1f77b4 !important;
    }
    
    /* Success messages */
    .stSuccess {
        background-color: #d4edda !important;
        border: 1px solid #28a745 !important;
        color: #155724 !important;
    }
    
    /* Better metric cards */
    .metric-card {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: #333;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        border: 1px solid #dee2e6;
    }
    
    /* Sentiment colors with good contrast */
    .sentiment-positive { 
        color: #28a745; 
        font-weight: bold; 
        font-size: 1.2em;
    }
    .sentiment-negative { 
        color: #dc3545; 
        font-weight: bold; 
        font-size: 1.2em;
    }
    .sentiment-neutral { 
        color: #6c757d; 
        font-weight: bold; 
        font-size: 1.2em;
    }
    
    /* Export section with light background */
    .export-section {
        background-color: #f8f9fa;
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #e9ecef;
        margin: 1rem 0;
        color: #333;
    }
    
    /* Better button styling */
    .stButton > button {
        border-radius: 8px;
        border: 1px solid #dee2e6;
        background-color: white;
        color: #333;
        transition: all 0.3s ease;
    }
    
    .stButton > button[kind="primary"] {
        background-color: #007bff;
        color: white;
        border: none;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 2rem;
        color: #6c757d;
        border-top: 1px solid #dee2e6;
        margin-top: 3rem;
        background-color: #f8f9fa;
    }
    
    /* Text contrast fixes */
    .stMarkdown {
        color: #333;
    }
    
    /* Sidebar improvements */
    .css-1d391kg {
        background-color: #f8f9fa;
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

def main():
    initialize_session_state()
    
    # Header with better contrast
    st.markdown('''
    <div class="main-header">
        📊 Brand Sentiment Monitor
    </div>
    <div style="text-align: center; margin-bottom: 2rem; color: #6c757d; font-size: 1.1em;">
        <em>AI-powered sentiment analysis for brands across social media and news</em>
    </div>
    ''', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.markdown("### 🎯 Analysis Configuration")
        
        # Brand selection
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
                help="Enter any brand name you want to analyze",
                placeholder="e.g., Tesla, Apple, Nike..."
            )
        
        # Validation
        if not validate_brand_input(brand):
            st.error("⚠️ Please enter a valid brand name")
            return
        
        # Data source options
        st.markdown("### 📡 Data Sources")
        use_sample_data = st.checkbox("📊 Use sample data", value=True, help="Perfect for testing!")
        
        if not use_sample_data:
            st.info("🔧 Real data collection requires API setup")
            # API options would go here
        
        # Analysis settings
        st.markdown("### ⚙️ Analysis Settings")
        max_posts = st.slider("Maximum posts:", 50, 500, 100)
        
        # Run button
        st.markdown("---")
        run_analysis = st.button(
            "🚀 Run Sentiment Analysis",
            type="primary",
            use_container_width=True
        )
    
    # Main content
    if run_analysis or st.session_state.last_brand != brand:
        st.session_state.last_brand = brand
        
        # Progress section with better styling
        st.markdown("### 📊 Analysis Progress")
        progress_bar = st.progress(0, text="Starting analysis...")
        
        with st.spinner(f"🔍 Analyzing sentiment for {brand}..."):
            # Initialize components
            progress_bar.progress(20, text="Initializing components...")
            collector = DataCollector(config)
            analyzer = SentimentAnalyzer(config)
            visualizer = SentimentVisualizer(config)
            
            # Collect data
            progress_bar.progress(50, text="Collecting data...")
            if use_sample_data:
                st.info(f"📊 Using sample data for {brand}")
                raw_data = collector.collect_sample_data(brand)
            else:
                raw_data = collector.collect_sample_data(brand)  # Fallback
            
            # Analyze
            progress_bar.progress(80, text="Analyzing sentiment...")
            if raw_data:
                analysis_df = analyzer.analyze_batch(raw_data)
                summary_stats = analyzer.get_summary_stats(analysis_df)
                
                st.session_state.analysis_data = analysis_df
                st.session_state.summary_stats = summary_stats
                
                progress_bar.progress(100, text="Complete!")
                st.success(f"✅ Analyzed {len(analysis_df)} posts for {brand}")
                
                # Clear progress after delay
                time.sleep(1)
                progress_bar.empty()
    
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
    """Enhanced welcome message with better colors"""
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #007bff 0%, #0056b3 100%); border-radius: 15px; color: white; margin: 2rem auto; max-width: 800px;">
        <h2>🚀 Welcome to Brand Sentiment Monitor!</h2>
        <p style="font-size: 1.1em; margin-top: 1rem; opacity: 0.9;">
            Analyze public sentiment about any brand using advanced AI and NLP techniques
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border: 1px solid #dee2e6; height: 200px;">
            <h4 style="color: #007bff;">📊 Advanced Analytics</h4>
            <ul style="color: #333;">
                <li>Multi-source sentiment analysis</li>
                <li>Real-time trend detection</li>
                <li>Confidence scoring</li>
                <li>Interactive visualizations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border: 1px solid #dee2e6; height: 200px;">
            <h4 style="color: #28a745;">🔍 Smart Collection</h4>
            <ul style="color: #333;">
                <li>Social media monitoring</li>
                <li>News article analysis</li>
                <li>Automated data cleaning</li>
                <li>Sample data for testing</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div style="background: #f8f9fa; padding: 1.5rem; border-radius: 10px; border: 1px solid #dee2e6; height: 200px;">
            <h4 style="color: #dc3545;">💾 Professional Export</h4>
            <ul style="color: #333;">
                <li>CSV data export</li>
                <li>JSON summary reports</li>
                <li>Custom filtered exports</li>
                <li>Shareable results</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick start
    st.markdown("---")
    st.markdown("""
    <div style="background: #e7f3ff; padding: 2rem; border-radius: 10px; border-left: 5px solid #007bff; margin: 2rem 0;">
        <h3 style="color: #007bff; margin-bottom: 1rem;">🎯 Quick Start Guide</h3>
        <div style="color: #333;">
            <strong>Step 1:</strong> Choose a brand from the sidebar<br>
            <strong>Step 2:</strong> Keep "Use sample data" checked<br>
            <strong>Step 3:</strong> Click "Run Sentiment Analysis"<br>
            <strong>Step 4:</strong> Explore the interactive results!
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_analysis_results(df: pd.DataFrame, summary_stats: Dict, brand: str):
    """Display results with improved styling"""
    
    visualizer = SentimentVisualizer(config)
    
    # Header
    st.markdown(f"""
    <div style="background: linear-gradient(90deg, #28a745, #20c997); padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; text-align: center;">
        <h2 style="margin: 0;">📈 Sentiment Analysis Results for {brand}</h2>
        <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Complete analysis with interactive visualizations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Metrics
    metrics = visualizer.create_dashboard_summary(summary_stats)
    trend = calculate_sentiment_trend(df)
    trend_emoji = get_trend_emoji(trend)
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📊 Total Posts", metrics['total_posts'])
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
    st.markdown("## 📊 Interactive Dashboard")
    
    tab1, tab2, tab3 = st.tabs(["📈 Overview", "📊 Distribution", "🔍 Analysis"])
    
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
        
        source_chart = visualizer.create_source_analysis(df)
        st.plotly_chart(source_chart, use_container_width=True)
    
    with tab3:
        confidence_chart = visualizer.create_confidence_distribution(df)
        st.plotly_chart(confidence_chart, use_container_width=True)
        
        # Word cloud
        st.markdown("### ☁️ Word Cloud")
        wordcloud_b64 = visualizer.create_wordcloud(df, 'all')
        if wordcloud_b64:
            st.markdown(
                f'<div style="text-align: center; background: white; padding: 1rem; border-radius: 10px;"><img src="data:image/png;base64,{wordcloud_b64}" style="max-width:100%;"></div>',
                unsafe_allow_html=True
            )
    
    # IMPROVED Export Section
    st.markdown("---")
    st.markdown("""
    <div style="background: #f8f9fa; padding: 2rem; border-radius: 15px; border: 2px solid #dee2e6; margin: 2rem 0;">
        <h2 style="color: #007bff; text-align: center; margin-bottom: 2rem;">💾 Export & Download</h2>
    """, unsafe_allow_html=True)
    
    # Export buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 📄 Data Export")
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="📊 Download CSV Data",
            data=csv_data,
            file_name=f"{brand.lower()}_sentiment_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True,
            type="primary"
        )
    
    with col2:
        st.markdown("#### 📋 Summary Report")
        summary_json = json.dumps(summary_stats, indent=2, default=str)
        st.download_button(
            label="📋 Download Summary",
            data=summary_json,
            file_name=f"{brand.lower()}_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
    
    with col3:
        st.markdown("#### 🔄 Actions")
        if st.button("🆕 New Analysis", use_container_width=True, type="primary"):
            st.session_state.analysis_data = None
            st.session_state.summary_stats = None
            st.rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Top posts
    st.markdown("## 🏆 Top Posts")
    top_posts = visualizer.create_top_posts_table(df, 'all', top_n=5)
    if not top_posts.empty:
        st.dataframe(top_posts, use_container_width=True, hide_index=True)

if __name__ == "__main__":
    main()
