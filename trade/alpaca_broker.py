"""
Alpaca broker integration for executing real trades.
Supports both paper trading and live trading.
"""
import os
from typing import List, Dict, Optional
from dotenv import load_dotenv
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce
from utils.logger import get_logger

load_dotenv()
log = get_logger("alpaca_broker")


def get_latest_price(symbol: str) -> Optional[float]:
    """Best-effort latest trade price for marketable-limit pricing. Returns None on failure."""
    try:
        from alpaca.data.historical import StockHistoricalDataClient
        from alpaca.data.requests import StockLatestTradeRequest

        key = sanitize_alpaca_credential(
            os.getenv("ALPACA_PAPER_API_KEY") or os.getenv("ALPACA_LIVE_API_KEY") or os.getenv("ALPACA_API_KEY")
        )
        secret = sanitize_alpaca_credential(
            os.getenv("ALPACA_PAPER_API_SECRET") or os.getenv("ALPACA_LIVE_API_SECRET") or os.getenv("ALPACA_API_SECRET")
        )
        if not key or not secret:
            return None
        data_client = StockHistoricalDataClient(key, secret)
        resp = data_client.get_stock_latest_trade(StockLatestTradeRequest(symbol_or_symbols=symbol))
        return float(resp[symbol].price)
    except Exception as e:
        log.warning(f"Could not fetch latest price for {symbol}: {e}")
        return None


def is_market_open(client: TradingClient) -> Optional[bool]:
    """True/False if the US market is open now; None if the check failed."""
    try:
        return bool(client.get_clock().is_open)
    except Exception as e:
        log.warning(f"Market clock check failed: {e}")
        return None


def sanitize_alpaca_credential(value: Optional[str]) -> Optional[str]:
    """
    Strip whitespace and non-ASCII characters from API key/secret.
    Alpaca keys are ASCII; pasted Unicode (arrows, smart quotes) breaks HTTP headers (latin-1).
    """
    if not value:
        return None
    s = value.strip()
    cleaned = "".join(c for c in s if ord(c) < 128)
    if len(cleaned) != len(s):
        log.warning(
            "Removed non-ASCII characters from an Alpaca credential — "
            "re-paste keys in GitHub Secrets if connection still fails (ASCII only)."
        )
    return cleaned if cleaned else None


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
    
    api_key = sanitize_alpaca_credential(api_key)
    api_secret = sanitize_alpaca_credential(api_secret)
    
    if not api_key or not api_secret:
        log.error(f"Alpaca {'paper' if paper else 'LIVE'} credentials missing in .env file")
        return None
    
    try:
        client = TradingClient(api_key, api_secret, paper=paper)
        account = client.get_account()
        acct_id = getattr(account, "account_number", None) or getattr(account, "id", "?")
        log.info(f"Connected to Alpaca ({'PAPER' if paper else 'LIVE'} trading), account id: {acct_id}")
        log.info(f"Account status: {account.status}, Buying power: ${float(account.buying_power):.2f}")
        return client
    except Exception as e:
        log.error(f"Failed to connect to Alpaca: {e}")
        return None


def _submit_buy(client: TradingClient, ticker: str, alloc: float,
                order_type: str, slippage_pct: float, extended_hours: bool) -> Dict:
    """Submit one BUY using a marketable limit (caps slippage) with fallback to market."""
    if order_type == "limit":
        price = get_latest_price(ticker)
        if price and price > 0:
            limit_price = round(price * (1 + max(slippage_pct, 0.0)), 2)
            req = LimitOrderRequest(
                symbol=ticker, notional=round(alloc, 2), side=OrderSide.BUY,
                time_in_force=TimeInForce.DAY, limit_price=limit_price,
                extended_hours=extended_hours,
            )
            order = client.submit_order(req)
            log.info(f"✅ LIMIT BUY ${alloc:.2f} {ticker} @ <= ${limit_price} (id {order.id})")
            return {"order": order, "order_type": "limit", "limit_price": limit_price}
        log.warning(f"{ticker}: no price for limit order, falling back to market")
    req = MarketOrderRequest(
        symbol=ticker, notional=round(alloc, 2), side=OrderSide.BUY, time_in_force=TimeInForce.DAY,
    )
    order = client.submit_order(req)
    log.info(f"✅ MARKET BUY ${alloc:.2f} {ticker} (id {order.id})")
    return {"order": order, "order_type": "market", "limit_price": None}


def execute_orders(
    signals: List[Dict],
    capital: float,
    max_alloc_per_trade: float,
    paper: bool = True,
    min_order_size: float = 1.0,
    max_positions: int = 3,
    order_type: str = "limit",
    limit_slippage_pct: float = 0.002,
    respect_market_hours: bool = True,
    extended_hours: bool = False,
    skip_if_already_held: bool = True,
    size_from_equity: bool = True,
) -> Dict:
    """
    Execute BUY signals on Alpaca with best-execution guards:
      - size positions off LIVE account equity (compounds with wins) when size_from_equity,
      - skip when the market is closed (unless extended_hours),
      - never exceed max_positions or pyramid into a held name,
      - marketable LIMIT orders to cap slippage (fallback to market).
    """
    client = get_alpaca_client(paper=paper)
    if not client:
        log.error("Cannot execute orders without Alpaca connection")
        return {"orders": [], "cash_left": capital, "error": "No Alpaca connection"}

    # Guard: only trade when the market is open (closed-market fills are illiquid/queued).
    if respect_market_hours and not extended_hours:
        open_now = is_market_open(client)
        if open_now is False:
            log.info("⏸️  Market closed — skipping order execution this run")
            return {"orders": [], "cash_left": capital, "executed_count": 0, "skipped": "market_closed"}

    try:
        account = client.get_account()
        buying_power = float(account.buying_power)
        equity = float(account.equity)
        # Compounding: size off live equity so the budget grows with wins (and shrinks on losses).
        base_capital = equity if size_from_equity else capital
        cash = min(base_capital, buying_power)
        log.info(
            f"💼 Sizing base: ${base_capital:.2f} "
            f"({'live equity' if size_from_equity else 'fixed config'}), "
            f"buying power ${buying_power:.2f}"
        )
    except Exception as e:
        log.error(f"Failed to get account info: {e}")
        return {"orders": [], "cash_left": capital, "error": str(e)}

    # Position-aware sizing: how many new names can we open, and which are already held?
    try:
        held = {p.symbol for p in client.get_all_positions()}
    except Exception as e:
        log.warning(f"Could not list positions ({e}); assuming none held")
        held = set()
    open_slots = max(0, max_positions - len(held))

    # Only BUYs flow through here (exits are handled by the position manager).
    buy_signals = [s for s in signals if str(s.get('action', '')).upper() == 'BUY']
    buy_signals.sort(key=lambda s: s.get('strength', 0), reverse=True)

    executed_orders = []
    per_trade = base_capital * max_alloc_per_trade

    for signal in buy_signals:
        ticker = signal['ticker']
        if skip_if_already_held and ticker in held:
            log.info(f"↩️  Skipping {ticker}: already held (no pyramiding)")
            continue
        if open_slots <= 0:
            log.info(f"🧮 Max positions reached ({max_positions}); skipping remaining signals")
            break
        alloc = min(cash, per_trade)
        if alloc < min_order_size:
            log.warning(f"Insufficient funds for {ticker} (${alloc:.2f} < ${min_order_size:.2f})")
            continue
        try:
            res = _submit_buy(client, ticker, alloc, order_type, limit_slippage_pct, extended_hours)
            order = res["order"]
            executed_orders.append({
                "ticker": ticker,
                "action": "BUY",
                "notional": round(alloc, 2),
                "order_id": str(order.id),
                "status": str(order.status),
                "order_type": res["order_type"],
                "limit_price": res["limit_price"],
                "submitted_at": str(order.submitted_at),
            })
            cash -= alloc
            held.add(ticker)
            open_slots -= 1
        except Exception as e:
            log.error(f"Failed to execute order for {ticker}: {e}")
            continue

    return {
        "orders": executed_orders,
        "cash_left": round(cash, 2),
        "executed_count": len(executed_orders),
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

