"""
Additional free data sources for trading bot
Integrates: Yahoo Finance, Investing.com, MarketWatch, Finviz, Stock Analysis
"""
import requests
import feedparser
from typing import List, Dict
from datetime import datetime
from utils.logger import get_logger

log = get_logger("additional_sources")


def fetch_yahoo_finance_news(tickers: List[str]) -> List[Dict]:
    """
    Fetch news from Yahoo Finance RSS feeds for specific tickers.
    
    Args:
        tickers: List of stock symbols
    
    Returns:
        List of news articles
    """
    articles = []
    
    for ticker in tickers:
        try:
            # Yahoo Finance RSS feed for specific ticker
            url = f"https://finance.yahoo.com/rss/headline?s={ticker}"
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:5]:  # Top 5 per ticker
                articles.append({
                    'source': 'Yahoo Finance',
                    'ticker': ticker,
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'publishedAt': entry.get('published', ''),
                    'content': entry.get('summary', ''),
                })
                
            log.info(f"Fetched {len(feed.entries[:5])} articles from Yahoo Finance for {ticker}")
        except Exception as e:
            log.warning(f"Failed to fetch Yahoo Finance for {ticker}: {e}")
            continue
    
    return articles


def fetch_investing_com_news() -> List[Dict]:
    """
    Fetch latest news from Investing.com RSS feeds.
    
    Returns:
        List of news articles
    """
    articles = []
    
    # Investing.com RSS feeds
    feeds = [
        "https://www.investing.com/rss/news_285.rss",  # Stock market news
        "https://www.investing.com/rss/news_25.rss",   # Most popular
        "https://www.investing.com/rss/news_1.rss",    # Latest
    ]
    
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # Top 10 per feed
                articles.append({
                    'source': 'Investing.com',
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'publishedAt': entry.get('published', ''),
                    'content': entry.get('summary', ''),
                })
            
            log.info(f"Fetched {len(feed.entries[:10])} articles from Investing.com")
        except Exception as e:
            log.warning(f"Failed to fetch Investing.com feed {feed_url}: {e}")
            continue
    
    return articles


def fetch_marketwatch_news() -> List[Dict]:
    """
    Fetch latest news from MarketWatch RSS feeds.
    
    Returns:
        List of news articles
    """
    articles = []
    
    # MarketWatch RSS feeds
    feeds = [
        "https://www.marketwatch.com/rss/topstories",
        "https://www.marketwatch.com/rss/marketpulse",
    ]
    
    for feed_url in feeds:
        try:
            feed = feedparser.parse(feed_url)
            
            for entry in feed.entries[:10]:  # Top 10 per feed
                articles.append({
                    'source': 'MarketWatch',
                    'title': entry.get('title', ''),
                    'url': entry.get('link', ''),
                    'publishedAt': entry.get('published', ''),
                    'content': entry.get('summary', ''),
                })
            
            log.info(f"Fetched {len(feed.entries[:10])} articles from MarketWatch")
        except Exception as e:
            log.warning(f"Failed to fetch MarketWatch feed {feed_url}: {e}")
            continue
    
    return articles


def fetch_finviz_news(tickers: List[str]) -> List[Dict]:
    """
    Fetch news from Finviz for specific tickers.
    Uses web scraping since Finviz doesn't have an official API.
    
    Args:
        tickers: List of stock symbols
    
    Returns:
        List of news articles
    """
    articles = []
    
    for ticker in tickers:
        try:
            # Finviz news page for ticker
            url = f"https://finviz.com/quote.ashx?t={ticker}"
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                # Simple extraction - look for news table
                # This is basic - could be enhanced with BeautifulSoup
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.text, 'html.parser')
                
                news_table = soup.find('table', {'id': 'news-table'})
                if news_table:
                    rows = news_table.find_all('tr')[:5]  # Top 5 news items
                    
                    for row in rows:
                        link_tag = row.find('a')
                        if link_tag:
                            articles.append({
                                'source': 'Finviz',
                                'ticker': ticker,
                                'title': link_tag.get_text().strip(),
                                'url': link_tag.get('href', ''),
                                'publishedAt': datetime.now().isoformat(),
                                'content': '',
                            })
                
                log.info(f"Fetched articles from Finviz for {ticker}")
        except ImportError:
            log.warning("BeautifulSoup not installed. Install with: pip install beautifulsoup4")
            break
        except Exception as e:
            log.warning(f"Failed to fetch Finviz for {ticker}: {e}")
            continue
    
    return articles


def fetch_stock_analysis_data(tickers: List[str]) -> List[Dict]:
    """
    Fetch fundamental data from Stock Analysis (stockanalysis.com).
    Note: This requires web scraping as they don't have a public API.
    
    Args:
        tickers: List of stock symbols
    
    Returns:
        List of fundamental data points
    """
    data_points = []
    
    for ticker in tickers:
        try:
            # Stock Analysis doesn't have an API, but we can note the ticker for manual review
            # Or implement web scraping if needed
            data_points.append({
                'source': 'Stock Analysis',
                'ticker': ticker,
                'url': f'https://stockanalysis.com/stocks/{ticker.lower()}/',
                'note': 'Manual review recommended for fundamentals',
                'timestamp': datetime.now().isoformat()
            })
        except Exception as e:
            log.warning(f"Failed to process Stock Analysis for {ticker}: {e}")
            continue
    
    return data_points


def fetch_simply_wall_st_data(tickers: List[str]) -> List[Dict]:
    """
    Fetch data from Simply Wall St.
    Note: Requires account/API access for automated fetching.
    
    Args:
        tickers: List of stock symbols
    
    Returns:
        List of data points
    """
    # Simply Wall St requires authentication
    # This is a placeholder for future implementation
    log.info("Simply Wall St integration requires API key - placeholder for now")
    
    return [{
        'source': 'Simply Wall St',
        'note': 'Requires API key for automation',
        'url': 'https://simplywall.st/',
        'tickers': tickers
    }]


def fetch_all_additional_sources(tickers: List[str]) -> Dict[str, List[Dict]]:
    """
    Fetch data from all additional sources.
    
    Args:
        tickers: List of stock symbols to track
    
    Returns:
        Dict with data from each source
    """
    log.info("🌐 Fetching data from additional sources...")
    
    results = {
        'yahoo_finance': fetch_yahoo_finance_news(tickers),
        'investing_com': fetch_investing_com_news(),
        'marketwatch': fetch_marketwatch_news(),
        'finviz': fetch_finviz_news(tickers),
        'stock_analysis': fetch_stock_analysis_data(tickers),
        'simply_wall_st': fetch_simply_wall_st_data(tickers),
    }
    
    # Count total articles
    total_articles = sum(len(articles) for articles in results.values() if isinstance(articles, list))
    log.info(f"✅ Fetched {total_articles} total data points from additional sources")
    
    return results




