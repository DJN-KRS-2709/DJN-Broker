import schedule, time, yaml, pytz, datetime as dt
from main import run_once, load_config

def main():
    cfg = load_config()
    tz = pytz.timezone(cfg.get("timezone", "Europe/Berlin"))
    run_time = "09:05"
    schedule.every().day.at(run_time).do(lambda: run_once(cfg))
    print(f"Scheduled daily run at {run_time} {cfg.get('timezone')} (now {dt.datetime.now(tz)})")
    while True:
        schedule.run_pending()
        time.sleep(30)

if __name__ == "__main__":
    main()
