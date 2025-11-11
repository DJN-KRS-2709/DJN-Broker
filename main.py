import yaml, os, pandas as pd, json
from dotenv import load_dotenv
from datetime import datetime
from utils.logger import get_logger
from data.market_data import fetch_prices
from data.news_data import fetch_news_newsapi, fetch_news_rss
from data.reddit_data import fetch_submissions
from nlp.sentiment import score_texts
from trade.strategy import simple_sentiment_momentum, enhanced_strategy_with_insights
from trade.simulation import run_simulation

load_dotenv()
log = get_logger("main")

def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_weekend_insights():
    """Load weekend analysis insights if available"""
    insights_path = os.path.join('storage', 'weekend_insights.json')
    if os.path.exists(insights_path):
        try:
            with open(insights_path, 'r') as f:
                data = json.load(f)
                log.info(f"📚 Loaded weekend insights from {data.get('timestamp', 'unknown time')}")
                return data.get('insights', [])
        except Exception as e:
            log.warning(f"Could not load weekend insights: {e}")
    return None

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

    # Initialize RAG memory if enabled
    rag_memory = None
    if cfg.get('rag', {}).get('enabled', False):
        try:
            from utils.rag_memory import TradingMemory
            rag_memory = TradingMemory(
                storage_path=cfg['rag'].get('storage_path', './storage/chroma_db'),
                model_name=cfg['rag'].get('model', 'all-MiniLM-L6-v2')
            )
            stats = rag_memory.get_stats()
            log.info(f"🧠 RAG Memory: {stats.get('total_insights', 0)} insights, {stats.get('total_trades', 0)} trades stored")
        except Exception as e:
            log.warning(f"Failed to initialize RAG memory: {e}")
            rag_memory = None

    # Try to load weekend insights
    weekend_insights = load_weekend_insights()
    
    # Use enhanced strategy if weekend insights available, otherwise use simple strategy
    if weekend_insights and cfg.get('use_weekend_insights', True):
        log.info(f"🌳 Using enhanced strategy with {len(weekend_insights)} weekend insights")
        signals, avg_sent = enhanced_strategy_with_insights(
            prices, news_scored, reddit_scored, tickers, weekend_insights,
            momentum_window=6, min_sentiment=0.4, rag_memory=rag_memory
        )
    else:
        log.info("📊 Using simple sentiment momentum strategy")
        signals, avg_sent = simple_sentiment_momentum(
            prices, news_scored, reddit_scored, tickers, momentum_window=6, min_sentiment=0.4
        )

    log.info(f"Avg sentiment={avg_sent:.3f}, generated {len(signals)} signals")
    res = run_simulation(
        prices=prices,
        signals=signals,
        capital=cfg.get('capital_usd', cfg.get('capital_eur', 500)),  # Support both USD and EUR
        max_alloc_per_trade=cfg['risk']['max_alloc_per_trade'],
        path=os.path.join('storage', 'intended_orders.csv')
    )
    log.info(f"Orders written: {len(res['orders'])}, cash_left={res['cash_left']}")
    # Save a tiny daily summary
    summary = {
        'avg_sentiment': avg_sent,
        'n_signals': len(signals),
        'cash_left': res['cash_left'],
        'used_weekend_insights': weekend_insights is not None
    }
    pd.DataFrame([summary]).to_csv(os.path.join('storage', 'daily_summary.csv'), mode='a', header=not os.path.exists(os.path.join('storage', 'daily_summary.csv')), index=False)

if __name__ == "__main__":
    cfg = load_config()
    run_once(cfg)
