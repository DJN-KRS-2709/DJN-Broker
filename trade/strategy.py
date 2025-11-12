from typing import Dict, List
import pandas as pd

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
        # Normal mode: Use momentum + sentiment
        for t in tickers:
            if t not in prices.columns:
                continue
            series = prices[t].dropna()
            if len(series) < momentum_window + 1:
                continue
            mom = (series.iloc[-1] / series.iloc[-momentum_window] - 1.0)
            # Long if sentiment positive and momentum positive
            if avg_sent >= min_sentiment and mom > 0.0:
                signals.append({"ticker": t, "action": "BUY", "strength": float(min(avg_sent, 1.0)), "momentum": float(mom)})
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
