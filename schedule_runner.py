import schedule, time, pytz, datetime as dt
from dual_trading import run_dual_trading, load_config
from learning.trade_memory import TradeMemory
from learning.analyzer import PerformanceAnalyzer
from trade.position_manager import get_closed_trades_summary
from trade.alpaca_broker import get_account_summary
from utils.logger import get_logger

log = get_logger("scheduler")

def job():
    log.info("🤖 Running DUAL trading job (Paper + Live)...")
    
    # Run dual trading (both paper and live)
    run_dual_trading()
    
    # Show comprehensive summary after each run
    cfg = load_config()
    if cfg.get('learning', {}).get('enabled', False):
        memory = TradeMemory()
        analyzer = PerformanceAnalyzer(memory)
        metrics = analyzer.analyze_performance(days=7)
        closed = get_closed_trades_summary()
        
        log.info("=" * 60)
        log.info("📊 DUAL TRADING SUMMARY")
        log.info("=" * 60)
        
        # Paper account summary
        paper_account = get_account_summary(paper=True)
        if paper_account:
            log.info(f"📝 Paper: ${paper_account['portfolio_value']:.2f} portfolio")
        
        # Live account summary  
        live_account = get_account_summary(paper=False)
        if live_account:
            log.info(f"💰 Live: ${live_account['portfolio_value']:.2f} portfolio, "
                    f"{live_account['num_positions']} positions")
        
        # Closed trades (real performance)
        if closed['total_closed'] > 0:
            log.info(f"📈 Closed Trades: {closed['total_closed']} "
                    f"({closed['win_rate']:.0%} win rate, ${closed['total_realized_pnl']:+.2f})")
        
        log.info(f"⭐ Best Stock: {metrics.get('best_stock', 'N/A')}")
        log.info("=" * 60)

def main():
    cfg = load_config()
    tz = pytz.timezone(cfg.get("timezone", "Europe/Berlin"))
    
    # Run immediately on startup
    log.info("🚀 Running initial trade on startup...")
    job()
    
    # Schedule once per day for daily summary
    # Runs at 20:00 CET (8 PM Berlin time)
    # US market: 2:00 PM ET (still open, closes at 4 PM ET)
    
    schedule.every().day.at("20:00").do(job)  # Daily summary at 8 PM CET
    
    log.info("=" * 60)
    log.info("⏰ DUAL TRADING SCHEDULER STARTED")
    log.info("=" * 60)
    log.info(f"Current time: {dt.datetime.now(tz)}")
    log.info(f"Timezone: {cfg.get('timezone')}")
    log.info("")
    log.info("📅 Daily Schedule:")
    log.info("  • 20:00 CET - DUAL TRADING (Paper + Live)")
    log.info("")
    log.info("🔄 How it works:")
    log.info("  📝 Paper: Aggressive trading for learning")
    log.info("  💰 Live: Conservative trading using learnings")
    log.info("=" * 60)
    if cfg.get('learning', {}).get('enabled', False):
        log.info("🧠 Paper learnings → Live trading decisions")
    log.info("=" * 60)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
