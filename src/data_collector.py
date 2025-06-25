import requests
import time
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
from bs4 import BeautifulSoup
import json
import random
import xml.etree.ElementTree as ET
from urllib.parse import quote

class DataCollector:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def collect_live_news(self, brand: str, days_back: int = 7) -> List[Dict]:
        """Collect LIVE news articles about any brand from Google News"""
        articles = []
        
        try:
            # Google News RSS search for the brand
            search_query = quote(f'"{brand}" OR {brand}')
            search_url = f"https://news.google.com/rss/search?q={search_query}&hl=en-US&gl=US&ceid=US:en"
            
            print(f"🔍 Searching Google News for: {brand}")
            
            response = self.session.get(search_url, timeout=15)
            
            if response.status_code == 200:
                # Parse RSS XML
                root = ET.fromstring(response.content)
                
                # Find all news items
                items = root.findall('.//item')[:25]  # Limit to 25 articles
                
                print(f"📰 Found {len(items)} news articles about {brand}")
                
                for idx, item in enumerate(items):
                    try:
                        title_elem = item.find('title')
                        desc_elem = item.find('description')
                        link_elem = item.find('link')
                        pub_date_elem = item.find('pubDate')
                        
                        title = title_elem.text if title_elem is not None else ""
                        description = desc_elem.text if desc_elem is not None else ""
                        link = link_elem.text if link_elem is not None else ""
                        pub_date_str = pub_date_elem.text if pub_date_elem is not None else ""
                        
                        # Parse publication date
                        try:
                            pub_date = pd.to_datetime(pub_date_str)
                        except:
                            pub_date = datetime.now() - timedelta(hours=random.randint(1, 168))
                        
                        # Clean description (remove HTML tags)
                        if description:
                            description = re.sub(r'<[^>]+>', '', description)
                            description = re.sub(r'&[^;]+;', ' ', description)
                        
                        # Skip if too old
                        if pub_date < datetime.now() - timedelta(days=days_back):
                            continue
                        
                        # Create article entry
                        articles.append({
                            'id': f'news_{brand.lower()}_{idx+1}',
                            'title': title,
                            'text': description[:500] if description else title,  # Use title if no description
                            'score': random.randint(10, 150),  # Simulate engagement
                            'num_comments': random.randint(0, 50),
                            'created_utc': pub_date,
                            'subreddit': 'google_news',
                            'url': link,
                            'source': 'google_news_live',
                            'keyword': brand.lower()
                        })
                        
                    except Exception as e:
                        print(f"Error parsing article {idx}: {e}")
                        continue
                
            else:
                print(f"❌ Failed to fetch news: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error collecting news for {brand}: {e}")
        
        print(f"✅ Collected {len(articles)} articles for {brand}")
        return articles
    
    def collect_sample_data(self, brand: str) -> List[Dict]:
        """Backup sample data if live news fails"""
        sample_posts = [
            {
                'id': f'sample_{brand.lower()}_1',
                'title': f'{brand} continues to innovate in the market',
                'text': f'Recent developments from {brand} show promising growth and customer satisfaction.',
                'score': random.randint(50, 200),
                'num_comments': random.randint(10, 50),
                'created_utc': datetime.now() - timedelta(hours=random.randint(1, 48)),
                'subreddit': 'sample_data',
                'url': f'https://example.com/{brand.lower()}',
                'source': 'sample_backup',
                'keyword': brand.lower()
            },
            {
                'id': f'sample_{brand.lower()}_2',
                'title': f'Mixed reviews for {brand} latest announcement',
                'text': f'Customers have varied opinions about {brand} recent updates and changes.',
                'score': random.randint(-20, 80),
                'num_comments': random.randint(5, 30),
                'created_utc': datetime.now() - timedelta(hours=random.randint(2, 72)),
                'subreddit': 'sample_data',
                'url': f'https://example.com/{brand.lower()}_2',
                'source': 'sample_backup',
                'keyword': brand.lower()
            }
        ]
        return sample_posts
    
    def load_custom_csv(self, filepath: str) -> List[Dict]:
        """Load data from uploaded CSV file"""
        try:
            df = pd.read_csv(filepath)
            
            # Check required columns
            required_cols = ['title', 'text']
            missing_cols = [col for col in required_cols if col not in df.columns]
            
            if missing_cols:
                raise ValueError(f"Missing required columns: {missing_cols}")
            
            posts = []
            for idx, row in df.iterrows():
                # Handle different date formats
                created_date = datetime.now() - timedelta(hours=idx)
                if 'date' in df.columns and pd.notna(row['date']):
                    try:
                        created_date = pd.to_datetime(row['date'])
                    except:
                        pass
                
                posts.append({
                    'id': f'custom_{idx+1}',
                    'title': str(row['title']) if pd.notna(row['title']) else '',
                    'text': str(row['text']) if pd.notna(row['text']) else '',
                    'score': int(row.get('score', 0)) if pd.notna(row.get('score', 0)) else 0,
                    'num_comments': int(row.get('comments', 0)) if pd.notna(row.get('comments', 0)) else 0,
                    'created_utc': created_date,
                    'subreddit': str(row.get('source', 'custom')) if pd.notna(row.get('source', 'custom')) else 'custom',
                    'url': str(row.get('url', f'https://custom.com/{idx+1}')) if pd.notna(row.get('url', '')) else f'https://custom.com/{idx+1}',
                    'source': 'custom_upload',
                    'keyword': str(row.get('brand', 'unknown')) if pd.notna(row.get('brand', 'unknown')) else 'unknown'
                })
            
            return posts
            
        except Exception as e:
            print(f"Error loading CSV: {e}")
            return []
    
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
