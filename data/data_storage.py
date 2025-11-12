"""
Data Storage System - Persist all data sources for RAG learning
Stores market data, news, Reddit posts, and sentiment scores.
"""
import os
import json
import pandas as pd
from datetime import datetime
from typing import Dict, List
from utils.logger import get_logger

log = get_logger("data_storage")


class DataStorage:
    """
    Centralized storage for all trading data sources.
    Stores historical data for RAG learning and analysis.
    """
    
    def __init__(self, storage_dir: str = "storage/data_archive"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        # Data file paths
        self.market_data_file = os.path.join(storage_dir, "market_data_history.json")
        self.news_file = os.path.join(storage_dir, "news_history.json")
        self.reddit_file = os.path.join(storage_dir, "reddit_history.json")
        self.sentiment_file = os.path.join(storage_dir, "sentiment_history.json")
        self.additional_sources_file = os.path.join(storage_dir, "additional_sources_history.json")
        
    def store_market_data(self, prices: pd.DataFrame, tickers: List[str], source: str = "yfinance"):
        """
        Store fetched market data with metadata.
        
        Args:
            prices: DataFrame with price data
            tickers: List of tickers
            source: Data source (yfinance, alpaca, etc.)
        """
        if prices.empty:
            log.warning("No market data to store (empty DataFrame)")
            return
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'source': source,
            'tickers': tickers,
            'num_bars': len(prices),
            'data': prices.to_dict(),  # Store actual price data
            'latest_prices': {ticker: float(prices[ticker].iloc[-1]) if ticker in prices.columns else None 
                             for ticker in tickers}
        }
        
        history = self._load_json(self.market_data_file, [])
        history.append(record)
        
        # Keep only last 30 days to avoid huge files
        history = self._keep_recent(history, days=30)
        
        self._save_json(self.market_data_file, history)
        log.info(f"💾 Stored {len(prices)} market data bars from {source}")
    
    def store_news(self, news_items: List[Dict]):
        """
        Store news articles with sentiment scores.
        
        Args:
            news_items: List of news articles with metadata and sentiment
        """
        if not news_items:
            log.warning("No news data to store")
            return
        
        # Extract compound sentiment score
        def get_sentiment(item):
            sent = item.get('sentiment', {})
            if isinstance(sent, dict):
                return sent.get('compound', 0)
            return sent if isinstance(sent, (int, float)) else 0
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'count': len(news_items),
            'articles': news_items,
            'avg_sentiment': sum(get_sentiment(item) for item in news_items) / len(news_items) if news_items else 0
        }
        
        history = self._load_json(self.news_file, [])
        history.append(record)
        
        # Keep only last 30 days
        history = self._keep_recent(history, days=30)
        
        self._save_json(self.news_file, history)
        log.info(f"💾 Stored {len(news_items)} news articles (avg sentiment: {record['avg_sentiment']:.2f})")
    
    def store_reddit(self, reddit_posts: List[Dict]):
        """
        Store Reddit posts with sentiment scores.
        
        Args:
            reddit_posts: List of Reddit submissions with metadata and sentiment
        """
        if not reddit_posts:
            log.warning("No Reddit data to store")
            return
        
        # Extract compound sentiment score
        def get_sentiment(post):
            sent = post.get('sentiment', {})
            if isinstance(sent, dict):
                return sent.get('compound', 0)
            return sent if isinstance(sent, (int, float)) else 0
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'count': len(reddit_posts),
            'posts': reddit_posts,
            'subreddits': list(set(post.get('subreddit', '') for post in reddit_posts)),
            'avg_sentiment': sum(get_sentiment(post) for post in reddit_posts) / len(reddit_posts) if reddit_posts else 0
        }
        
        history = self._load_json(self.reddit_file, [])
        history.append(record)
        
        # Keep only last 30 days
        history = self._keep_recent(history, days=30)
        
        self._save_json(self.reddit_file, history)
        log.info(f"💾 Stored {len(reddit_posts)} Reddit posts from {len(record['subreddits'])} subreddits")
    
    def store_sentiment_summary(self, summary: Dict):
        """
        Store overall sentiment summary for the trading run.
        
        Args:
            summary: Dict with sentiment metrics (news, reddit, overall)
        """
        record = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            **summary
        }
        
        history = self._load_json(self.sentiment_file, [])
        history.append(record)
        
        # Keep only last 90 days
        history = self._keep_recent(history, days=90)
        
        self._save_json(self.sentiment_file, history)
        log.info(f"💾 Stored sentiment summary (overall: {summary.get('overall_sentiment', 0):.2f})")
    
    def get_recent_market_data(self, days: int = 7) -> List[Dict]:
        """Retrieve market data from last N days."""
        history = self._load_json(self.market_data_file, [])
        return self._keep_recent(history, days=days)
    
    def get_recent_news(self, days: int = 7) -> List[Dict]:
        """Retrieve news from last N days."""
        history = self._load_json(self.news_file, [])
        return self._keep_recent(history, days=days)
    
    def get_recent_reddit(self, days: int = 7) -> List[Dict]:
        """Retrieve Reddit posts from last N days."""
        history = self._load_json(self.reddit_file, [])
        return self._keep_recent(history, days=days)
    
    def get_sentiment_trends(self, days: int = 7) -> pd.DataFrame:
        """
        Get sentiment trends over time.
        
        Returns:
            DataFrame with date, news_sentiment, reddit_sentiment, overall_sentiment
        """
        history = self._load_json(self.sentiment_file, [])
        recent = self._keep_recent(history, days=days)
        
        if not recent:
            return pd.DataFrame()
        
        df = pd.DataFrame(recent)
        df['date'] = pd.to_datetime(df['date'])
        return df.sort_values('date')
    
    def store_additional_sources(self, sources_data: Dict):
        """
        Store data from additional sources (Yahoo Finance, Investing.com, etc.)
        
        Args:
            sources_data: Dict with data from each additional source
        """
        if not sources_data:
            log.warning("No additional sources data to store")
            return
        
        # Count total articles
        total_count = sum(len(data) for data in sources_data.values() if isinstance(data, list))
        
        record = {
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'total_count': total_count,
            'sources': sources_data,
            'source_counts': {
                source: len(data) if isinstance(data, list) else 0
                for source, data in sources_data.items()
            }
        }
        
        history = self._load_json(self.additional_sources_file, [])
        history.append(record)
        
        # Keep only last 30 days
        history = self._keep_recent(history, days=30)
        
        self._save_json(self.additional_sources_file, history)
        log.info(f"💾 Stored {total_count} items from {len(sources_data)} additional sources")
    
    def get_recent_additional_sources(self, days: int = 7) -> List[Dict]:
        """Retrieve additional sources data from last N days."""
        history = self._load_json(self.additional_sources_file, [])
        return self._keep_recent(history, days=days)
    
    def get_storage_stats(self) -> Dict:
        """Get statistics about stored data."""
        return {
            'market_data_entries': len(self._load_json(self.market_data_file, [])),
            'news_entries': len(self._load_json(self.news_file, [])),
            'reddit_entries': len(self._load_json(self.reddit_file, [])),
            'sentiment_entries': len(self._load_json(self.sentiment_file, [])),
            'additional_sources_entries': len(self._load_json(self.additional_sources_file, [])),
            'total_storage_mb': self._get_storage_size_mb()
        }
    
    def _keep_recent(self, items: List[Dict], days: int) -> List[Dict]:
        """Filter items to keep only recent N days."""
        if not items:
            return []
        
        from datetime import timedelta
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        return [item for item in items if item.get('timestamp', '') >= cutoff]
    
    def _load_json(self, filepath: str, default):
        """Load JSON file or return default."""
        if not os.path.exists(filepath):
            return default
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Failed to load {filepath}: {e}")
            return default
    
    def _save_json(self, filepath: str, data):
        """Save data to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log.error(f"Failed to save {filepath}: {e}")
    
    def _get_storage_size_mb(self) -> float:
        """Calculate total storage size in MB."""
        total_size = 0
        for file in [self.market_data_file, self.news_file, self.reddit_file, 
                     self.sentiment_file, self.additional_sources_file]:
            if os.path.exists(file):
                total_size += os.path.getsize(file)
        return round(total_size / (1024 * 1024), 2)

