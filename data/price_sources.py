"""
Multiple Price Data Sources with Automatic Fallback
Tries multiple free APIs to ensure we always have price data
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Optional
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
log = get_logger("price_sources")


def fetch_prices_alpha_vantage(tickers: List[str]) -> pd.DataFrame:
    """
    Fetch prices from Alpha Vantage API.
    Free tier: 25 requests/day (5 API calls per minute)
    """
    api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not api_key:
        log.warning("Alpha Vantage API key not found")
        return pd.DataFrame()
    
    prices = {}
    
    for ticker in tickers[:5]:  # Limit to 5 tickers to stay within rate limits
        try:
            url = f"https://www.alphavantage.co/query"
            params = {
                'function': 'TIME_SERIES_INTRADAY',
                'symbol': ticker,
                'interval': '60min',
                'apikey': api_key,
                'outputsize': 'compact'  # Last 100 data points
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series (60min)' in data:
                time_series = data['Time Series (60min)']
                df_ticker = pd.DataFrame.from_dict(time_series, orient='index')
                df_ticker.index = pd.to_datetime(df_ticker.index)
                df_ticker = df_ticker.sort_index()
                prices[ticker] = df_ticker['4. close'].astype(float)
                log.info(f"✅ Alpha Vantage: Fetched {len(df_ticker)} bars for {ticker}")
            else:
                log.warning(f"Alpha Vantage: No data for {ticker}")
                
        except Exception as e:
            log.warning(f"Alpha Vantage failed for {ticker}: {e}")
            continue
    
    if prices:
        df = pd.DataFrame(prices)
        log.info(f"✅ Alpha Vantage: Total {len(df)} bars for {len(prices)} tickers")
        return df
    
    return pd.DataFrame()


def fetch_prices_twelve_data(tickers: List[str], days: int = 7) -> pd.DataFrame:
    """
    Fetch prices from Twelve Data API.
    Free tier: 800 requests/day
    """
    api_key = os.getenv("TWELVE_DATA_API_KEY")
    if not api_key:
        log.warning("Twelve Data API key not found")
        return pd.DataFrame()
    
    prices = {}
    
    for ticker in tickers:
        try:
            url = f"https://api.twelvedata.com/time_series"
            params = {
                'symbol': ticker,
                'interval': '1h',
                'outputsize': days * 24,  # Approximate hourly bars
                'apikey': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'values' in data and data['values']:
                df_ticker = pd.DataFrame(data['values'])
                df_ticker['datetime'] = pd.to_datetime(df_ticker['datetime'])
                df_ticker = df_ticker.set_index('datetime').sort_index()
                prices[ticker] = df_ticker['close'].astype(float)
                log.info(f"✅ Twelve Data: Fetched {len(df_ticker)} bars for {ticker}")
            else:
                log.warning(f"Twelve Data: No data for {ticker}")
                
        except Exception as e:
            log.warning(f"Twelve Data failed for {ticker}: {e}")
            continue
    
    if prices:
        df = pd.DataFrame(prices)
        log.info(f"✅ Twelve Data: Total {len(df)} bars for {len(prices)} tickers")
        return df
    
    return pd.DataFrame()


def fetch_prices_finnhub(tickers: List[str], days: int = 7) -> pd.DataFrame:
    """
    Fetch prices from Finnhub API.
    Free tier: 60 calls/minute
    """
    api_key = os.getenv("FINNHUB_API_KEY")
    if not api_key:
        log.warning("Finnhub API key not found")
        return pd.DataFrame()
    
    prices = {}
    end_time = int(datetime.now().timestamp())
    start_time = int((datetime.now() - timedelta(days=days)).timestamp())
    
    for ticker in tickers:
        try:
            url = f"https://finnhub.io/api/v1/stock/candle"
            params = {
                'symbol': ticker,
                'resolution': '60',  # 60 minutes
                'from': start_time,
                'to': end_time,
                'token': api_key
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data.get('s') == 'ok' and 'c' in data:
                timestamps = [datetime.fromtimestamp(t) for t in data['t']]
                df_ticker = pd.DataFrame({
                    'close': data['c']
                }, index=timestamps)
                prices[ticker] = df_ticker['close']
                log.info(f"✅ Finnhub: Fetched {len(df_ticker)} bars for {ticker}")
            else:
                log.warning(f"Finnhub: No data for {ticker}")
                
        except Exception as e:
            log.warning(f"Finnhub failed for {ticker}: {e}")
            continue
    
    if prices:
        df = pd.DataFrame(prices)
        log.info(f"✅ Finnhub: Total {len(df)} bars for {len(prices)} tickers")
        return df
    
    return pd.DataFrame()


def fetch_prices_iex_cloud(tickers: List[str]) -> pd.DataFrame:
    """
    Fetch prices from IEX Cloud API.
    Free tier: Limited (500K messages/month)
    """
    api_key = os.getenv("IEX_CLOUD_API_KEY")
    if not api_key:
        log.warning("IEX Cloud API key not found")
        return pd.DataFrame()
    
    prices = {}
    
    for ticker in tickers:
        try:
            # Use sandbox for testing: sandbox.iexapis.com
            # Use production: cloud.iexapis.com
            base_url = "https://cloud.iexapis.com/stable"
            url = f"{base_url}/stock/{ticker}/intraday-prices"
            params = {
                'token': api_key,
                'chartLast': 50  # Last 50 data points
            }
            
            response = requests.get(url, params=params, timeout=10)
            data = response.json()
            
            if data and isinstance(data, list):
                df_ticker = pd.DataFrame(data)
                df_ticker['datetime'] = pd.to_datetime(df_ticker['date'] + ' ' + df_ticker['minute'])
                df_ticker = df_ticker.set_index('datetime').sort_index()
                prices[ticker] = df_ticker['close'].astype(float)
                log.info(f"✅ IEX Cloud: Fetched {len(df_ticker)} bars for {ticker}")
            else:
                log.warning(f"IEX Cloud: No data for {ticker}")
                
        except Exception as e:
            log.warning(f"IEX Cloud failed for {ticker}: {e}")
            continue
    
    if prices:
        df = pd.DataFrame(prices)
        log.info(f"✅ IEX Cloud: Total {len(df)} bars for {len(prices)} tickers")
        return df
    
    return pd.DataFrame()


def fetch_prices_with_fallback(tickers: List[str], days: int = 14) -> pd.DataFrame:
    """
    Try multiple price sources with automatic fallback.
    Order of priority:
    1. yfinance (unlimited, but currently failing)
    2. Twelve Data (800 req/day - good for multiple tickers)
    3. Alpha Vantage (25 req/day - limited)
    4. Finnhub (60 calls/min - good rate)
    5. IEX Cloud (limited free tier)
    6. Alpaca (requires subscription for recent data)
    
    Returns:
        DataFrame with prices or empty DataFrame if all fail
    """
    log.info("🔄 Attempting to fetch prices from multiple sources...")
    
    # Try each source in order
    sources = [
        ("Twelve Data", lambda: fetch_prices_twelve_data(tickers, days)),
        ("Finnhub", lambda: fetch_prices_finnhub(tickers, days)),
        ("Alpha Vantage", lambda: fetch_prices_alpha_vantage(tickers)),
        ("IEX Cloud", lambda: fetch_prices_iex_cloud(tickers)),
    ]
    
    for source_name, fetch_func in sources:
        try:
            log.info(f"Trying {source_name}...")
            prices = fetch_func()
            
            if not prices.empty and len(prices) > 0:
                log.info(f"✅ SUCCESS! Got {len(prices)} bars from {source_name}")
                return prices
            else:
                log.warning(f"⚠️ {source_name} returned no data")
        except Exception as e:
            log.warning(f"❌ {source_name} failed: {e}")
            continue
    
    log.error("❌ All price sources failed!")
    return pd.DataFrame()

