import schedule, time, pytz, datetime as dt
from main import run_once, load_config
from learning.trade_memory import TradeMemory
from learning.analyzer import PerformanceAnalyzer
from utils.logger import get_logger

log = get_logger("scheduler")

def job():
    log.info("🤖 Running scheduled trading job...")
    cfg = load_config()
    run_once(cfg)
    
    # Show learning summary after each run
    if cfg.get('learning', {}).get('enabled', False):
        memory = TradeMemory()
        analyzer = PerformanceAnalyzer(memory)
        metrics = analyzer.analyze_performance(days=7)
        
        log.info("=" * 60)
        log.info("📊 WEEKLY PERFORMANCE SUMMARY")
        log.info("=" * 60)
        log.info(f"Total Trades: {metrics.get('total_trades', 0)}")
        log.info(f"Win Rate: {metrics.get('win_rate', 0):.1%}")
        log.info(f"Total P&L: ${metrics.get('total_pnl', 0):.2f}")
        log.info(f"Best Stock: {metrics.get('best_stock', 'N/A')}")
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
    log.info("⏰ DAILY SCHEDULER STARTED")
    log.info("=" * 60)
    log.info(f"Current time: {dt.datetime.now(tz)}")
    log.info(f"Timezone: {cfg.get('timezone')}")
    log.info("")
    log.info("📅 Daily Schedule:")
    log.info("  • 20:00 - Daily summary (8 PM CET)")
    log.info("=" * 60)
    if cfg.get('learning', {}).get('enabled', False):
        log.info("🧠 Learning system will optimize after each run")
    log.info("=" * 60)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
