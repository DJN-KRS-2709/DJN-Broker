import yaml, os, pandas as pd
from dotenv import load_dotenv
from utils.logger import get_logger
from data.market_data import fetch_prices
from data.news_data import fetch_news_newsapi, fetch_news_rss
from data.reddit_data import fetch_submissions
from data.data_storage import DataStorage
from data.additional_sources import fetch_all_additional_sources
from nlp.sentiment import score_texts
from trade.strategy import simple_sentiment_momentum
from trade.simulation import run_simulation
from trade.alpaca_broker import execute_orders, get_account_summary
from trade.position_manager import manage_swing_positions

# Learning system imports
from learning.trade_memory import TradeMemory
from learning.analyzer import PerformanceAnalyzer
from learning.strategy_optimizer import StrategyOptimizer

load_dotenv()
log = get_logger("main")

def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

# Initialize learning system
memory = TradeMemory()
analyzer = PerformanceAnalyzer(memory)

# Load config to determine paper/live mode
cfg = load_config()
paper_mode = cfg.get('alpaca', {}).get('paper_trading', True)
optimizer = StrategyOptimizer(memory, analyzer, paper_mode=paper_mode)

# Initialize data storage system
data_storage = DataStorage()

def run_once(cfg):
    log.info("=" * 60)
    log.info("🤖 LEARNING-ENABLED TRADING BOT STARTING")
    log.info("=" * 60)
    
    # Check if learning system is enabled
    learning_enabled = cfg.get('learning', {}).get('enabled', False)
    
    if learning_enabled:
        log.info("🧠 Learning system: ENABLED")
        
        # Analyze performance and show learnings
        metrics = analyzer.analyze_performance(days=cfg.get('learning', {}).get('performance_lookback_days', 7))
        log.info(f"📊 Win rate: {metrics.get('win_rate', 0):.1%}, Total P&L: ${metrics.get('total_pnl', 0):.2f}")
        
        for insight in metrics.get('insights', []):
            log.info(f"   {insight}")
        
        # Check if we should pause trading
        if optimizer.should_pause_trading():
            log.warning("🛑 Trading paused due to poor performance. Review strategy!")
            return
        
        # Get optimization summary
        opt_summary = optimizer.get_optimization_summary()
        if opt_summary.get('best_stocks'):
            log.info(f"⭐ Best performers: {', '.join(opt_summary['best_stocks'])}")
    else:
        log.info("📝 Learning system: DISABLED")
    
    tickers = cfg['universe']
    prices = fetch_prices(tickers, cfg['data']['yfinance']['period'], cfg['data']['yfinance']['interval'])
    log.info(f"Fetched prices with shape {prices.shape}")
    
    # Store market data (will auto-detect source from fetch_prices)
    data_source = "alpaca" if len(prices) > 0 and "Alpaca" in str(type(prices)) else "yfinance"
    data_storage.store_market_data(prices, tickers, source=data_source)

    # News
    news = []
    if cfg['data']['news'].get('use_newsapi', True):
        news = fetch_news_newsapi(cfg['data']['news']['query'], cfg['data']['news']['languages'])
    if not news:
        news = fetch_news_rss(cfg['data']['news']['rss_feeds'])
    news_scored = score_texts(news, text_key="title")
    
    # Store news with sentiment scores
    data_storage.store_news(news_scored)

    # Reddit
    reddit = fetch_submissions(cfg['reddit']['subreddits'], cfg['reddit']['limit_per_sub'])
    reddit_scored = score_texts(reddit, text_key="title")
    
    # Store Reddit with sentiment scores
    data_storage.store_reddit(reddit_scored)
    
    # Fetch additional sources (Yahoo Finance, Investing.com, MarketWatch, etc.)
    additional_news = []
    if cfg.get('additional_sources', {}).get('enabled', False):
        log.info("🌐 Fetching from additional sources...")
        additional_data = fetch_all_additional_sources(tickers)
        
        # Combine all additional news into single list for sentiment analysis
        for source_name, source_data in additional_data.items():
            if isinstance(source_data, list):
                additional_news.extend(source_data)
        
        # Score sentiment on additional news
        if additional_news:
            additional_news_scored = score_texts(additional_news, text_key="title")
            # Add to main news list for strategy
            news_scored.extend(additional_news_scored)
            log.info(f"✅ Added {len(additional_news)} articles from additional sources")
        
        # Store additional sources data
        data_storage.store_additional_sources(additional_data)

    # Apply learning optimizations if enabled
    min_sentiment = 0.2  # Temporarily lowered to generate signals with current sentiment
    if learning_enabled:
        strategy_params = optimizer.optimize_strategy({
            'min_sentiment': 0.2,  # Lowered threshold
            'take_profit_pct': cfg['risk']['take_profit_pct'],
            'stop_loss_pct': cfg['risk']['stop_loss_pct']
        })
        min_sentiment = strategy_params.get('min_sentiment', 0.2)
        log.info(f"🎯 Optimized sentiment threshold: {min_sentiment:.2f}")

    signals, avg_sent = simple_sentiment_momentum(
        prices, news_scored, reddit_scored, tickers, momentum_window=6, min_sentiment=min_sentiment
    )
    
    # Helper to extract compound sentiment
    def get_compound(item):
        sent = item.get('sentiment', {})
        return sent.get('compound', 0) if isinstance(sent, dict) else sent
    
    # Store overall sentiment summary
    data_storage.store_sentiment_summary({
        'overall_sentiment': avg_sent,
        'news_sentiment': sum(get_compound(n) for n in news_scored) / len(news_scored) if news_scored else 0,
        'reddit_sentiment': sum(get_compound(r) for r in reddit_scored) / len(reddit_scored) if reddit_scored else 0,
        'news_count': len(news_scored),
        'reddit_count': len(reddit_scored),
        'num_signals': len(signals)
    })

    # Store signals with context for learning
    if learning_enabled:
        for signal in signals:
            memory.store_signal(signal, {
                'avg_sentiment': avg_sent,
                'market_conditions': 'normal',  # Could be enhanced
                'news_count': len(news),
                'reddit_count': len(reddit)
            })

    log.info(f"Avg sentiment={avg_sent:.3f}, generated {len(signals)} signals")
    
    # Log data storage stats
    storage_stats = data_storage.get_storage_stats()
    log.info(f"📦 Data archived: {storage_stats['market_data_entries']} market, "
             f"{storage_stats['news_entries']} news, {storage_stats['reddit_entries']} reddit entries")
    
    # Filter signals based on learnings (TEMPORARILY DISABLED for sentiment-only mode)
    if learning_enabled and signals and False:  # Disabled
        original_count = len(signals)
        signals = optimizer.filter_signals_by_learning(signals)
        if len(signals) < original_count:
            log.info(f"🧠 Filtered signals: {original_count} → {len(signals)} based on learnings")
    
    # Check if we should use Alpaca or paper simulation
    use_alpaca = cfg.get('alpaca', {}).get('use_alpaca', False)
    paper_trading = cfg.get('alpaca', {}).get('paper_trading', True)
    
    if use_alpaca:
        log.info(f"🚀 Executing orders via Alpaca ({'PAPER' if paper_trading else 'LIVE'} trading)")
        
        # Manage existing positions (for swing trading)
        if cfg.get('trading_style') == 'swing':
            log.info("📊 Managing swing positions...")
            manage_swing_positions(cfg, paper=paper_trading)
        
        # Get current account status
        account_summary = get_account_summary(paper=paper_trading)
        if account_summary:
            log.info(f"Account: ${account_summary['portfolio_value']:.2f} portfolio, "
                    f"${account_summary['buying_power']:.2f} buying power, "
                    f"{account_summary['num_positions']} positions")
        
        # Execute real orders via Alpaca
        res = execute_orders(
            signals=signals,
            capital=cfg['capital_eur'],
            max_alloc_per_trade=cfg['risk']['max_alloc_per_trade'],
            paper=paper_trading
        )
        
        if 'error' in res:
            log.error(f"Failed to execute orders: {res['error']}")
        else:
            log.info(f"✅ Executed {res['executed_count']} orders, cash_left=${res['cash_left']:.2f}")
            
            # Save executed orders to CSV
            if res['orders']:
                df = pd.DataFrame(res['orders'])
                path = os.path.join('storage', 'executed_orders.csv')
                if os.path.exists(path):
                    df_prev = pd.read_csv(path)
                    df = pd.concat([df_prev, df], ignore_index=True)
                df.to_csv(path, index=False)
                
                # Store trades in learning system
                if learning_enabled:
                    for order in res['orders']:
                        # Store trade (we'll update with P&L later when we close)
                        memory.store_trade({
                            'ticker': order['ticker'],
                            'action': order['action'],
                            'price': order.get('price', 0),
                            'notional': order['notional'],
                            'order_id': order['order_id'],
                            'status': 'open',
                            'pnl': 0  # Will update when closed
                        })
                    log.info(f"💾 Stored {len(res['orders'])} trades in learning system")
    else:
        log.info("📝 Running paper simulation (no real trades)")
        res = run_simulation(
            prices=prices,
            signals=signals,
            capital=cfg['capital_eur'],
            max_alloc_per_trade=cfg['risk']['max_alloc_per_trade'],
            path=os.path.join('storage', 'intended_orders.csv')
        )
        log.info(f"Orders written: {len(res['orders'])}, cash_left={res['cash_left']}")
    
    # Save a tiny daily summary
    summary = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'avg_sentiment': avg_sent,
        'n_signals': len(signals),
        'cash_left': res.get('cash_left', 0),
        'executed_count': res.get('executed_count', 0),
        'mode': 'alpaca_paper' if (use_alpaca and paper_trading) else ('alpaca_live' if use_alpaca else 'simulation'),
        'learning_enabled': learning_enabled
    }
    
    # Add performance metrics if available
    if learning_enabled:
        metrics = memory.get_performance_metrics()
        summary['win_rate'] = metrics.get('win_rate', 0)
        summary['total_pnl'] = metrics.get('total_pnl', 0)
        summary['total_trades'] = metrics.get('total_trades', 0)
    
    pd.DataFrame([summary]).to_csv(os.path.join('storage', 'daily_summary.csv'), mode='a', header=not os.path.exists(os.path.join('storage', 'daily_summary.csv')), index=False)
    
    # Send email notification if configured
    recipient_email = os.getenv('NOTIFICATION_EMAIL')
    if recipient_email:
        try:
            from utils.email_notifier import send_trading_summary
            send_trading_summary(summary, recipient_email)
            log.info(f"📧 Email summary sent to {recipient_email}")
        except Exception as e:
            log.warning(f"Failed to send email: {e}")
    
    log.info("=" * 60)
    log.info("✅ TRADING RUN COMPLETE")
    if learning_enabled:
        log.info("🧠 System is learning from every trade!")
    log.info("=" * 60)

if __name__ == "__main__":
    cfg = load_config()
    run_once(cfg)
