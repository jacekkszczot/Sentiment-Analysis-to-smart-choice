import pandas as pd
import json
from pathlib import Path
from datetime import datetime
import streamlit as st
from typing import Dict, List, Any
import os
import numpy as np  # DODANE!
import base64

def save_analysis_results(df: pd.DataFrame, summary_stats: Dict, filename: str, config) -> str:
    """Save analysis results to files"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save CSV
    csv_path = config.RESULTS_DIR / f"{filename}_{timestamp}.csv"
    df.to_csv(csv_path, index=False)
    
    # Save summary JSON
    json_path = config.RESULTS_DIR / f"{filename}_summary_{timestamp}.json"
    with open(json_path, 'w') as f:
        json.dump(summary_stats, f, indent=2, default=str)
    
    return f"Results saved to {csv_path} and {json_path}"

def load_sample_brands() -> List[str]:
    """Return list of sample brands for testing"""
    return [
        "Tesla", "Apple", "Microsoft", "Google", "Amazon", 
        "Netflix", "Spotify", "Nike", "Adidas", "McDonald's",
        "Starbucks", "Coca-Cola", "Pepsi", "Samsung", "Sony"
    ]

def format_large_number(num: int) -> str:
    """Format large numbers with K, M suffixes"""
    if num >= 1_000_000:
        return f"{num / 1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num / 1_000:.1f}K"
    else:
        return str(num)

def validate_brand_input(brand: str) -> bool:
    """Validate brand name input"""
    if not brand or len(brand.strip()) < 2:
        return False
    
    # Check for special characters that might break searches
    invalid_chars = ['<', '>', '"', "'", '&', '?', '%']
    if any(char in brand for char in invalid_chars):
        return False
    
    return True

def get_color_for_sentiment(sentiment: str) -> str:
    """Get color code for sentiment"""
    colors = {
        'positive': '#2E8B57',
        'negative': '#DC143C',
        'neutral': '#4682B4'
    }
    return colors.get(sentiment, '#808080')

def create_download_link(df: pd.DataFrame, filename: str = "sentiment_analysis") -> str:
    """Create download link for DataFrame"""
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}.csv">Download CSV</a>'
    return href

def check_api_keys() -> Dict[str, bool]:
    """Check if API keys are configured"""
    return {
        'reddit': bool(os.getenv('REDDIT_CLIENT_ID') and os.getenv('REDDIT_CLIENT_SECRET')),
        'twitter': bool(os.getenv('TWITTER_API_KEY')),  # For future implementation
    }

def display_api_setup_instructions():
    """Display instructions for setting up API keys"""
    st.info("""
    **🔑 API Setup Instructions:**
    
    For full functionality, you can set up API access:
    
    **Reddit API (Optional):**
    1. Go to https://www.reddit.com/prefs/apps
    2. Create a new app (script type)
    3. Set environment variables:
       - REDDIT_CLIENT_ID
       - REDDIT_CLIENT_SECRET
       - REDDIT_USER_AGENT
    
    **Note:** The app works with sample data even without API keys!
    """)

@st.cache_data
def load_cached_data(brand: str, use_sample: bool = True) -> pd.DataFrame:
    """Load and cache data for performance"""
    # This would implement caching logic
    # For now, return empty DataFrame
    return pd.DataFrame()

def format_datetime(dt) -> str:
    """Format datetime for display"""
    if pd.isna(dt):
        return "N/A"
    
    if isinstance(dt, str):
        try:
            dt = pd.to_datetime(dt)
        except:
            return dt
    
    return dt.strftime("%Y-%m-%d %H:%M")

def calculate_sentiment_trend(df: pd.DataFrame) -> str:
    """Calculate if sentiment is trending up or down"""
    if 'created_utc' not in df.columns or len(df) < 2:
        return "insufficient_data"
    
    # Sort by date
    df_sorted = df.sort_values('created_utc')
    
    # Calculate sentiment score (positive=1, neutral=0, negative=-1)
    sentiment_scores = df_sorted['final_sentiment'].map({
        'positive': 1,
        'neutral': 0,
        'negative': -1
    })
    
    # Calculate trend using linear regression slope
    x = range(len(sentiment_scores))
    slope = np.polyfit(x, sentiment_scores, 1)[0]
    
    if slope > 0.01:
        return "improving"
    elif slope < -0.01:
        return "declining"
    else:
        return "stable"

def get_trend_emoji(trend: str) -> str:
    """Get emoji for trend direction"""
    trend_emojis = {
        "improving": "📈",
        "declining": "📉", 
        "stable": "➡️",
        "insufficient_data": "❓"
    }
    return trend_emojis.get(trend, "❓")
