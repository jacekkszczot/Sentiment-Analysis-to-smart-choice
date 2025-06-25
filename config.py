from pathlib import Path
import os

class Config:
    # Project paths
    PROJECT_ROOT = Path(__file__).parent
    SRC_DIR = PROJECT_ROOT / "src"
    DATA_DIR = PROJECT_ROOT / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PROCESSED_DATA_DIR = DATA_DIR / "processed"
    RESULTS_DIR = PROJECT_ROOT / "results"
    
    # Create directories if they don't exist
    for dir_path in [DATA_DIR, RAW_DATA_DIR, PROCESSED_DATA_DIR, RESULTS_DIR]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Analysis settings
    MIN_TEXT_LENGTH = 10
    MAX_ARTICLES_DEFAULT = 50
    CONFIDENCE_THRESHOLD = 0.0
    
    # Chart colors and themes
    DEFAULT_COLORS = {
        'positive': '#28a745',
        'negative': '#dc3545', 
        'neutral': '#6c757d'
    }
    
    CHART_THEME = 'plotly_white'
    
    # Sample brands for dropdown
    SAMPLE_BRANDS = [
        "Tesla", "Apple", "McDonald's", "Starbucks", "Nike", 
        "Coca-Cola", "Amazon", "Google", "Microsoft", "Netflix",
        "Disney", "Spotify", "Uber", "Airbnb", "Volkswagen",
        "BMW", "Mercedes", "Toyota", "Samsung", "Sony"
    ]

# Global config instance
config = Config()
