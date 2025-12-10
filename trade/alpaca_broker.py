"""
Alpaca broker integration for executing real trades.
Supports both paper trading and live trading.
"""
import os
import json
from datetime import datetime, timezone
from typing import List, Dict, Optional
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from utils.logger import get_logger

load_dotenv()
log = get_logger("alpaca_broker")

# Position tracking file path
POSITION_TRACKING_FILE = "storage/position_tracking.json"


def get_alpaca_client(paper: bool = True) -> Optional[TradingClient]:
    """
    Initialize Alpaca trading client.
    
    Args:
        paper: If True, use paper trading. If False, use live trading.
    
    Returns:
        TradingClient or None if credentials missing
    """
    # Use separate credentials for paper vs live
    if paper:
        api_key = os.getenv("ALPACA_PAPER_API_KEY") or os.getenv("ALPACA_API_KEY")
        api_secret = os.getenv("ALPACA_PAPER_API_SECRET") or os.getenv("ALPACA_API_SECRET")
    else:
        api_key = os.getenv("ALPACA_LIVE_API_KEY")
        api_secret = os.getenv("ALPACA_LIVE_API_SECRET")
    
    if not api_key or not api_secret:
        log.error(f"Alpaca {'paper' if paper else 'LIVE'} credentials missing in .env file")
        return None
    
    try:
        client = TradingClient(api_key, api_secret, paper=paper)
        account = client.get_account()
        log.info(f"Connected to Alpaca ({'PAPER' if paper else 'LIVE'} trading)")
        log.info(f"Account status: {account.status}, Buying power: ${float(account.buying_power):.2f}")
        return client
    except Exception as e:
        log.error(f"Failed to connect to Alpaca: {e}")
        return None


def _load_position_tracking() -> Dict:
    """Load position tracking data from JSON file."""
    try:
        if os.path.exists(POSITION_TRACKING_FILE):
            with open(POSITION_TRACKING_FILE, 'r') as f:
                return json.load(f)
        return {"_comment": "Tracks entry times for open positions", "positions": {}}
    except Exception as e:
        log.error(f"Failed to load position tracking: {e}")
        return {"positions": {}}


def _save_position_tracking(data: Dict):
    """Save position tracking data to JSON file."""
    try:
        os.makedirs(os.path.dirname(POSITION_TRACKING_FILE), exist_ok=True)
        with open(POSITION_TRACKING_FILE, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        log.error(f"Failed to save position tracking: {e}")


def track_position_entry(ticker: str, order_id: str, notional: float, submitted_at: str):
    """
    Track when a position was opened (entry time).
    
    Args:
        ticker: Stock symbol
        order_id: Alpaca order ID
        notional: Dollar amount invested
        submitted_at: Timestamp when order was submitted
    """
    tracking = _load_position_tracking()
    
    tracking["positions"][ticker] = {
        "entry_time": submitted_at,
        "order_id": order_id,
        "notional": notional,
        "tracked_at": datetime.now(timezone.utc).isoformat()
    }
    
    _save_position_tracking(tracking)
    log.info(f"📍 Tracking entry for {ticker} at {submitted_at}")


def remove_position_tracking(ticker: str):
    """
    Remove position tracking when position is closed.
    
    Args:
        ticker: Stock symbol to remove
    """
    tracking = _load_position_tracking()
    
    if ticker in tracking["positions"]:
        del tracking["positions"][ticker]
        _save_position_tracking(tracking)
        log.info(f"🗑️  Removed tracking for {ticker}")


def get_position_entry_time(ticker: str) -> Optional[datetime]:
    """
    Get the entry time for a position.
    
    Args:
        ticker: Stock symbol
    
    Returns:
        datetime object or None if not tracked
    """
    tracking = _load_position_tracking()
    
    if ticker in tracking["positions"]:
        entry_time_str = tracking["positions"][ticker]["entry_time"]
        try:
            return datetime.fromisoformat(entry_time_str.replace('+00:00', '+00:00'))
        except Exception as e:
            log.error(f"Failed to parse entry time for {ticker}: {e}")
            return None
    
    return None


def execute_orders(signals: List[Dict], capital: float, max_alloc_per_trade: float, paper: bool = True) -> Dict:
    """
    Execute real trades on Alpaca based on signals.
    
    Args:
        signals: List of trading signals with ticker, action, etc.
        capital: Total capital available
        max_alloc_per_trade: Maximum allocation per trade (as fraction)
        paper: Use paper trading if True, live trading if False
    
    Returns:
        Dict with executed orders and remaining cash
    """
    client = get_alpaca_client(paper=paper)
    if not client:
        log.error("Cannot execute orders without Alpaca connection")
        return {"orders": [], "cash_left": capital, "error": "No Alpaca connection"}
    
    try:
        account = client.get_account()
        buying_power = float(account.buying_power)
        cash = min(capital, buying_power)  # Don't exceed buying power
    except Exception as e:
        log.error(f"Failed to get account info: {e}")
        return {"orders": [], "cash_left": capital, "error": str(e)}
    
    executed_orders = []
    
    for signal in signals:
        ticker = signal['ticker']
        action = signal['action'].upper()
        
        # Calculate allocation
        alloc = min(cash, capital * max_alloc_per_trade)
        
        if alloc <= 0:
            log.warning(f"Insufficient funds for {ticker}, skipping")
            continue
        
        try:
            # Get current price (from signal or fetch latest)
            # For now, we'll use notional orders and let Alpaca determine qty
            
            # Prepare order
            side = OrderSide.BUY if action == "BUY" else OrderSide.SELL
            
            order_request = MarketOrderRequest(
                symbol=ticker,
                notional=alloc,  # Order by dollar amount
                side=side,
                time_in_force=TimeInForce.DAY
            )
            
            # Submit order
            order = client.submit_order(order_request)
            
            log.info(f"✅ Order submitted: {action} ${alloc:.2f} of {ticker} (Order ID: {order.id})")
            
            executed_orders.append({
                "ticker": ticker,
                "action": action,
                "notional": round(alloc, 2),
                "order_id": str(order.id),
                "status": order.status,
                "submitted_at": str(order.submitted_at)
            })
            
            # Track entry time for BUY orders
            if action == "BUY":
                track_position_entry(
                    ticker=ticker,
                    order_id=str(order.id),
                    notional=round(alloc, 2),
                    submitted_at=str(order.submitted_at)
                )
            
            cash -= alloc
            
        except Exception as e:
            log.error(f"Failed to execute order for {ticker}: {e}")
            continue
    
    return {
        "orders": executed_orders,
        "cash_left": round(cash, 2),
        "executed_count": len(executed_orders)
    }


def get_account_summary(paper: bool = True) -> Optional[Dict]:
    """
    Get current account summary from Alpaca.
    
    Returns:
        Dict with account details or None
    """
    client = get_alpaca_client(paper=paper)
    if not client:
        return None
    
    try:
        account = client.get_account()
        positions = client.get_all_positions()
        
        return {
            "status": account.status,
            "cash": float(account.cash),
            "portfolio_value": float(account.portfolio_value),
            "buying_power": float(account.buying_power),
            "equity": float(account.equity),
            "num_positions": len(positions),
            "positions": [
                {
                    "symbol": pos.symbol,
                    "qty": float(pos.qty),
                    "market_value": float(pos.market_value),
                    "unrealized_pl": float(pos.unrealized_pl)
                }
                for pos in positions
            ]
        }
    except Exception as e:
        log.error(f"Failed to get account summary: {e}")
        return None


def close_all_positions(paper: bool = True) -> bool:
    """
    Close all open positions (emergency liquidation).
    
    Returns:
        True if successful, False otherwise
    """
    client = get_alpaca_client(paper=paper)
    if not client:
        return False
    
    try:
        client.close_all_positions(cancel_orders=True)
        log.info("✅ All positions closed successfully")
        return True
    except Exception as e:
        log.error(f"Failed to close positions: {e}")
        return False


def get_positions(paper: bool = True) -> List[Dict]:
    """
    Get all open positions.
    
    Returns:
        List of position dictionaries with details
    """
    client = get_alpaca_client(paper=paper)
    if not client:
        return []
    
    try:
        positions = client.get_all_positions()
        
        position_list = []
        for pos in positions:
            position_list.append({
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'avg_entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'market_value': float(pos.market_value),
                'unrealized_pl': float(pos.unrealized_pl),
                'unrealized_plpc': float(pos.unrealized_plpc),
                'side': pos.side
            })
        
        return position_list
    except Exception as e:
        log.error(f"Failed to get positions: {e}")
        return []

