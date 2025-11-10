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

    # Momentum per ticker
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
        # Shorting not included for simplicity
    return signals, avg_sent


def enhanced_strategy_with_insights(
    prices: pd.DataFrame,
    news_scores: List[Dict],
    reddit_scores: List[Dict],
    tickers: List[str],
    weekend_insights: List[Dict],
    momentum_window: int = 6,
    min_sentiment: float = 0.4,
):
    """
    Enhanced strategy that combines real-time signals with weekend Tree of Thoughts insights
    
    This strategy:
    1. Uses the simple sentiment momentum strategy as baseline
    2. Boosts signals that align with weekend insights
    3. Filters out signals that contradict high-confidence weekend analysis
    4. Adds new signals from high-confidence weekend insights
    """
    from utils.logger import get_logger
    log = get_logger("strategy")
    
    # Get base signals from simple strategy
    base_signals, avg_sent = simple_sentiment_momentum(
        prices, news_scores, reddit_scores, tickers, momentum_window, min_sentiment
    )
    
    # Create insights lookup by ticker
    insights_map = {}
    for insight in weekend_insights:
        ticker = insight.get('ticker')
        if ticker:
            insights_map[ticker] = insight
    
    log.info(f"📊 Base strategy generated {len(base_signals)} signals")
    log.info(f"🌳 Weekend insights available for {len(insights_map)} tickers")
    
    enhanced_signals = []
    
    # Enhance existing signals
    for sig in base_signals:
        ticker = sig['ticker']
        
        if ticker in insights_map:
            insight = insights_map[ticker]
            signal_type = insight.get('signal', 'NEUTRAL')
            confidence = insight.get('confidence', 0.5)
            
            # If weekend insight agrees with signal, boost it
            if signal_type == 'BULLISH' and sig['action'] == 'BUY':
                sig['strength'] = min(1.0, sig['strength'] * (1 + confidence * 0.5))
                sig['weekend_boost'] = True
                sig['weekend_confidence'] = confidence
                sig['weekend_reasoning'] = insight.get('reasoning', '')
                log.info(f"✨ Boosted {ticker} signal (weekend confidence: {confidence:.2f})")
                enhanced_signals.append(sig)
            
            # If weekend insight contradicts with high confidence, filter out
            elif signal_type == 'BEARISH' and sig['action'] == 'BUY' and confidence > 0.7:
                log.info(f"🚫 Filtered out {ticker} BUY signal (weekend bearish confidence: {confidence:.2f})")
                # Skip this signal
                continue
            
            else:
                # No strong opinion from weekend, keep signal as is
                enhanced_signals.append(sig)
        else:
            # No weekend insight for this ticker, keep signal
            enhanced_signals.append(sig)
    
    # Add high-confidence weekend signals not in base signals
    base_tickers = {sig['ticker'] for sig in base_signals}
    for ticker, insight in insights_map.items():
        if ticker not in base_tickers:
            signal_type = insight.get('signal', 'NEUTRAL')
            confidence = insight.get('confidence', 0.5)
            
            # Only add if high confidence and bullish
            if signal_type == 'BULLISH' and confidence >= 0.65:
                # Check if we have price data and current momentum
                if ticker in prices.columns:
                    series = prices[ticker].dropna()
                    if len(series) >= momentum_window + 1:
                        mom = (series.iloc[-1] / series.iloc[-momentum_window] - 1.0)
                        
                        # Add signal from weekend insights
                        enhanced_signals.append({
                            "ticker": ticker,
                            "action": "BUY",
                            "strength": confidence,
                            "momentum": float(mom),
                            "weekend_only": True,
                            "weekend_confidence": confidence,
                            "weekend_reasoning": insight.get('reasoning', '')
                        })
                        log.info(f"🌟 Added {ticker} signal from weekend insights (confidence: {confidence:.2f})")
    
    log.info(f"🎯 Enhanced strategy generated {len(enhanced_signals)} signals (net change: {len(enhanced_signals) - len(base_signals):+d})")
    
    return enhanced_signals, avg_sent
