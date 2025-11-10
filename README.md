# Free Trading Agent MVP (Cursor-ready)

Build and run a **zero-cost** trading research + simulation agent locally.

## Features
- **Free data sources**: Yahoo Finance (prices), Reddit API (posts), NewsAPI *or* free RSS fallback.
- **Sentiment**: VADER (NLTK) with automatic lexicon download.
- **Signals**: simple sentiment + momentum rule.
- **Simulation**: paper-trade ledger (CSV) with basic risk controls.
- **Scheduling**: optional daily run via `schedule_runner.py`.
- **🌳 Weekend Deep Analysis**: Tree of Thoughts pattern for comprehensive market analysis when markets are closed.
  - Generates and evaluates multiple market hypotheses
  - Deep exploration of promising investment scenarios
  - Synthesizes actionable insights for Monday trading
  - Enhances weekday strategy with weekend research

## Quickstart
1. **Open this folder in Cursor**.
2. Create a virtual env (optional) and install deps:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and set keys (NewsAPI optional):
   ```bash
   cp .env.example .env
   # edit .env and add your keys
   ```
4. (Optional) Edit `config.yaml` to pick tickers and params.
5. **Run once**:
   ```bash
   python main.py
   ```
6. **Schedule daily** (runs at 09:05 Europe/Berlin by default):
   ```bash
   python schedule_runner.py
   ```

## Weekend Deep Analysis (Tree of Thoughts)

The bot automatically runs different logic on weekends vs weekdays:

**Weekdays (Mon-Fri)**: 
- Fetches real-time market data, news, and Reddit sentiment
- Generates trading signals using sentiment + momentum strategy
- **Enhanced with weekend insights** to boost high-confidence signals
- Filters out signals that contradict weekend analysis
- Simulates paper trades and logs to CSV

**Weekends (Sat-Sun)**:
- Runs comprehensive Tree of Thoughts analysis
- Generates multiple market hypotheses per ticker
- Evaluates each hypothesis with evidence from:
  - Multi-timeframe momentum (hourly, daily, weekly)
  - Volatility analysis
  - Technical patterns
  - Sentiment trends
  - Correlation analysis
- Deep exploration of top 10-15 hypotheses
- Synthesizes actionable insights for Monday
- Saves insights to `storage/weekend_insights.json`

**Tree of Thoughts Benefits**:
- More thoughtful decision-making vs purely reactive trading
- Considers multiple scenarios and counter-arguments
- Reduces FOMO and impulsive trades
- Better prepared for Monday market open

## Configuration

Edit `config.yaml` to customize:

```yaml
# Weekend analysis settings
use_weekend_insights: true      # Use Tree of Thoughts insights in Monday trading
run_time: "09:05"               # Daily run time (both weekday/weekend)
weekend_extra_run: false        # Enable extra Saturday afternoon run
weekend_run_time: "10:00"       # Time for extra weekend run (if enabled)
```

## Output Files

- `storage/intended_orders.csv` - Simulated trade orders
- `storage/daily_summary.csv` - Daily trading summary
- `storage/weekend_insights.json` - Weekend Tree of Thoughts analysis (Sat/Sun)

## Notes
- If you don't have a NewsAPI key, the code uses **free RSS feeds** (Reuters/Investing.com/ECB) automatically.
- This project **does NOT place real trades**. It writes intended orders and a simulation PnL to CSV in `storage/`.
- Weekend analysis runs automatically when scheduler detects Saturday/Sunday.
- When you're ready to go beyond MVP, replace `trade/simulation.py` with a broker adapter (e.g., IBKR/Alpaca) and add proper risk management.
