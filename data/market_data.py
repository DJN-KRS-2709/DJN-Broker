from typing import List
import yfinance as yf
import pandas as pd
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from utils.logger import get_logger
from data.price_sources import fetch_prices_with_fallback

load_dotenv()
log = get_logger("market_data")


def fetch_prices_alpaca(tickers: List[str], days: int = 7, interval: str = "1h") -> pd.DataFrame:
    """
    Fetch historical prices using Alpaca API (alternative to yfinance).
    
    Args:
        tickers: List of stock symbols
        days: Number of days of historical data
        interval: Time interval (1h, 1d, etc.)
    
    Returns:
        DataFrame with ticker columns and closing prices
    """
    api_key = os.getenv("ALPACA_PAPER_API_KEY") or os.getenv("ALPACA_API_KEY")
    api_secret = os.getenv("ALPACA_PAPER_API_SECRET") or os.getenv("ALPACA_API_SECRET")
    
    if not api_key or not api_secret:
        log.error("Alpaca credentials not found for market data")
        return pd.DataFrame()
    
    try:
        client = StockHistoricalDataClient(api_key, api_secret)
        
        # Map interval to Alpaca TimeFrame
        timeframe_map = {
            "1h": TimeFrame.Hour,
            "1d": TimeFrame.Day,
            "15m": TimeFrame.Minute,
            "5m": TimeFrame.Minute,
        }
        timeframe = timeframe_map.get(interval, TimeFrame.Hour)
        
        # Set time range
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        request_params = StockBarsRequest(
            symbol_or_symbols=tickers,
            timeframe=timeframe,
            start=start_date,
            end=end_date
        )
        
        bars = client.get_stock_bars(request_params)
        
        # Convert to DataFrame
        closes = {}
        for ticker in tickers:
            if ticker in bars.data:
                ticker_bars = bars.data[ticker]
                df_ticker = pd.DataFrame([{
                    'timestamp': bar.timestamp,
                    'close': bar.close
                } for bar in ticker_bars])
                df_ticker.set_index('timestamp', inplace=True)
                closes[ticker] = df_ticker['close']
        
        df = pd.DataFrame(closes).dropna(how='all')
        log.info(f"✅ Fetched {len(df)} bars from Alpaca for {len(closes)} tickers")
        return df
        
    except Exception as e:
        log.error(f"Alpaca market data fetch failed: {e}")
        return pd.DataFrame()


def fetch_prices(tickers: List[str], period: str = "7d", interval: str = "1h") -> pd.DataFrame:
    """
    Return a multi-index DataFrame: columns (ticker, field).
    Priority order: Twelve Data API → Alpaca → yfinance (last resort)
    """
    days = int(period.replace('d', '')) if 'd' in period else 14
    
    # PRIORITY 1: Try Twelve Data and other paid APIs first (most reliable)
    log.info("🔄 Trying Twelve Data API (primary source)...")
    prices = fetch_prices_with_fallback(tickers, days=days)
    if not prices.empty:
        log.info(f"✅ Successfully fetched data from alternative APIs")
        return prices
    
    # PRIORITY 2: Try Alpaca as backup
    log.warning("Twelve Data failed, trying Alpaca...")
    alpaca_prices = fetch_prices_alpaca(tickers, days=days, interval=interval)
    if not alpaca_prices.empty:
        log.info(f"✅ Successfully fetched data from Alpaca")
        return alpaca_prices
    
    # PRIORITY 3: Try yfinance as last resort (least reliable)
    log.warning("Alpaca failed, trying yfinance as last resort...")
    try:
        data = yf.download(
            tickers=tickers,
            period=period,
            interval=interval,
            group_by='ticker',
            auto_adjust=True,
            threads=True,
            progress=False
        )
        
        # Ensure a consistent multi-index even for single ticker
        if isinstance(data.columns, pd.Index):
            # Single ticker format -> add top-level with ticker name
            t = tickers[0]
            data = pd.concat({t: data}, axis=1)
        
        # Keep only Close for simplicity
        closes = {}
        for t in tickers:
            try:
                closes[t] = data[t]['Close']
            except Exception:
                continue
        
        df = pd.DataFrame(closes).dropna(how='all')
        
        if len(df) > 0:
            log.info(f"✅ Fetched {len(df)} bars from yfinance for {len(closes)} tickers")
            return df
        else:
            log.error("❌ All price sources failed - no data available")
            return pd.DataFrame()
            
    except Exception as e:
        log.error(f"❌ yfinance (last resort) also failed: {e}")
        return pd.DataFrame()
