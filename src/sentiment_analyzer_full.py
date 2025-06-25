import pandas as pd
import numpy as np
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import re
from typing import List, Dict, Tuple
import nltk
from collections import Counter

class SentimentAnalyzer:
    def __init__(self, config):
        self.config = config
        self.vader_analyzer = SentimentIntensityAnalyzer()
        self.download_nltk_data()
    
    def download_nltk_data(self):
        """Download required NLTK data"""
        try:
            import ssl
            try:
                _create_unverified_https_context = ssl._create_unverified_context
            except AttributeError:
                pass
            else:
                ssl._create_default_https_context = _create_unverified_https_context
            
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
        except:
            pass
    
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
    
    def vader_sentiment(self, text: str) -> Dict:
        """Analyze sentiment using VADER"""
        try:
            scores = self.vader_analyzer.polarity_scores(text)
            
            # Determine sentiment based on compound score
            compound = scores['compound']
            if compound >= 0.05:
                sentiment = 'positive'
            elif compound <= -0.05:
                sentiment = 'negative'
            else:
                sentiment = 'neutral'
            
            return {
                'sentiment': sentiment,
                'compound': compound,
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'confidence': abs(compound)
            }
        except:
            return {
                'sentiment': 'neutral',
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'confidence': 0.0
            }
    
    def analyze_batch(self, data: List[Dict]) -> pd.DataFrame:
        """Analyze sentiment for a batch of posts"""
        results = []
        
        for item in data:
            # Combine title and text
            combined_text = f"{item.get('title', '')} {item.get('text', '')}"
            cleaned_text = self.clean_text(combined_text)
            
            if len(cleaned_text) < self.config.MIN_TEXT_LENGTH:
                continue
            
            # TextBlob analysis
            textblob_result = self.textblob_sentiment(cleaned_text)
            
            # VADER analysis
            vader_result = self.vader_sentiment(cleaned_text)
            
            # Create ensemble sentiment
            ensemble_sentiment = self.ensemble_sentiment(
                textblob_result['sentiment'],
                vader_result['sentiment'],
                textblob_result['confidence'],
                vader_result['confidence']
            )
            
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
                
                # VADER results
                'vader_sentiment': vader_result['sentiment'],
                'vader_compound': vader_result['compound'],
                'vader_positive': vader_result['positive'],
                'vader_negative': vader_result['negative'],
                'vader_neutral': vader_result['neutral'],
                
                # Ensemble result
                'final_sentiment': ensemble_sentiment['sentiment'],
                'final_confidence': ensemble_sentiment['confidence'],
                
                # Metadata
                'score': item.get('score', 0),
                'num_comments': item.get('num_comments', 0),
                'url': item.get('url', ''),
                'subreddit': item.get('subreddit', '')
            }
            
            results.append(result)
        
        return pd.DataFrame(results)
    
    def ensemble_sentiment(self, textblob_sent: str, vader_sent: str, 
                         textblob_conf: float, vader_conf: float) -> Dict:
        """Combine TextBlob and VADER results"""
        
        # Weight the predictions by confidence
        if textblob_conf > vader_conf:
            primary_sentiment = textblob_sent
            confidence = (textblob_conf + vader_conf) / 2
        elif vader_conf > textblob_conf:
            primary_sentiment = vader_sent
            confidence = (textblob_conf + vader_conf) / 2
        else:
            # If equal confidence, check agreement
            if textblob_sent == vader_sent:
                primary_sentiment = textblob_sent
                confidence = (textblob_conf + vader_conf) / 2
            else:
                primary_sentiment = 'neutral'
                confidence = 0.5
        
        return {
            'sentiment': primary_sentiment,
            'confidence': confidence
        }
    
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
