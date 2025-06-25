import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
RESULTS_DIR = BASE_DIR / "results"
SRC_DIR = BASE_DIR / "src"

# Create directories if they don't exist
for dir_path in [RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR]:
    dir_path.mkdir(parents=True, exist_ok=True)

# API Keys (will be loaded from environment variables)
REDDIT_CLIENT_ID = os.getenv("REDDIT_CLIENT_ID", "")
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET", "")
REDDIT_USER_AGENT = os.getenv("REDDIT_USER_AGENT", "SentimentMonitor/1.0")

# Default settings
DEFAULT_BRAND = "tesla"
DEFAULT_SUBREDDITS = ["technology", "cars", "electricvehicles", "stocks"]
DEFAULT_KEYWORDS = ["tesla", "model 3", "model y", "elon musk", "tsla"]

# Sentiment analysis settings
SENTIMENT_MODELS = ["textblob", "vader", "custom"]
MIN_TEXT_LENGTH = 10
MAX_POSTS_PER_SOURCE = 100

# Visualization settings
CHART_THEME = "plotly_dark"
DEFAULT_COLORS = {
    "positive": "#2E8B57",
    "negative": "#DC143C", 
    "neutral": "#4682B4"
}
