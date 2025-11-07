# Free Trading Agent MVP (Cursor-ready)

Build and run a **zero-cost** trading research + simulation agent locally.

## Features
- **Free data sources**: Yahoo Finance (prices), Reddit API (posts), NewsAPI *or* free RSS fallback.
- **Sentiment**: VADER (NLTK) with automatic lexicon download.
- **Signals**: simple sentiment + momentum rule.
- **Simulation**: paper-trade ledger (CSV) with basic risk controls.
- **Scheduling**: optional daily run via `schedule_runner.py`.

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

## Notes
- If you don’t have a NewsAPI key, the code uses **free RSS feeds** (Reuters/Investing.com/ECB) automatically.
- This project **does NOT place real trades**. It writes intended orders and a simulation PnL to CSV in `storage/`.
- When you’re ready to go beyond MVP, replace `trade/simulation.py` with a broker adapter (e.g., IBKR/Alpaca) and add proper risk management.
