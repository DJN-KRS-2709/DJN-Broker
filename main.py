import yaml, os, pandas as pd
from dotenv import load_dotenv
from utils.logger import get_logger
from data.market_data import fetch_prices
from data.news_data import fetch_news_newsapi, fetch_news_rss
from data.reddit_data import fetch_submissions
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

# Initialize learning system
memory = TradeMemory()
analyzer = PerformanceAnalyzer(memory)
optimizer = StrategyOptimizer(memory, analyzer)

def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

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

    # News
    news = []
    if cfg['data']['news'].get('use_newsapi', True):
        news = fetch_news_newsapi(cfg['data']['news']['query'], cfg['data']['news']['languages'])
    if not news:
        news = fetch_news_rss(cfg['data']['news']['rss_feeds'])
    news_scored = score_texts(news, text_key="title")

    # Reddit
    reddit = fetch_submissions(cfg['reddit']['subreddits'], cfg['reddit']['limit_per_sub'])
    reddit_scored = score_texts(reddit, text_key="title")

    # Apply learning optimizations if enabled
    min_sentiment = 0.4
    if learning_enabled:
        strategy_params = optimizer.optimize_strategy({
            'min_sentiment': 0.4,
            'take_profit_pct': cfg['risk']['take_profit_pct'],
            'stop_loss_pct': cfg['risk']['stop_loss_pct']
        })
        min_sentiment = strategy_params.get('min_sentiment', 0.4)
        log.info(f"🎯 Optimized sentiment threshold: {min_sentiment:.2f}")

    signals, avg_sent = simple_sentiment_momentum(
        prices, news_scored, reddit_scored, tickers, momentum_window=6, min_sentiment=min_sentiment
    )

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
    
    # Filter signals based on learnings
    if learning_enabled and signals:
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
