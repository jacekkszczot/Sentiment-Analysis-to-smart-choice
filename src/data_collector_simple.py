import requests
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import json

class DataCollector:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def collect_sample_data(self, brand: str) -> List[Dict]:
        """Generate sample data for testing"""
        sample_posts = [
            {
                'id': 'sample_1',
                'title': f'{brand} is revolutionizing the industry!',
                'text': f'I absolutely love my new {brand} product. The quality is amazing and customer service is excellent.',
                'score': 145,
                'num_comments': 23,
                'created_utc': datetime.now() - timedelta(hours=2),
                'subreddit': 'technology',
                'url': 'https://example.com/1',
                'source': 'reddit_sample',
                'keyword': brand.lower()
            },
            {
                'id': 'sample_2',
                'title': f'Disappointed with {brand}',
                'text': f'My experience with {brand} has been terrible. Poor quality and awful customer support.',
                'score': -12,
                'num_comments': 8,
                'created_utc': datetime.now() - timedelta(hours=5),
                'subreddit': 'reviews',
                'url': 'https://example.com/2',
                'source': 'reddit_sample',
                'keyword': brand.lower()
            },
            {
                'id': 'sample_3',
                'title': f'{brand} announces new features',
                'text': f'{brand} just released some interesting updates. Mixed feelings about the new direction.',
                'score': 67,
                'num_comments': 15,
                'created_utc': datetime.now() - timedelta(hours=8),
                'subreddit': 'news',
                'url': 'https://example.com/3',
                'source': 'reddit_sample',
                'keyword': brand.lower()
            }
        ]
        return sample_posts
    
    def save_data(self, data: List[Dict], filename: str) -> str:
        """Save collected data to JSON file"""
        filepath = self.config.RAW_DATA_DIR / f"{filename}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
        return str(filepath)
