# Data Sources & Storage System

## 📊 Overview

Your trading bot now collects and stores data from **multiple sources** for RAG (Retrieval-Augmented Generation) learning. All data is automatically archived and used for strategy optimization.

---

## 🌐 Data Sources

### 1. **Market Price Data** 📈
- **Primary Source:** Yahoo Finance (yfinance)
- **Fallback Source:** Alpaca Market Data API
- **Data Type:** Historical stock prices (OHLCV)
- **Frequency:** 1-hour bars, 14 days lookback
- **Tickers:** AAPL, MSFT, GOOGL, TSLA, NVDA
- **Fallback Logic:** Automatically switches to Alpaca if yfinance fails

**Note:** Alpaca free tier has limitations on recent data. If both sources fail, trading continues using sentiment-only signals.

### 2. **News Data** 📰
- **Primary Source:** NewsAPI (if API key configured)
- **Fallback Source:** RSS Feeds
  - Reuters Finance Europe
  - European Central Bank Press
  - Investing.com
- **Languages:** English & German
- **Volume:** ~25 articles per language
- **Sentiment Analysis:** VADER (NLTK) - compound score [-1, 1]

### 3. **Social Media Data** 🤖
- **Source:** Reddit API
- **Subreddits:**
  - r/stocks
  - r/investing
  - r/wallstreetbets
  - r/StockMarket
- **Volume:** 25 posts per subreddit (~100 total)
- **Sentiment Analysis:** VADER on titles and content
- **Requires:** Reddit API credentials in `.env`

### 4. **Broker Data** 💼
- **Source:** Alpaca Trading API
- **Data:** 
  - Account status
  - Portfolio value
  - Open positions
  - Order history
  - Real-time P&L

---

## 💾 Data Storage & Archiving

All data is automatically stored in `storage/data_archive/` for RAG learning:

### Storage Structure:
```
storage/
├── data_archive/
│   ├── market_data_history.json    # Price data (30 days)
│   ├── news_history.json           # News articles with sentiment (30 days)
│   ├── reddit_history.json         # Reddit posts with sentiment (30 days)
│   └── sentiment_history.json      # Overall sentiment trends (90 days)
├── learning/
│   ├── trades_history.json         # All executed trades
│   ├── signals_history.json        # All trading signals
│   ├── learnings.json             # AI-discovered insights
│   └── performance_metrics.json    # Performance statistics
└── daily_summary.csv               # Quick daily overview
```

### What Gets Stored:

#### **News Archive** (`news_history.json`)
```json
{
  "timestamp": "2025-11-12T13:05:47.961641",
  "date": "2025-11-12",
  "count": 10,
  "avg_sentiment": 0.020,
  "articles": [
    {
      "title": "Stock market today...",
      "source": "Reuters",
      "url": "https://...",
      "publishedAt": "2025-11-12",
      "sentiment": {
        "compound": 0.84,
        "pos": 0.406,
        "neg": 0.0,
        "neu": 0.594
      }
    }
  ]
}
```

#### **Reddit Archive** (`reddit_history.json`)
```json
{
  "timestamp": "2025-11-12T13:05:48.774",
  "date": "2025-11-12",
  "count": 100,
  "avg_sentiment": 0.15,
  "subreddits": ["stocks", "investing", "wallstreetbets"],
  "posts": [
    {
      "subreddit": "stocks",
      "title": "AAPL analysis...",
      "url": "https://reddit.com/...",
      "sentiment": {
        "compound": 0.72,
        "pos": 0.35,
        "neg": 0.05,
        "neu": 0.60
      }
    }
  ]
}
```

#### **Sentiment Trends** (`sentiment_history.json`)
```json
{
  "timestamp": "2025-11-12T13:05:48.775",
  "date": "2025-11-12",
  "overall_sentiment": 0.42,
  "news_sentiment": 0.38,
  "reddit_sentiment": 0.45,
  "news_count": 10,
  "reddit_count": 100,
  "num_signals": 3
}
```

#### **Market Data** (`market_data_history.json`)
```json
{
  "timestamp": "2025-11-12T13:05:44.870",
  "date": "2025-11-12",
  "source": "yfinance",
  "tickers": ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA"],
  "num_bars": 336,
  "latest_prices": {
    "AAPL": 235.42,
    "MSFT": 420.15,
    "GOOGL": 175.30
  },
  "data": { ... }
}
```

---

## 🧠 RAG Learning System

The stored data is used by the RAG learning system to:

1. **Identify Patterns**
   - Which news sources have highest signal accuracy
   - Which subreddits provide best sentiment signals
   - Optimal sentiment thresholds for entry
   - Best performing stocks

2. **Optimize Strategy**
   - Adjust sentiment threshold based on historical win rate
   - Filter signals based on learned patterns
   - Pause trading during poor market conditions
   - Focus on best-performing stocks

3. **Performance Analysis**
   - Calculate win rates by stock, time, sentiment
   - Track P&L trends
   - Generate actionable insights
   - Adapt risk parameters

---

## 📱 Viewing Your Data

### Quick Stats:
```bash
python3 show_data_archive.py
```

Shows:
- Storage statistics
- Recent news headlines with sentiment
- Recent Reddit posts with sentiment
- Sentiment trends over time
- Market data summary

### View Learning Insights:
```bash
python3 show_learnings.py
```

Shows:
- AI-discovered patterns
- Best performing stocks
- Performance metrics
- Strategy recommendations

---

## ⚙️ Configuration

### Enable/Disable Data Sources

Edit `config.yaml`:

```yaml
data:
  yfinance:
    period: "14d"
    interval: "1h"
  
  news:
    use_newsapi: true      # Set to false to use RSS only
    languages: ["en", "de"]
    query: "stocks OR market OR DAX OR ECB OR earnings"
    rss_feeds:
      - "https://www.reuters.com/finance/markets/europe/rss"
      - "https://www.ecb.europa.eu/press/pressconf/2024/html/index.en.html"

reddit:
  subreddits: ["stocks", "investing", "wallstreetbets", "StockMarket"]
  limit_per_sub: 25
```

### API Keys (.env)

```bash
# NewsAPI (optional - falls back to RSS)
NEWSAPI_KEY=your_newsapi_key_here

# Reddit API (required for Reddit data)
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USER_AGENT=free-mvp/0.1 by your_username

# Alpaca (for trading + market data fallback)
ALPACA_PAPER_API_KEY=your_key_here
ALPACA_PAPER_API_SECRET=your_secret_here
```

---

## 🔄 Data Retention

- **Market Data:** 30 days
- **News:** 30 days
- **Reddit:** 30 days
- **Sentiment Trends:** 90 days
- **Trades/Learnings:** Unlimited

Older data is automatically purged to keep storage size manageable.

---

## 📊 Storage Size

Typical storage usage:
- **Market Data:** ~5 MB/month
- **News:** ~2 MB/month
- **Reddit:** ~3 MB/month
- **Sentiment:** ~0.5 MB/month
- **Trades/Learning:** ~1 MB/month

**Total:** ~12 MB/month

---

## 🚀 Benefits

1. **Historical Context:** Learn from past market conditions
2. **Pattern Recognition:** Identify what works and what doesn't
3. **Adaptive Strategy:** Continuously improve based on results
4. **Data-Driven Decisions:** Every trade is informed by historical data
5. **Transparency:** Full audit trail of all data and decisions

---

## 🛠️ Troubleshooting

### No Market Data
- **yfinance fails:** This is common. The bot will try Alpaca automatically.
- **Alpaca fails:** Free tier has limitations. Bot continues with sentiment-only.
- **Solution:** Add a paid Alpaca data subscription or wait for yfinance to recover.

### No Reddit Data
- **Check credentials:** Ensure `REDDIT_CLIENT_ID` and `REDDIT_CLIENT_SECRET` are correct
- **API limits:** Reddit has rate limits. Bot will retry on next run.
- **Verify:** Go to https://www.reddit.com/prefs/apps to check your app

### No News Data
- **NewsAPI limit:** Free tier: 100 requests/day
- **Fallback active:** Bot automatically uses RSS feeds
- **Solution:** No action needed - RSS feeds work well

---

## 📈 Next Steps

Want to add more data sources?
1. **Twitter/X API** - Social sentiment
2. **Financial Modeling Prep** - Fundamentals
3. **SEC Edgar** - Company filings
4. **Crypto APIs** - Digital asset prices
5. **Economic indicators** - Fed data, GDP, unemployment

All can be integrated into the existing storage system!

---

## ✅ Summary

Your bot now:
- ✅ Fetches data from **6+ sources** (yfinance, Alpaca, NewsAPI, RSS, Reddit, Broker)
- ✅ Automatically **stores all data** in RAG system
- ✅ **Falls back** when sources fail
- ✅ **Learns patterns** from historical data
- ✅ **Optimizes strategy** based on learnings
- ✅ Provides **full transparency** with data viewer tools

**Every trading decision is now backed by comprehensive historical data!** 🎯





