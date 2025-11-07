# DJN Broker - Automated Trading System 🚀

An **automated trading system** with sentiment analysis, momentum strategies, and **real broker integration** via Alpaca.

## Features
- 🤖 **Automated Trading**: Real trades via Alpaca API (paper & live trading)
- 📊 **Free Data Sources**: Yahoo Finance, Reddit API, NewsAPI + RSS fallback
- 🧠 **Sentiment Analysis**: VADER (NLTK) for news & social media sentiment
- 📈 **Trading Strategy**: Sentiment + momentum-based signals
- ⏰ **Scheduling**: Automated daily execution
- 🛡️ **Risk Management**: Position limits, allocation controls, stop-loss/take-profit

## Trading Modes

### 1. **Alpaca Paper Trading** (Default, Safe)
Practice with $100k virtual money. No risk, real market data.

### 2. **Alpaca Live Trading** (Real Money)
Execute real trades with your Alpaca brokerage account.

### 3. **Simulation Mode** (No Broker)
Paper trading simulation, saves orders to CSV only.

## Quickstart

### 1. Install Dependencies
```bash
pip3 install -r requirements.txt
```

### 2. Set Up API Credentials
Edit `.env` file:
```bash
# Reddit API (required for sentiment)
REDDIT_CLIENT_ID=your_reddit_client_id
REDDIT_CLIENT_SECRET=your_reddit_secret
REDDIT_USER_AGENT=free-mvp/0.1 by your_username

# NewsAPI (optional - falls back to RSS)
NEWSAPI_KEY=your_newsapi_key

# Alpaca API (required for real trading)
# Get from: https://app.alpaca.markets/paper/dashboard/overview
ALPACA_API_KEY=your_alpaca_api_key
ALPACA_API_SECRET=your_alpaca_secret
```

### 3. Configure Trading Settings
Edit `config.yaml`:
```yaml
universe:
  - "AAPL"   # Your stock picks
  - "MSFT"
  - "GOOGL"

alpaca:
  paper_trading: true   # true = paper, false = LIVE
  use_alpaca: true      # true = Alpaca, false = simulation
```

### 4. Test Alpaca Connection
```bash
python3 check_alpaca_account.py
```

### 5. Run Trading System

**Single run:**
```bash
python3 main.py
```

**Scheduled daily runs:**
```bash
python3 schedule_runner.py
```

## Project Structure
```
DJN-Broker/
├── data/               # Data fetching (market, news, Reddit)
├── nlp/                # Sentiment analysis
├── trade/              # Trading strategy & Alpaca integration
│   ├── alpaca_broker.py  # 🆕 Real broker integration
│   ├── strategy.py       # Trading signals
│   └── simulation.py     # Paper trading fallback
├── utils/              # Logging utilities
├── storage/            # Trade logs and summaries
├── main.py             # Main execution script
├── config.yaml         # Trading configuration
└── .env                # API credentials (not committed)
```

## Safety Features
- ✅ Paper trading enabled by default
- ✅ Position size limits (15% max per trade)
- ✅ Maximum number of positions
- ✅ Stop-loss and take-profit parameters
- ✅ Dry-run simulation mode available

## Getting Alpaca API Keys

### Paper Trading (Free, Recommended)
1. Sign up at [Alpaca](https://alpaca.markets/)
2. Go to [Paper Dashboard](https://app.alpaca.markets/paper/dashboard/overview)
3. Navigate to "API Keys" section
4. Generate new API key & secret
5. Add to `.env` file

### Live Trading (Real Money - Use Caution!)
1. Fund your Alpaca account
2. Get keys from [Live Dashboard](https://app.alpaca.markets/live)
3. Set `paper_trading: false` in `config.yaml`

## Warning ⚠️
- **Start with paper trading** to test your strategy
- This system executes real trades when `use_alpaca: true` and `paper_trading: false`
- **READ [LIVE_TRADING_GUIDE.md](LIVE_TRADING_GUIDE.md) BEFORE enabling live trading**
- Only use live trading if you understand the risks
- Past performance does not guarantee future results
- You can lose money trading

## 📚 Documentation
- **[README.md](README.md)** - Quick start and overview
- **[LIVE_TRADING_GUIDE.md](LIVE_TRADING_GUIDE.md)** - ⚠️ CRITICAL: Read before live trading

## Support
Built for automated trading research. Use responsibly! 🚀
