#!/usr/bin/env python3
"""
Show stored data archive - View Reddit, news, market data, and sentiment trends
"""
from data.data_storage import DataStorage
from utils.logger import get_logger
import pandas as pd

log = get_logger("data_viewer")

def main():
    storage = DataStorage()
    
    print("=" * 80)
    print("📦 DATA ARCHIVE VIEWER")
    print("=" * 80)
    print()
    
    # Storage stats
    stats = storage.get_storage_stats()
    print("📊 STORAGE STATISTICS:")
    print(f"  • Market Data Entries: {stats['market_data_entries']}")
    print(f"  • News Entries: {stats['news_entries']}")
    print(f"  • Reddit Entries: {stats['reddit_entries']}")
    print(f"  • Sentiment Entries: {stats['sentiment_entries']}")
    print(f"  • Additional Sources Entries: {stats['additional_sources_entries']}")
    print(f"  • Total Storage: {stats['total_storage_mb']} MB")
    print()
    
    # Recent news
    print("=" * 80)
    print("📰 RECENT NEWS (Last 7 Days)")
    print("=" * 80)
    recent_news = storage.get_recent_news(days=7)
    for entry in recent_news[-5:]:  # Last 5 entries
        print(f"\n📅 {entry['date']} - {entry['count']} articles")
        print(f"   Average Sentiment: {entry['avg_sentiment']:.3f}")
        if entry['articles']:
            print(f"   Latest headlines:")
            for article in entry['articles'][:3]:
                sentiment = article.get('sentiment', {})
                compound = sentiment.get('compound', 0) if isinstance(sentiment, dict) else sentiment
                print(f"     • {article.get('title', 'No title')} (sentiment: {compound:.2f})")
    
    # Recent Reddit
    print()
    print("=" * 80)
    print("🤖 RECENT REDDIT (Last 7 Days)")
    print("=" * 80)
    recent_reddit = storage.get_recent_reddit(days=7)
    for entry in recent_reddit[-5:]:  # Last 5 entries
        print(f"\n📅 {entry['date']} - {entry['count']} posts")
        print(f"   Subreddits: {', '.join(entry['subreddits'])}")
        print(f"   Average Sentiment: {entry['avg_sentiment']:.3f}")
        if entry['posts']:
            print(f"   Top posts:")
            for post in entry['posts'][:3]:
                sentiment = post.get('sentiment', {})
                compound = sentiment.get('compound', 0) if isinstance(sentiment, dict) else sentiment
                print(f"     • r/{post.get('subreddit', 'unknown')}: {post.get('title', 'No title')[:60]}... ({compound:.2f})")
    
    # Sentiment trends
    print()
    print("=" * 80)
    print("📈 SENTIMENT TRENDS (Last 7 Days)")
    print("=" * 80)
    trends = storage.get_sentiment_trends(days=7)
    if not trends.empty:
        print(trends[['date', 'overall_sentiment', 'news_sentiment', 'reddit_sentiment', 'num_signals']].to_string(index=False))
    else:
        print("No sentiment data available yet")
    
    # Additional Sources
    print()
    print("=" * 80)
    print("🌐 ADDITIONAL SOURCES (Last 7 Days)")
    print("=" * 80)
    additional = storage.get_recent_additional_sources(days=7)
    for entry in additional[-3:]:  # Last 3 entries
        print(f"\n📅 {entry['date']} - Total Items: {entry['total_count']}")
        print(f"   Sources breakdown:")
        for source, count in entry.get('source_counts', {}).items():
            if count > 0:
                print(f"     • {source}: {count} items")
        
        # Show sample headlines
        if entry.get('sources', {}).get('yahoo_finance'):
            yahoo_articles = entry['sources']['yahoo_finance'][:2]
            if yahoo_articles:
                print(f"   Sample Yahoo Finance headlines:")
                for article in yahoo_articles:
                    print(f"     • [{article.get('ticker', '??')}] {article.get('title', '')[:60]}...")
    
    # Market data
    print()
    print("=" * 80)
    print("📊 RECENT MARKET DATA (Last 7 Days)")
    print("=" * 80)
    market_data = storage.get_recent_market_data(days=7)
    for entry in market_data[-5:]:  # Last 5 entries
        print(f"\n📅 {entry['date']} - Source: {entry['source']}")
        print(f"   Tickers: {', '.join(entry['tickers'])}")
        print(f"   Data Points: {entry['num_bars']}")
        if entry.get('latest_prices'):
            print(f"   Latest Prices:")
            for ticker, price in entry['latest_prices'].items():
                if price is not None:
                    print(f"     • {ticker}: ${price:.2f}")
    
    print()
    print("=" * 80)
    print("✅ Data archive viewing complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()

