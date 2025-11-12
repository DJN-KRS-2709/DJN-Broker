"""
Trade Outcome Tracker

This script helps track trade outcomes and store them in RAG memory for learning.
Run this periodically to update the RAG system with trade results.
"""

import yaml
import pandas as pd
from datetime import datetime
from utils.rag_memory import TradingMemory
from utils.logger import get_logger

log = get_logger("trade_tracker")


def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def track_trade_outcomes():
    """
    Track trade outcomes from intended_orders.csv and store in RAG memory
    
    This is a simplified tracker. In production, you'd integrate with your broker API
    to get actual fill prices and outcomes.
    """
    cfg = load_config()
    
    # Initialize RAG memory
    if not cfg.get('rag', {}).get('enabled', False):
        log.warning("RAG is not enabled in config.yaml")
        return
    
    memory = TradingMemory(
        storage_path=cfg['rag'].get('storage_path', './storage/chroma_db'),
        model_name=cfg['rag'].get('model', 'all-MiniLM-L6-v2')
    )
    
    log.info("📊 Loading trade orders from storage/intended_orders.csv")
    
    try:
        df = pd.read_csv('storage/intended_orders.csv')
        log.info(f"Found {len(df)} orders")
        
        # For demo purposes, simulate outcomes
        # In production, you'd fetch actual outcomes from your broker
        
        for idx, row in df.iterrows():
            ticker = row.get('ticker', 'UNKNOWN')
            action = row.get('action', 'BUY')
            price = row.get('price', 0.0)
            
            # Simulate outcome (in production, use actual data)
            # For now, just store the order as OPEN
            trade = {
                'ticker': ticker,
                'action': action,
                'entry_price': price,
                'exit_price': 0.0,  # Would be filled when position closes
                'outcome': 'OPEN',
                'pnl': 0.0,
                'timestamp': datetime.now().isoformat(),
                'reasoning': row.get('reasoning', 'Automated trade from strategy')
            }
            
            memory.store_trade_outcome(trade)
            log.info(f"Stored trade: {ticker} {action} @ ${price:.2f}")
        
        log.info("✅ Trade outcomes tracked successfully")
        
        # Show stats
        stats = memory.get_stats()
        log.info(f"📈 RAG Memory Stats: {stats}")
        
    except FileNotFoundError:
        log.warning("No orders file found at storage/intended_orders.csv")
    except Exception as e:
        log.error(f"Error tracking trades: {e}", exc_info=True)


def update_trade_outcome(ticker: str, entry_price: float, exit_price: float, outcome: str):
    """
    Update a specific trade outcome
    
    Args:
        ticker: Stock ticker
        entry_price: Entry price
        exit_price: Exit price
        outcome: WIN, LOSS, or NEUTRAL
    """
    cfg = load_config()
    
    if not cfg.get('rag', {}).get('enabled', False):
        log.warning("RAG is not enabled")
        return
    
    memory = TradingMemory(
        storage_path=cfg['rag'].get('storage_path', './storage/chroma_db'),
        model_name=cfg['rag'].get('model', 'all-MiniLM-L6-v2')
    )
    
    pnl = exit_price - entry_price
    
    trade = {
        'ticker': ticker,
        'action': 'BUY',  # Assuming BUY for simplicity
        'entry_price': entry_price,
        'exit_price': exit_price,
        'outcome': outcome,
        'pnl': pnl,
        'timestamp': datetime.now().isoformat(),
        'reasoning': f'Manual outcome update: {outcome}'
    }
    
    memory.store_trade_outcome(trade)
    log.info(f"✅ Updated trade outcome: {ticker} {outcome} (PnL: ${pnl:.2f})")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'update':
        # Manual update mode: python track_trade_outcomes.py update AAPL 150.00 155.00 WIN
        if len(sys.argv) >= 6:
            ticker = sys.argv[2]
            entry = float(sys.argv[3])
            exit_price = float(sys.argv[4])
            outcome = sys.argv[5].upper()
            update_trade_outcome(ticker, entry, exit_price, outcome)
        else:
            print("Usage: python track_trade_outcomes.py update TICKER ENTRY_PRICE EXIT_PRICE OUTCOME")
            print("Example: python track_trade_outcomes.py update AAPL 150.00 155.00 WIN")
    else:
        # Auto-track mode
        track_trade_outcomes()

