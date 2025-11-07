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

load_dotenv()
log = get_logger("main")

def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def run_once(cfg):
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

    signals, avg_sent = simple_sentiment_momentum(
        prices, news_scored, reddit_scored, tickers, momentum_window=6, min_sentiment=0.4
    )

    log.info(f"Avg sentiment={avg_sent:.3f}, generated {len(signals)} signals")
    
    # Check if we should use Alpaca or paper simulation
    use_alpaca = cfg.get('alpaca', {}).get('use_alpaca', False)
    paper_trading = cfg.get('alpaca', {}).get('paper_trading', True)
    
    if use_alpaca:
        log.info(f"🚀 Executing orders via Alpaca ({'PAPER' if paper_trading else 'LIVE'} trading)")
        
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
        'avg_sentiment': avg_sent,
        'n_signals': len(signals),
        'cash_left': res.get('cash_left', 0),
        'executed_count': res.get('executed_count', 0),
        'mode': 'alpaca_paper' if (use_alpaca and paper_trading) else ('alpaca_live' if use_alpaca else 'simulation')
    }
    pd.DataFrame([summary]).to_csv(os.path.join('storage', 'daily_summary.csv'), mode='a', header=not os.path.exists(os.path.join('storage', 'daily_summary.csv')), index=False)

if __name__ == "__main__":
    cfg = load_config()
    run_once(cfg)
