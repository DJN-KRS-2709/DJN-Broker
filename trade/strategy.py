from typing import Dict, List
import pandas as pd
import numpy as np

def calculate_rsi(series: pd.Series, period: int = 14) -> float:
    """Calculate RSI (Relative Strength Index)."""
    if len(series) < period + 1:
        return 50.0  # Neutral if not enough data
    
    delta = series.diff()
    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)
    
    avg_gain = gain.rolling(window=period).mean().iloc[-1]
    avg_loss = loss.rolling(window=period).mean().iloc[-1]
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    return float(rsi)

def calculate_trend_strength(series: pd.Series, short_window: int = 5, long_window: int = 20) -> float:
    """
    Calculate trend strength using moving average crossover.
    Returns positive for uptrend, negative for downtrend.
    """
    if len(series) < long_window:
        return 0.0
    
    short_ma = series.rolling(window=short_window).mean().iloc[-1]
    long_ma = series.rolling(window=long_window).mean().iloc[-1]
    
    # Percentage difference between short and long MA
    trend = (short_ma - long_ma) / long_ma
    return float(trend)

def simple_sentiment_momentum(
    prices: pd.DataFrame,
    news_scores: List[Dict],
    reddit_scores: List[Dict],
    tickers: List[str],
    momentum_window: int = 6,  # ~6 hours if using 1h bars
    min_sentiment: float = 0.4,
):
    signals = []
    # Aggregate sentiment
    agg_sent = 0.0
    cnt = 0
    for item in (news_scores + reddit_scores):
        sc = item.get("sentiment", {}).get("compound", 0.0)
        agg_sent += sc
        cnt += 1
    avg_sent = (agg_sent / cnt) if cnt else 0.0

    # Check if we have price data
    has_price_data = not prices.empty and len(prices.columns) > 0
    
    if has_price_data:
        # Enhanced mode: Use momentum + sentiment + technical confirmation
        ticker_scores = []
        
        for t in tickers:
            if t not in prices.columns:
                continue
            series = prices[t].dropna()
            if len(series) < momentum_window + 1:
                continue
            
            # Calculate momentum
            mom = (series.iloc[-1] / series.iloc[-momentum_window] - 1.0)
            
            # Calculate RSI (avoid overbought stocks)
            rsi = calculate_rsi(series)
            
            # Calculate trend strength
            trend = calculate_trend_strength(series)
            
            # Score the ticker
            score = 0.0
            
            # Sentiment check
            if avg_sent >= min_sentiment:
                score += avg_sent * 0.4  # 40% weight on sentiment
            
            # Momentum check (positive momentum = good)
            if mom > 0.0:
                score += min(mom * 5, 0.3)  # Cap at 30% weight
            
            # RSI check (avoid overbought > 70, favor oversold < 40)
            if 30 <= rsi <= 65:  # Sweet spot
                score += 0.2
            elif rsi < 30:  # Oversold - potential bounce
                score += 0.15
            elif rsi > 75:  # Overbought - skip
                score -= 0.3
            
            # Trend confirmation
            if trend > 0.01:  # In uptrend
                score += 0.1
            elif trend < -0.02:  # In downtrend - avoid
                score -= 0.2
            
            ticker_scores.append({
                "ticker": t,
                "score": score,
                "momentum": float(mom),
                "rsi": rsi,
                "trend": trend,
                "sentiment": avg_sent
            })
        
        # Sort by score and take top performers
        ticker_scores.sort(key=lambda x: x["score"], reverse=True)
        
        # Only generate signals for tickers with positive scores
        for ts in ticker_scores:
            if ts["score"] > 0.3:  # Minimum score threshold
                signals.append({
                    "ticker": ts["ticker"], 
                    "action": "BUY", 
                    "strength": float(min(ts["score"], 1.0)), 
                    "momentum": ts["momentum"],
                    "rsi": ts["rsi"],
                    "trend": ts["trend"]
                })
    else:
        # FALLBACK MODE: Sentiment-only (when price data unavailable)
        if avg_sent >= min_sentiment:
            # Generate buy signals for top 2 tickers based on sentiment only
            # This is a simplified approach when market data is unavailable
            for t in tickers[:2]:  # Trade only top 2 tickers (e.g., AAPL, MSFT)
                signals.append({
                    "ticker": t, 
                    "action": "BUY", 
                    "strength": float(min(avg_sent, 1.0)), 
                    "momentum": 0.0,  # No momentum data available
                    "sentiment_only": True
                })
    
    return signals, avg_sent
