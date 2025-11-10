"""
Weekend Deep Analysis using Tree of Thoughts Pattern

This module performs comprehensive market analysis over the weekend when markets are closed.
It uses the Tree of Thoughts reasoning pattern to:
1. Generate multiple market hypotheses
2. Evaluate each hypothesis with data
3. Explore promising branches deeper
4. Synthesize actionable insights for Monday trading
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json
import os
from utils.logger import get_logger

log = get_logger("weekend_analysis")


@dataclass
class Hypothesis:
    """A market hypothesis to explore"""
    id: str
    description: str
    confidence: float = 0.0
    evidence: List[str] = None
    contradictions: List[str] = None
    score: float = 0.0
    
    def __post_init__(self):
        if self.evidence is None:
            self.evidence = []
        if self.contradictions is None:
            self.contradictions = []


@dataclass
class MarketInsight:
    """An actionable market insight derived from analysis"""
    ticker: str
    signal: str  # "BULLISH", "BEARISH", "NEUTRAL"
    confidence: float
    reasoning: str
    key_factors: List[str]
    risk_factors: List[str]


class TreeOfThoughtsAnalyzer:
    """
    Implements Tree of Thoughts pattern for deep market analysis
    """
    
    def __init__(self, tickers: List[str]):
        self.tickers = tickers
        self.hypotheses: List[Hypothesis] = []
        self.insights: List[MarketInsight] = []
        
    def generate_hypotheses(
        self, 
        prices: pd.DataFrame, 
        weekly_prices: pd.DataFrame,
        news_scores: List[Dict],
        reddit_scores: List[Dict]
    ) -> List[Hypothesis]:
        """
        STEP 1: Generate multiple market hypotheses to explore
        """
        log.info("🌳 Generating market hypotheses (Tree of Thoughts - Level 1)...")
        hypotheses = []
        
        # Analyze overall market sentiment
        avg_sentiment = self._calculate_avg_sentiment(news_scores, reddit_scores)
        
        for ticker in self.tickers:
            if ticker not in prices.columns:
                continue
                
            # Generate 3-4 hypotheses per ticker
            
            # Hypothesis 1: Momentum continuation
            mom_short = self._calculate_momentum(prices, ticker, window=5)
            mom_long = self._calculate_momentum(weekly_prices, ticker, window=4)
            
            if mom_short > 0 and mom_long > 0:
                hypotheses.append(Hypothesis(
                    id=f"{ticker}_momentum_bull",
                    description=f"{ticker} will continue bullish momentum on Monday",
                    confidence=0.6
                ))
            elif mom_short < 0 and mom_long < 0:
                hypotheses.append(Hypothesis(
                    id=f"{ticker}_momentum_bear",
                    description=f"{ticker} will continue bearish momentum on Monday",
                    confidence=0.6
                ))
            
            # Hypothesis 2: Mean reversion
            volatility = self._calculate_volatility(prices, ticker)
            if abs(mom_short) > 0.03 and volatility > 0.02:
                hypotheses.append(Hypothesis(
                    id=f"{ticker}_mean_reversion",
                    description=f"{ticker} is overextended and may mean-revert",
                    confidence=0.5
                ))
            
            # Hypothesis 3: Sentiment-driven move
            if avg_sentiment > 0.3:
                hypotheses.append(Hypothesis(
                    id=f"{ticker}_sentiment_bull",
                    description=f"{ticker} will rally on positive market sentiment",
                    confidence=0.5
                ))
            elif avg_sentiment < -0.3:
                hypotheses.append(Hypothesis(
                    id=f"{ticker}_sentiment_bear",
                    description=f"{ticker} will decline on negative market sentiment",
                    confidence=0.5
                ))
            
            # Hypothesis 4: Breakout potential
            resistance = self._find_resistance_level(weekly_prices, ticker)
            current_price = prices[ticker].iloc[-1] if len(prices[ticker]) > 0 else None
            if current_price and resistance and current_price > resistance * 0.98:
                hypotheses.append(Hypothesis(
                    id=f"{ticker}_breakout",
                    description=f"{ticker} is near resistance and may breakout",
                    confidence=0.5
                ))
        
        log.info(f"Generated {len(hypotheses)} initial hypotheses")
        self.hypotheses = hypotheses
        return hypotheses
    
    def evaluate_hypotheses(
        self,
        prices: pd.DataFrame,
        weekly_prices: pd.DataFrame,
        news_scores: List[Dict],
        reddit_scores: List[Dict]
    ) -> List[Hypothesis]:
        """
        STEP 2: Evaluate each hypothesis with evidence
        """
        log.info("🔍 Evaluating hypotheses with evidence (Tree of Thoughts - Level 2)...")
        
        avg_sentiment = self._calculate_avg_sentiment(news_scores, reddit_scores)
        
        for hyp in self.hypotheses:
            ticker = hyp.id.split('_')[0]
            
            if ticker not in prices.columns:
                continue
            
            # Gather evidence for this hypothesis
            if "momentum_bull" in hyp.id:
                mom_1d = self._calculate_momentum(prices, ticker, window=1)
                mom_5d = self._calculate_momentum(prices, ticker, window=5)
                mom_weekly = self._calculate_momentum(weekly_prices, ticker, window=4)
                
                if mom_1d > 0:
                    hyp.evidence.append(f"1-day momentum: +{mom_1d*100:.1f}%")
                    hyp.confidence += 0.1
                else:
                    hyp.contradictions.append(f"1-day momentum negative: {mom_1d*100:.1f}%")
                    hyp.confidence -= 0.15
                
                if mom_5d > 0.02:
                    hyp.evidence.append(f"5-day momentum strong: +{mom_5d*100:.1f}%")
                    hyp.confidence += 0.15
                    
                if mom_weekly > 0.05:
                    hyp.evidence.append(f"Weekly momentum very strong: +{mom_weekly*100:.1f}%")
                    hyp.confidence += 0.2
                
                if avg_sentiment > 0.2:
                    hyp.evidence.append(f"Positive market sentiment: {avg_sentiment:.2f}")
                    hyp.confidence += 0.1
                    
            elif "momentum_bear" in hyp.id:
                mom_1d = self._calculate_momentum(prices, ticker, window=1)
                mom_5d = self._calculate_momentum(prices, ticker, window=5)
                
                if mom_1d < 0:
                    hyp.evidence.append(f"1-day momentum: {mom_1d*100:.1f}%")
                    hyp.confidence += 0.1
                else:
                    hyp.contradictions.append(f"1-day momentum positive: +{mom_1d*100:.1f}%")
                    hyp.confidence -= 0.15
                
                if avg_sentiment < -0.2:
                    hyp.evidence.append(f"Negative market sentiment: {avg_sentiment:.2f}")
                    hyp.confidence += 0.1
                    
            elif "mean_reversion" in hyp.id:
                vol = self._calculate_volatility(prices, ticker)
                mom = self._calculate_momentum(prices, ticker, window=5)
                avg_price = prices[ticker].tail(20).mean()
                current = prices[ticker].iloc[-1]
                
                deviation = abs(current - avg_price) / avg_price
                if deviation > 0.03:
                    hyp.evidence.append(f"Price deviation from 20-bar avg: {deviation*100:.1f}%")
                    hyp.confidence += 0.15
                
                if vol > 0.03:
                    hyp.evidence.append(f"High volatility: {vol*100:.1f}%")
                    hyp.confidence += 0.1
                    
            elif "sentiment" in hyp.id:
                ticker_mentions = self._count_ticker_mentions(ticker, news_scores, reddit_scores)
                if ticker_mentions > 3:
                    hyp.evidence.append(f"{ticker} mentioned {ticker_mentions} times in news/reddit")
                    hyp.confidence += 0.2
                
                if avg_sentiment > 0.3 and "bull" in hyp.id:
                    hyp.evidence.append(f"Strong positive sentiment: {avg_sentiment:.2f}")
                    hyp.confidence += 0.2
                elif avg_sentiment < -0.3 and "bear" in hyp.id:
                    hyp.evidence.append(f"Strong negative sentiment: {avg_sentiment:.2f}")
                    hyp.confidence += 0.2
                    
            elif "breakout" in hyp.id:
                resistance = self._find_resistance_level(weekly_prices, ticker)
                current = prices[ticker].iloc[-1]
                volume = self._calculate_relative_volume(prices, ticker)
                
                if current and resistance and current > resistance * 0.98:
                    hyp.evidence.append(f"Price near resistance: {current:.2f} vs {resistance:.2f}")
                    hyp.confidence += 0.15
                
                if volume > 1.2:
                    hyp.evidence.append(f"Above-average volume: {volume:.1f}x")
                    hyp.confidence += 0.15
            
            # Calculate final score
            hyp.score = hyp.confidence * (len(hyp.evidence) / max(len(hyp.contradictions) + 1, 1))
            hyp.score = max(0, min(1, hyp.score))  # Clamp between 0 and 1
        
        # Sort by score
        self.hypotheses.sort(key=lambda h: h.score, reverse=True)
        log.info(f"Evaluated {len(self.hypotheses)} hypotheses")
        
        return self.hypotheses
    
    def explore_promising_branches(
        self,
        prices: pd.DataFrame,
        weekly_prices: pd.DataFrame,
        top_k: int = 10
    ) -> List[Hypothesis]:
        """
        STEP 3: Deep dive into the most promising hypotheses
        """
        log.info(f"🔬 Deep exploration of top {top_k} hypotheses (Tree of Thoughts - Level 3)...")
        
        top_hypotheses = self.hypotheses[:top_k]
        
        for hyp in top_hypotheses:
            ticker = hyp.id.split('_')[0]
            
            if ticker not in prices.columns:
                continue
            
            # Deep analysis: sector correlation, technical patterns, risk factors
            
            # Check correlation with market (using first ticker as proxy)
            market_ticker = self.tickers[0]
            if ticker != market_ticker and market_ticker in prices.columns:
                correlation = self._calculate_correlation(prices, ticker, market_ticker)
                if abs(correlation) > 0.7:
                    hyp.evidence.append(f"High correlation with market: {correlation:.2f}")
            
            # Check for technical patterns
            pattern = self._detect_pattern(prices, ticker)
            if pattern:
                hyp.evidence.append(f"Technical pattern: {pattern}")
                if ("bull" in hyp.id and "bullish" in pattern) or ("bear" in hyp.id and "bearish" in pattern):
                    hyp.score += 0.1
            
            # Risk assessment
            vol = self._calculate_volatility(prices, ticker)
            if vol > 0.04:
                hyp.evidence.append(f"HIGH RISK: Volatility {vol*100:.1f}%")
                hyp.score *= 0.9  # Penalize high-risk plays
        
        # Re-sort after deep analysis
        self.hypotheses.sort(key=lambda h: h.score, reverse=True)
        
        return self.hypotheses
    
    def synthesize_insights(self, min_score: float = 0.5) -> List[MarketInsight]:
        """
        STEP 4: Convert top hypotheses into actionable insights
        """
        log.info("💡 Synthesizing actionable insights (Tree of Thoughts - Final)...")
        
        insights = []
        seen_tickers = set()
        
        for hyp in self.hypotheses:
            if hyp.score < min_score:
                continue
            
            ticker = hyp.id.split('_')[0]
            
            # Only one insight per ticker (highest scoring)
            if ticker in seen_tickers:
                continue
            seen_tickers.add(ticker)
            
            # Determine signal
            signal = "NEUTRAL"
            if "bull" in hyp.id or "breakout" in hyp.id:
                signal = "BULLISH"
            elif "bear" in hyp.id:
                signal = "BEARISH"
            elif "mean_reversion" in hyp.id:
                # Mean reversion is contrarian
                signal = "BEARISH" if hyp.description and "decline" in hyp.description else "NEUTRAL"
            
            insight = MarketInsight(
                ticker=ticker,
                signal=signal,
                confidence=hyp.score,
                reasoning=hyp.description,
                key_factors=hyp.evidence[:5],  # Top 5 evidence points
                risk_factors=[c for c in hyp.contradictions[:3]]  # Top 3 risks
            )
            insights.append(insight)
        
        self.insights = insights
        log.info(f"Generated {len(insights)} actionable insights for Monday")
        
        return insights
    
    # Helper methods
    
    def _calculate_avg_sentiment(self, news_scores: List[Dict], reddit_scores: List[Dict]) -> float:
        """Calculate average sentiment from news and reddit"""
        scores = []
        for item in news_scores + reddit_scores:
            if 'sentiment' in item and 'compound' in item['sentiment']:
                scores.append(item['sentiment']['compound'])
        return np.mean(scores) if scores else 0.0
    
    def _calculate_momentum(self, prices: pd.DataFrame, ticker: str, window: int) -> float:
        """Calculate momentum over window periods"""
        if ticker not in prices.columns:
            return 0.0
        series = prices[ticker].dropna()
        if len(series) < window + 1:
            return 0.0
        return float(series.iloc[-1] / series.iloc[-window] - 1.0)
    
    def _calculate_volatility(self, prices: pd.DataFrame, ticker: str, window: int = 10) -> float:
        """Calculate rolling volatility"""
        if ticker not in prices.columns:
            return 0.0
        series = prices[ticker].dropna()
        if len(series) < window:
            return 0.0
        returns = series.pct_change().tail(window)
        return float(returns.std())
    
    def _find_resistance_level(self, prices: pd.DataFrame, ticker: str) -> float:
        """Find recent resistance level (simple: recent high)"""
        if ticker not in prices.columns:
            return None
        series = prices[ticker].dropna()
        if len(series) < 5:
            return None
        return float(series.tail(20).max())
    
    def _calculate_relative_volume(self, prices: pd.DataFrame, ticker: str) -> float:
        """Calculate relative volume (if volume data available, else return 1.0)"""
        # For simplicity, return 1.0 since we're using hourly price data
        return 1.0
    
    def _count_ticker_mentions(self, ticker: str, news_scores: List[Dict], reddit_scores: List[Dict]) -> int:
        """Count how many times ticker is mentioned"""
        count = 0
        ticker_base = ticker.split('.')[0].upper()  # e.g., "SAP" from "SAP.DE"
        
        for item in news_scores + reddit_scores:
            text = (item.get('title', '') + ' ' + item.get('text', '')).upper()
            if ticker_base in text:
                count += 1
        
        return count
    
    def _calculate_correlation(self, prices: pd.DataFrame, ticker1: str, ticker2: str, window: int = 20) -> float:
        """Calculate correlation between two tickers"""
        if ticker1 not in prices.columns or ticker2 not in prices.columns:
            return 0.0
        
        s1 = prices[ticker1].dropna().tail(window)
        s2 = prices[ticker2].dropna().tail(window)
        
        if len(s1) < 5 or len(s2) < 5:
            return 0.0
        
        return float(s1.corr(s2))
    
    def _detect_pattern(self, prices: pd.DataFrame, ticker: str) -> str:
        """Simple pattern detection"""
        if ticker not in prices.columns:
            return None
        
        series = prices[ticker].dropna()
        if len(series) < 10:
            return None
        
        recent = series.tail(10)
        
        # Simple pattern: consecutive higher highs
        if all(recent.iloc[i] > recent.iloc[i-1] for i in range(len(recent)-3, len(recent))):
            return "bullish_trend"
        elif all(recent.iloc[i] < recent.iloc[i-1] for i in range(len(recent)-3, len(recent))):
            return "bearish_trend"
        
        return None


def run_weekend_analysis(cfg: Dict) -> Dict:
    """
    Main weekend analysis function using Tree of Thoughts
    """
    from data.market_data import fetch_prices
    from data.news_data import fetch_news_newsapi, fetch_news_rss
    from data.reddit_data import fetch_submissions
    from nlp.sentiment import score_texts
    
    log.info("=" * 80)
    log.info("🌳 WEEKEND DEEP ANALYSIS - Tree of Thoughts Pattern")
    log.info("=" * 80)
    
    tickers = cfg['universe']
    
    # Fetch extended data for deeper analysis
    log.info("📊 Fetching extended market data...")
    
    # Get daily data for the past month
    prices_daily = fetch_prices(tickers, period="1mo", interval="1d")
    
    # Get hourly data for the past week
    prices_hourly = fetch_prices(tickers, period="7d", interval="1h")
    
    # Get weekly data for longer-term trends
    prices_weekly = fetch_prices(tickers, period="3mo", interval="1wk")
    
    log.info(f"Daily prices: {prices_daily.shape}, Hourly: {prices_hourly.shape}, Weekly: {prices_weekly.shape}")
    
    # Fetch comprehensive news (larger query)
    log.info("📰 Fetching comprehensive news and sentiment...")
    news = []
    if cfg['data']['news'].get('use_newsapi', True):
        # Expanded news fetch for weekend
        news = fetch_news_newsapi(
            cfg['data']['news'].get('weekend_query', cfg['data']['news']['query']),
            cfg['data']['news']['languages']
        )
    if not news:
        news = fetch_news_rss(cfg['data']['news']['rss_feeds'])
    
    news_scored = score_texts(news, text_key="title")
    
    # Fetch more Reddit data
    reddit = fetch_submissions(
        cfg['reddit']['subreddits'],
        cfg['reddit'].get('weekend_limit_per_sub', cfg['reddit']['limit_per_sub'] * 2)
    )
    reddit_scored = score_texts(reddit, text_key="title")
    
    log.info(f"Analyzed {len(news_scored)} news items and {len(reddit_scored)} reddit posts")
    
    # Initialize Tree of Thoughts analyzer
    analyzer = TreeOfThoughtsAnalyzer(tickers)
    
    # Step 1: Generate hypotheses
    hypotheses = analyzer.generate_hypotheses(
        prices_hourly, prices_weekly, news_scored, reddit_scored
    )
    
    # Step 2: Evaluate with evidence
    hypotheses = analyzer.evaluate_hypotheses(
        prices_hourly, prices_weekly, news_scored, reddit_scored
    )
    
    # Step 3: Deep exploration of top hypotheses
    hypotheses = analyzer.explore_promising_branches(
        prices_hourly, prices_weekly, top_k=15
    )
    
    # Step 4: Synthesize actionable insights
    insights = analyzer.synthesize_insights(min_score=0.4)
    
    # Save insights for Monday
    output = {
        'timestamp': datetime.now().isoformat(),
        'analysis_type': 'weekend_tree_of_thoughts',
        'hypotheses_evaluated': len(hypotheses),
        'insights': [
            {
                'ticker': i.ticker,
                'signal': i.signal,
                'confidence': round(i.confidence, 3),
                'reasoning': i.reasoning,
                'key_factors': i.key_factors,
                'risk_factors': i.risk_factors
            }
            for i in insights
        ],
        'top_hypotheses': [
            {
                'id': h.id,
                'description': h.description,
                'score': round(h.score, 3),
                'confidence': round(h.confidence, 3),
                'evidence': h.evidence,
                'contradictions': h.contradictions
            }
            for h in hypotheses[:10]
        ]
    }
    
    # Save to storage
    os.makedirs('storage', exist_ok=True)
    output_path = os.path.join('storage', 'weekend_insights.json')
    with open(output_path, 'w') as f:
        json.dump(output, f, indent=2)
    
    log.info(f"💾 Saved weekend insights to {output_path}")
    
    # Log summary
    log.info("\n" + "=" * 80)
    log.info("📊 WEEKEND ANALYSIS SUMMARY")
    log.info("=" * 80)
    log.info(f"Total hypotheses evaluated: {len(hypotheses)}")
    log.info(f"Actionable insights for Monday: {len(insights)}")
    log.info("\nTop 5 Insights:")
    for i, insight in enumerate(insights[:5], 1):
        log.info(f"{i}. {insight.ticker}: {insight.signal} (confidence: {insight.confidence:.2f})")
        log.info(f"   Reasoning: {insight.reasoning}")
        if insight.key_factors:
            log.info(f"   Key factors: {', '.join(insight.key_factors[:2])}")
    log.info("=" * 80)
    
    return output


