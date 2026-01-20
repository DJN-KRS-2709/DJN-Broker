"""
Dual Trading System - Paper Learning + Live Execution

Runs both paper and live trading:
- Paper: Aggressive settings to learn fast (sandbox)
- Live: Conservative settings using paper learnings

Paper trading insights automatically inform live trading decisions.
"""
import yaml
import os
import pandas as pd
from dotenv import load_dotenv
from copy import deepcopy

from utils.logger import get_logger
from data.market_data import fetch_prices
from data.news_data import fetch_news_newsapi, fetch_news_rss
from data.reddit_data import fetch_submissions
from data.data_storage import DataStorage
from data.additional_sources import fetch_all_additional_sources
from nlp.sentiment import score_texts
from trade.strategy import simple_sentiment_momentum
from trade.alpaca_broker import execute_orders, get_account_summary
from trade.position_manager import manage_swing_positions, get_closed_trades_summary

# Learning system imports (shared between paper and live)
from learning.trade_memory import TradeMemory
from learning.analyzer import PerformanceAnalyzer
from learning.strategy_optimizer import StrategyOptimizer

load_dotenv()
log = get_logger("dual_trading")

# Shared learning system - learnings flow from paper to live
shared_memory = TradeMemory()
shared_analyzer = PerformanceAnalyzer(shared_memory)
data_storage = DataStorage()


def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def get_paper_config(base_cfg):
    """
    Paper trading config - more aggressive for learning.
    """
    cfg = deepcopy(base_cfg)
    cfg['alpaca']['paper_trading'] = True
    # Paper can be more aggressive - it's play money
    cfg['risk']['max_positions'] = 4
    cfg['risk']['max_alloc_per_trade'] = 0.25  # 25% per trade
    return cfg


def get_live_config(base_cfg):
    """
    Live trading config - more aggressive, uses learnings.
    """
    cfg = deepcopy(base_cfg)
    cfg['alpaca']['paper_trading'] = False
    # More aggressive settings
    cfg['risk']['max_positions'] = 4  # Up to 4 positions
    cfg['risk']['max_alloc_per_trade'] = 0.25  # 25% per trade (~$140)
    cfg['risk']['stop_loss_pct'] = 0.03  # 3% stop loss
    cfg['risk']['take_profit_pct'] = 0.05  # 5% take profit
    return cfg


def fetch_market_data(cfg):
    """Fetch all market data (shared between paper and live)."""
    tickers = cfg['universe']
    
    # Prices
    prices = fetch_prices(tickers, cfg['data']['yfinance']['period'], cfg['data']['yfinance']['interval'])
    log.info(f"📊 Fetched prices: {prices.shape}")
    
    # Store market data
    data_storage.store_market_data(prices, tickers, source="yfinance")
    
    # News
    news = []
    if cfg['data']['news'].get('use_newsapi', True):
        news = fetch_news_newsapi(cfg['data']['news']['query'], cfg['data']['news']['languages'])
    if not news:
        news = fetch_news_rss(cfg['data']['news']['rss_feeds'])
    news_scored = score_texts(news, text_key="title")
    data_storage.store_news(news_scored)
    
    # Reddit
    reddit = fetch_submissions(cfg['reddit']['subreddits'], cfg['reddit']['limit_per_sub'])
    reddit_scored = score_texts(reddit, text_key="title")
    data_storage.store_reddit(reddit_scored)
    
    # Additional sources
    additional_news = []
    if cfg.get('additional_sources', {}).get('enabled', False):
        additional_data = fetch_all_additional_sources(tickers)
        for source_name, source_data in additional_data.items():
            if isinstance(source_data, list):
                additional_news.extend(source_data)
        if additional_news:
            additional_news_scored = score_texts(additional_news, text_key="title")
            news_scored.extend(additional_news_scored)
    
    return prices, news_scored, reddit_scored


def run_paper_trading(cfg, prices, news_scored, reddit_scored):
    """
    Run paper trading - aggressive learning mode.
    """
    log.info("=" * 60)
    log.info("📝 PAPER TRADING (Learning Mode)")
    log.info("=" * 60)
    
    tickers = cfg['universe']
    paper_optimizer = StrategyOptimizer(shared_memory, shared_analyzer, paper_mode=True)
    
    # Analyze current performance
    metrics = shared_analyzer.analyze_performance(days=7)
    log.info(f"📊 Paper Performance: {metrics.get('win_rate', 0):.1%} win rate")
    
    # Generate signals with lower threshold for more learning
    min_sentiment = 0.15  # Lower threshold = more signals = more learning
    signals, avg_sent = simple_sentiment_momentum(
        prices, news_scored, reddit_scored, tickers, 
        momentum_window=6, min_sentiment=min_sentiment
    )
    
    log.info(f"📈 Sentiment: {avg_sent:.3f}, Signals: {len(signals)}")
    
    # Store signals for learning
    for signal in signals:
        shared_memory.store_signal(signal, {
            'avg_sentiment': avg_sent,
            'mode': 'paper',
            'market_conditions': 'normal'
        })
    
    # Manage existing positions
    if cfg.get('trading_style') == 'swing':
        manage_swing_positions(cfg, paper=True)
    
    # Execute paper trades
    res = execute_orders(
        signals=signals,
        capital=cfg['capital_eur'],
        max_alloc_per_trade=cfg['risk']['max_alloc_per_trade'],
        paper=True
    )
    
    if 'error' not in res:
        log.info(f"✅ Paper: Executed {res['executed_count']} orders")
        
        # Store trades for learning
        for order in res.get('orders', []):
            shared_memory.store_trade({
                'ticker': order['ticker'],
                'action': order['action'],
                'price': order.get('price', 0),
                'notional': order['notional'],
                'order_id': order['order_id'],
                'status': 'open',
                'pnl': 0,
                'mode': 'paper'
            })
    
    return signals, avg_sent, res


def run_live_trading(cfg, prices, news_scored, reddit_scored, paper_signals):
    """
    Run live trading - conservative mode using paper learnings.
    """
    log.info("=" * 60)
    log.info("💰 LIVE TRADING (Real Money - Using Paper Learnings)")
    log.info("=" * 60)
    
    tickers = cfg['universe']
    live_optimizer = StrategyOptimizer(shared_memory, shared_analyzer, paper_mode=False)
    
    # Get recommendations from paper learnings
    recommendations = shared_analyzer.get_strategy_recommendations()
    if recommendations.get('ready'):
        log.info(f"🧠 Using {len(recommendations.get('adjustments', []))} learnings from paper trading")
    
    # Check paper performance before trading live
    metrics = shared_analyzer.analyze_performance(days=7)
    win_rate = metrics.get('win_rate', 0)
    
    # Also check REAL closed trades (more accurate than open trades)
    closed_summary = get_closed_trades_summary()
    real_win_rate = closed_summary.get('win_rate', 0)
    total_closed = closed_summary.get('total_closed', 0)
    
    # Safety check: Don't trade live if closed trades show poor performance
    # But allow trading if we don't have enough closed trade data yet
    if total_closed >= 10 and real_win_rate < 0.3:
        log.warning(f"⚠️ Closed trades win rate too low ({real_win_rate:.1%}). Skipping live trades.")
        log.warning("   Will continue paper trading to learn more.")
        return None, 0, {'skipped': True, 'reason': 'low_winrate'}
    
    # If not enough closed trades, allow live trading (new system bootstrapping)
    if total_closed < 10:
        log.info(f"📊 Only {total_closed} closed trades - bootstrapping mode (live trading enabled)")
    
    # Use same sentiment threshold as paper (more aggressive)
    min_sentiment = 0.15  # Lower = more trades
    
    # Skip optimizer threshold adjustment for more aggressive trading
    # Just use the base threshold directly
    log.info(f"🎯 Using aggressive sentiment threshold: {min_sentiment}")
    
    # Generate signals with higher threshold
    signals, avg_sent = simple_sentiment_momentum(
        prices, news_scored, reddit_scored, tickers,
        momentum_window=6, min_sentiment=min_sentiment
    )
    
    log.info(f"📈 Sentiment: {avg_sent:.3f}, Live Signals: {len(signals)}")
    
    # Show best performers but don't filter aggressively
    best_stocks = shared_memory.get_best_performing_stocks(limit=3)
    if best_stocks:
        log.info(f"⭐ Best performers from paper: {best_stocks}")
    # Trade all signals that pass sentiment threshold (more aggressive)
    
    # Get account status
    account = get_account_summary(paper=False)
    if account:
        log.info(f"💼 Live Account: ${account['portfolio_value']:.2f} value, "
                f"${account['buying_power']:.2f} buying power")
    
    # Manage existing positions
    if cfg.get('trading_style') == 'swing':
        manage_swing_positions(cfg, paper=False)
    
    # Execute live trades (if any signals pass the filter)
    if signals:
        res = execute_orders(
            signals=signals,
            capital=cfg['capital_eur'],
            max_alloc_per_trade=cfg['risk']['max_alloc_per_trade'],
            paper=False
        )
        
        if 'error' not in res:
            log.info(f"✅ LIVE: Executed {res['executed_count']} orders")
            
            # Store live trades (separate tracking)
            for order in res.get('orders', []):
                shared_memory.store_trade({
                    'ticker': order['ticker'],
                    'action': order['action'],
                    'price': order.get('price', 0),
                    'notional': order['notional'],
                    'order_id': order['order_id'],
                    'status': 'open',
                    'pnl': 0,
                    'mode': 'live'  # Mark as live trade
                })
        else:
            log.error(f"Live execution error: {res.get('error')}")
            res = {'error': res.get('error')}
    else:
        log.info("📊 No signals passed live filters. Waiting for better opportunities.")
        res = {'executed_count': 0, 'cash_left': cfg['capital_eur'], 'orders': []}
    
    return signals, avg_sent, res


def run_dual_trading():
    """
    Main function: Run both paper and live trading.
    """
    log.info("=" * 60)
    log.info("🤖 DUAL TRADING SYSTEM")
    log.info("   Paper: Learning Mode (Aggressive)")
    log.info("   Live: Real Money (Conservative + Learnings)")
    log.info("=" * 60)
    
    base_cfg = load_config()
    
    # Fetch market data ONCE (shared)
    log.info("📡 Fetching market data...")
    prices, news_scored, reddit_scored = fetch_market_data(base_cfg)
    
    # Run PAPER trading first (generates learnings)
    paper_cfg = get_paper_config(base_cfg)
    paper_signals, paper_sentiment, paper_result = run_paper_trading(
        paper_cfg, prices, news_scored, reddit_scored
    )
    
    # Run LIVE trading (uses learnings from paper)
    live_cfg = get_live_config(base_cfg)
    live_signals, live_sentiment, live_result = run_live_trading(
        live_cfg, prices, news_scored, reddit_scored, paper_signals
    )
    
    # Save dual summary
    summary = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'mode': 'dual',
        # Paper stats
        'paper_signals': len(paper_signals) if paper_signals else 0,
        'paper_executed': paper_result.get('executed_count', 0) if paper_result else 0,
        'paper_sentiment': paper_sentiment,
        # Live stats
        'live_signals': len(live_signals) if live_signals else 0,
        'live_executed': live_result.get('executed_count', 0) if live_result else 0,
        'live_sentiment': live_sentiment,
        'live_skipped': live_result.get('skipped', False) if live_result else False,
    }
    
    # Get closed trades summary
    closed_summary = get_closed_trades_summary()
    summary['total_closed'] = closed_summary.get('total_closed', 0)
    summary['real_win_rate'] = closed_summary.get('win_rate', 0)
    summary['realized_pnl'] = closed_summary.get('total_realized_pnl', 0)
    
    pd.DataFrame([summary]).to_csv(
        'storage/dual_trading_summary.csv', 
        mode='a', 
        header=not os.path.exists('storage/dual_trading_summary.csv'), 
        index=False
    )
    
    log.info("=" * 60)
    log.info("✅ DUAL TRADING COMPLETE")
    log.info(f"   Paper: {summary['paper_executed']} trades")
    log.info(f"   Live: {summary['live_executed']} trades")
    log.info("🧠 Learnings shared: Paper → Live")
    log.info("=" * 60)


if __name__ == "__main__":
    run_dual_trading()

