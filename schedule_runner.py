import schedule, time, yaml, pytz, datetime as dt
from main import run_once, load_config
from nlp.weekend_analysis import run_weekend_analysis
from utils.logger import get_logger

log = get_logger("scheduler")

def scheduled_job(cfg, tz):
    """
    Smart scheduler: runs different logic on weekends vs weekdays
    - Weekends (Sat/Sun): Deep Tree of Thoughts analysis
    - Weekdays (Mon-Fri): Regular trading logic
    """
    now = dt.datetime.now(tz)
    day_name = now.strftime("%A")
    
    # Weekend: Saturday (5) or Sunday (6)
    if now.weekday() >= 5:
        log.info(f"🌳 {day_name} detected - Running WEEKEND DEEP ANALYSIS")
        log.info("Using Tree of Thoughts pattern to analyze market trends...")
        try:
            run_weekend_analysis(cfg)
            log.info("✅ Weekend analysis completed successfully")
        except Exception as e:
            log.error(f"❌ Weekend analysis failed: {e}", exc_info=True)
    else:
        # Weekday: Regular trading
        log.info(f"📈 {day_name} detected - Running REGULAR TRADING LOGIC")
        try:
            run_once(cfg)
            log.info("✅ Trading logic completed successfully")
        except Exception as e:
            log.error(f"❌ Trading logic failed: {e}", exc_info=True)

def main():
    cfg = load_config()
    tz = pytz.timezone(cfg.get("timezone", "Europe/Berlin"))
    run_time = cfg.get("run_time", "09:05")
    weekend_run_time = cfg.get("weekend_run_time", "10:00")
    
    # Schedule both weekday and weekend runs
    schedule.every().day.at(run_time).do(lambda: scheduled_job(cfg, tz))
    
    # Optional: Extra weekend run (Saturday afternoon for deep analysis)
    if cfg.get("weekend_extra_run", False):
        schedule.every().saturday.at(weekend_run_time).do(lambda: run_weekend_analysis(cfg))
    
    log.info("=" * 80)
    log.info("🤖 AI Trading Bot Scheduler Started")
    log.info("=" * 80)
    log.info(f"📅 Daily run time: {run_time} {cfg.get('timezone')}")
    log.info(f"🌍 Timezone: {cfg.get('timezone')}")
    log.info(f"⏰ Current time: {dt.datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S %A')}")
    log.info("")
    log.info("📋 Schedule:")
    log.info(f"  • Weekdays (Mon-Fri): Regular trading at {run_time}")
    log.info(f"  • Weekends (Sat-Sun): Deep analysis at {run_time}")
    if cfg.get("weekend_extra_run", False):
        log.info(f"  • Saturday extra: Deep analysis at {weekend_run_time}")
    log.info("=" * 80)
    
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
