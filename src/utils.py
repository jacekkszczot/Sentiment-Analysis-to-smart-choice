import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re

def validate_brand_input(brand: str) -> bool:
    """Validate brand name input"""
    if not brand or not brand.strip():
        return False
    if len(brand.strip()) < 2:
        return False
    # Allow letters, numbers, spaces, apostrophes, hyphens
    if not re.match(r"^[a-zA-Z0-9\s'\-&.]+$", brand.strip()):
        return False
    return True

def load_sample_brands() -> List[str]:
    """Load sample brands for dropdown"""
    from config import config
    return config.SAMPLE_BRANDS

def calculate_sentiment_trend(df: pd.DataFrame) -> str:
    """Calculate sentiment trend over time"""
    if 'created_utc' not in df.columns or len(df) < 5:
        return 'stable'
    
    try:
        # Convert sentiment to numeric
        sentiment_map = {'positive': 1, 'neutral': 0, 'negative': -1}
        df['sentiment_numeric'] = df['final_sentiment'].map(sentiment_map)
        
        # Sort by date
        df_sorted = df.sort_values('created_utc')
        
        # Calculate trend using simple linear regression
        x = np.arange(len(df_sorted))
        y = df_sorted['sentiment_numeric'].values
        
        # Remove NaN values
        mask = ~np.isnan(y)
        if mask.sum() < 3:
            return 'stable'
        
        x_clean = x[mask]
        y_clean = y[mask]
        
        # Linear regression
        slope = np.polyfit(x_clean, y_clean, 1)[0]
        
        if slope > 0.05:
            return 'improving'
        elif slope < -0.05:
            return 'declining'
        else:
            return 'stable'
            
    except Exception as e:
        print(f"Error calculating trend: {e}")
        return 'stable'

def get_trend_emoji(trend: str) -> str:
    """Get emoji for trend"""
    trend_emojis = {
        'improving': '📈',
        'declining': '📉', 
        'stable': '➡️'
    }
    return trend_emojis.get(trend, '➡️')

def format_number(num: int) -> str:
    """Format large numbers with K, M suffixes"""
    if num >= 1_000_000:
        return f"{num/1_000_000:.1f}M"
    elif num >= 1_000:
        return f"{num/1_000:.1f}K"
    else:
        return str(num)

def clean_brand_name(brand: str) -> str:
    """Clean brand name for file names"""
    if not brand:
        return "unknown"
    # Remove special characters, keep only alphanumeric and spaces
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', brand)
    # Replace spaces with underscores and convert to lowercase
    cleaned = re.sub(r'\s+', '_', cleaned.strip()).lower()
    return cleaned if cleaned else "unknown"

def get_confidence_category(confidence: float) -> str:
    """Categorize confidence level"""
    if confidence >= 0.8:
        return "Very High"
    elif confidence >= 0.6:
        return "High"
    elif confidence >= 0.4:
        return "Medium"
    elif confidence >= 0.2:
        return "Low"
    else:
        return "Very Low"

def create_date_range_text(start_date, end_date) -> str:
    """Create readable date range text"""
    if not start_date or not end_date:
        return "Date range unavailable"
    
    try:
        start = pd.to_datetime(start_date)
        end = pd.to_datetime(end_date)
        
        if start.date() == end.date():
            return f"Data from {start.strftime('%B %d, %Y')}"
        else:
            return f"Data from {start.strftime('%B %d')} to {end.strftime('%B %d, %Y')}"
    except:
        return "Date range unavailable"

def export_to_json_summary(df: pd.DataFrame, summary_stats: Dict, brand: str) -> Dict:
    """Create JSON summary for quick sharing"""
    
    try:
        positive_pct = (df['final_sentiment'] == 'positive').mean() * 100
        negative_pct = (df['final_sentiment'] == 'negative').mean() * 100
        neutral_pct = (df['final_sentiment'] == 'neutral').mean() * 100
        
        summary = {
            "brand": brand,
            "analysis_date": datetime.now().isoformat(),
            "total_posts": len(df),
            "sentiment_breakdown": {
                "positive_percentage": round(positive_pct, 1),
                "negative_percentage": round(negative_pct, 1),
                "neutral_percentage": round(neutral_pct, 1)
            },
            "key_metrics": {
                "average_confidence": round(df['final_confidence'].mean(), 3),
                "trend": calculate_sentiment_trend(df),
                "data_quality": get_confidence_category(df['final_confidence'].mean())
            },
            "top_positive_examples": [],
            "top_negative_examples": [],
            "summary_insight": f"{brand} shows {positive_pct:.1f}% positive sentiment with {get_confidence_category(df['final_confidence'].mean()).lower()} confidence analysis."
        }
        
        # Add top examples
        if 'final_sentiment' in df.columns:
            positive_posts = df[df['final_sentiment'] == 'positive'].nlargest(3, 'final_confidence')
            negative_posts = df[df['final_sentiment'] == 'negative'].nlargest(3, 'final_confidence')
            
            for _, post in positive_posts.iterrows():
                summary["top_positive_examples"].append({
                    "text": post['original_text'][:200] + "..." if len(post['original_text']) > 200 else post['original_text'],
                    "confidence": round(post['final_confidence'], 3)
                })
            
            for _, post in negative_posts.iterrows():
                summary["top_negative_examples"].append({
                    "text": post['original_text'][:200] + "..." if len(post['original_text']) > 200 else post['original_text'],
                    "confidence": round(post['final_confidence'], 3)
                })
        
        return summary
        
    except Exception as e:
        print(f"Error creating JSON summary: {e}")
        return {"error": f"Failed to create summary: {str(e)}"}
