from typing import List
import yfinance as yf
import pandas as pd

def fetch_prices(tickers: List[str], period: str = "7d", interval: str = "1h") -> pd.DataFrame:
    """Return a multi-index DataFrame: columns (ticker, field)."""
    data = yf.download(
        tickers=tickers,
        period=period,
        interval=interval,
        group_by='ticker',
        auto_adjust=True,
        threads=True,
        progress=False
    )
    # Ensure a consistent multi-index even for single ticker
    if isinstance(data.columns, pd.Index):
        # Single ticker format -> add top-level with ticker name
        t = tickers[0]
        data = pd.concat({t: data}, axis=1)
    # Keep only Close for simplicity
    closes = {}
    for t in tickers:
        try:
            closes[t] = data[t]['Close']
        except Exception:
            continue
    df = pd.DataFrame(closes).dropna(how='all')
    return df
