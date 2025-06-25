import pandas as pd
import numpy as np
from textblob import TextBlob
import re
from typing import List, Dict, Tuple
from collections import Counter

class SentimentAnalyzer:
    def __init__(self, config):
        self.config = config
    
    def clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        if not text or pd.isna(text):
            return ""
        
        # Remove URLs
        text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
        # Remove user mentions and hashtags
        text = re.sub(r'@\w+|#\w+', '', text)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def textblob_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using TextBlob"""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            subjectivity = blob.sentiment.subjectivity
            
            # Convert polarity to category
            if polarity > 0.1:
                sentiment = 'positive'
            elif polarity < -0.1:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'polarity': polarity,
                'subjectivity': subjectivity,
                'confidence': abs(polarity)
            }
        except:
            return {
                'sentiment': 'neutral',
                'polarity': 0.0,
                'subjectivity': 0.0,
                'confidence': 0.0
            }
    
    def analyze_batch(self, data: List[Dict]) -> pd.DataFrame:
        """Analyze sentiment for a batch of posts"""
        results = []
        
        for item in data:
            # Combine title and text
            combined_text = f"{item.get('title', '')} {item.get('text', '')}"
            cleaned_text = self.clean_text(combined_text)
            
            if len(cleaned_text) < 10:  # MIN_TEXT_LENGTH
                continue
            
            # TextBlob analysis
            textblob_result = self.textblob_sentiment(cleaned_text)
            
            result = {
                'id': item.get('id'),
                'original_text': combined_text,
                'cleaned_text': cleaned_text,
                'source': item.get('source'),
                'keyword': item.get('keyword'),
                'created_utc': item.get('created_utc'),
                
                # TextBlob results
                'textblob_sentiment': textblob_result['sentiment'],
                'textblob_polarity': textblob_result['polarity'],
                'textblob_subjectivity': textblob_result['subjectivity'],
                
                # Final results (just TextBlob for now)
                'final_sentiment': textblob_result['sentiment'],
                'final_confidence': textblob_result['confidence'],
                
                # Metadata
                'score': item.get('score', 0),
                'num_comments': item.get('num_comments', 0),
                'url': item.get('url', ''),
                'subreddit': item.get('subreddit', '')
            }
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def get_summary_stats(self, df: pd.DataFrame) -> Dict:
        """Generate summary statistics"""
        if df.empty:
            return {}
        
        sentiment_counts = df['final_sentiment'].value_counts()
        total_posts = len(df)
        
        summary = {
            'total_posts': total_posts,
            'sentiment_distribution': {
                'positive': sentiment_counts.get('positive', 0),
                'negative': sentiment_counts.get('negative', 0),
                'neutral': sentiment_counts.get('neutral', 0)
            },
            'sentiment_percentages': {
                'positive': round(sentiment_counts.get('positive', 0) / total_posts * 100, 2),
                'negative': round(sentiment_counts.get('negative', 0) / total_posts * 100, 2),
                'neutral': round(sentiment_counts.get('neutral', 0) / total_posts * 100, 2)
            },
            'average_confidence': round(df['final_confidence'].mean(), 3),
            'top_sources': df['source'].value_counts().head(5).to_dict(),
            'date_range': {
                'start': df['created_utc'].min() if 'created_utc' in df.columns else None,
                'end': df['created_utc'].max() if 'created_utc' in df.columns else None
            }
        }
        
        return summary
