import requests
import praw
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
        self.reddit = None
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
    
    def setup_reddit(self, client_id: str, client_secret: str, user_agent: str):
        """Setup Reddit API connection"""
        try:
            self.reddit = praw.Reddit(
                client_id=client_id,
                client_secret=client_secret,
                user_agent=user_agent
            )
            return True
        except Exception as e:
            print(f"Reddit setup failed: {e}")
            return False
    
    def collect_reddit_posts(self, subreddits: List[str], keywords: List[str], 
                           limit: int = 100) -> List[Dict]:
        """Collect posts from Reddit"""
        posts = []
        
        if not self.reddit:
            print("Reddit not configured, skipping...")
            return posts
        
        for subreddit_name in subreddits:
            try:
                subreddit = self.reddit.subreddit(subreddit_name)
                
                # Search for keyword mentions
                for keyword in keywords:
                    search_results = subreddit.search(keyword, limit=limit//len(keywords))
                    
                    for post in search_results:
                        posts.append({
                            'id': post.id,
                            'title': post.title,
                            'text': post.selftext,
                            'score': post.score,
                            'num_comments': post.num_comments,
                            'created_utc': datetime.fromtimestamp(post.created_utc),
                            'subreddit': subreddit_name,
                            'url': post.url,
                            'source': 'reddit',
                            'keyword': keyword
                        })
                        
                time.sleep(0.1)  # Rate limiting
                
            except Exception as e:
                print(f"Error collecting from r/{subreddit_name}: {e}")
                continue
        
        return posts
    
    def collect_news_articles(self, brand: str, days_back: int = 7) -> List[Dict]:
        """Collect news articles using web scraping"""
        articles = []
        
        # Google News search (simple scraping)
        try:
            search_url = f"https://news.google.com/rss/search?q={brand}&hl=en-US&gl=US&ceid=US:en"
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'xml')
                items = soup.find_all('item')[:20]  # Limit to 20 articles
                
                for item in items:
                    title = item.find('title').text if item.find('title') else ""
                    description = item.find('description').text if item.find('description') else ""
                    pub_date = item.find('pubDate').text if item.find('pubDate') else ""
                    link = item.find('link').text if item.find('link') else ""
                    
                    articles.append({
                        'id': hash(title + link),
                        'title': title,
                        'text': description,
                        'published_date': pub_date,
                        'url': link,
                        'source': 'google_news',
                        'keyword': brand
                    })
                    
        except Exception as e:
            print(f"Error collecting news articles: {e}")
        
        return articles
    
    def collect_sample_data(self, brand: str) -> List[Dict]:
        """Generate sample data for testing without API keys"""
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
            },
            {
                'id': 'sample_4',
                'title': f'Great innovation from {brand}',
                'text': f'The latest {brand} product showcases incredible innovation. Impressed with the technology.',
                'score': 203,
                'num_comments': 45,
                'created_utc': datetime.now() - timedelta(hours=12),
                'subreddit': 'technology',
                'url': 'https://example.com/4',
                'source': 'reddit_sample',
                'keyword': brand.lower()
            },
            {
                'id': 'sample_5',
                'title': f'{brand} stock discussion',
                'text': f'What do you think about {brand} stock performance? Seems overvalued to me.',
                'score': 34,
                'num_comments': 67,
                'created_utc': datetime.now() - timedelta(hours=18),
                'subreddit': 'investing',
                'url': 'https://example.com/5',
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
        
        print(f"Data saved to {filepath}")
        return str(filepath)
    
    def load_data(self, filename: str) -> List[Dict]:
        """Load data from JSON file"""
        filepath = self.config.RAW_DATA_DIR / f"{filename}.json"
        
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return []
