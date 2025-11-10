from typing import List, Dict
import pandas as pd
import os

def run_simulation(prices: pd.DataFrame, signals: List[Dict], capital: float, max_alloc_per_trade: float, path:str) -> Dict:
    """Very simple simulator: buy at last close price, no carry across days (flat by EOD)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    rows = []
    cash = capital
    for sig in signals:
        t = sig['ticker']
        if t not in prices.columns: 
            continue
        price = float(prices[t].iloc[-1])
        alloc = min(cash, capital * max_alloc_per_trade)
        if alloc < price:
            continue
        qty = int(alloc // price)
        if qty <= 0:
            continue
        entry = price
        # naive exit target for MVP: take-profit or stop-loss on same bar is ignored; we just write intent
        rows.append({
            "ticker": t,
            "action": sig['action'],
            "price": entry,
            "qty": qty,
            "notional": round(qty * entry, 2)
        })
        cash -= qty * entry
    df = pd.DataFrame(rows)
    if not df.empty:
        if os.path.exists(path):
            df_prev = pd.read_csv(path)
            df = pd.concat([df_prev, df], ignore_index=True)
        df.to_csv(path, index=False)
    return {"orders": rows, "cash_left": round(cash, 2)}
