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
    
    # Schedule for multiple times during the day for aggressive trading
    # US market hours: 9:30 AM - 4:00 PM ET
    # In Europe/Berlin (CET/CEST), that's approximately:
    # - 15:30 (3:30 PM) - 22:00 (10:00 PM) during standard time
    # - 16:30 (4:30 PM) - 23:00 (11:00 PM) during daylight saving time
    
    schedule.every().day.at("09:00").do(job)  # Morning pre-market analysis
    schedule.every().day.at("15:35").do(job)  # Right after US market open
    schedule.every().day.at("18:00").do(job)  # US midday
    schedule.every().day.at("21:30").do(job)  # Before US market close
    
    log.info("=" * 60)
    log.info("⏰ AGGRESSIVE SCHEDULER STARTED")
    log.info("=" * 60)
    log.info(f"Current time: {dt.datetime.now(tz)}")
    log.info(f"Timezone: {cfg.get('timezone')}")
    log.info("")
    log.info("📅 Daily Schedule:")
    log.info("  • 09:00 - Morning pre-market analysis")
    log.info("  • 15:35 - Right after US market open")
    log.info("  • 18:00 - US market midday")
    log.info("  • 21:30 - Before US market close")
    log.info("=" * 60)
    if cfg.get('learning', {}).get('enabled', False):
        log.info("🧠 Learning system will optimize after each run")
    log.info("=" * 60)
    
    while True:
        schedule.run_pending()
        time.sleep(60)

if __name__ == "__main__":
    main()
