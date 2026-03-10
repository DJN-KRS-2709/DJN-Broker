"""
Position Manager - Handles swing trading hold periods and exits
"""
import os
import json
from typing import Dict, List
from datetime import datetime, timedelta
from trade.alpaca_broker import get_alpaca_client
from utils.logger import get_logger

log = get_logger("position_manager")

# File to track closed trades
CLOSED_TRADES_FILE = "storage/learning/closed_trades.json"


class PositionManager:
    """
    Manages swing trading positions with time-based rules.
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.trading_style = config.get('trading_style', 'swing')
        self.min_hold_hours = config.get('min_hold_hours', 24)
        self.max_hold_days = config.get('max_hold_days', 7)
        self.stop_loss_pct = config['risk']['stop_loss_pct']
        self.take_profit_pct = config['risk']['take_profit_pct']
    
    def should_close_position(self, position: Dict, paper: bool = True) -> tuple[bool, str]:
        """
        Determine if a position should be closed.
        
        Returns:
            (should_close: bool, reason: str)
        """
        symbol = position['symbol']
        qty = float(position['qty'])
        avg_entry = float(position['avg_entry_price'])
        current_price = float(position['current_price'])
        unrealized_pl_pct = float(position['unrealized_plpc'])
        
        # Calculate hold time
        # Note: Alpaca doesn't give us exact entry time in position object
        # We'll estimate based on when we first see it
        # For proper implementation, store entry times in learning/trade_memory
        
        # Check take profit
        if unrealized_pl_pct >= self.take_profit_pct:
            log.info(f"✅ {symbol}: Take profit hit ({unrealized_pl_pct:.1%} >= {self.take_profit_pct:.1%})")
            return True, "take_profit"
        
        # Check stop loss
        if unrealized_pl_pct <= -self.stop_loss_pct:
            log.info(f"🛑 {symbol}: Stop loss hit ({unrealized_pl_pct:.1%} <= -{self.stop_loss_pct:.1%})")
            return True, "stop_loss"
        
        # For swing trading, we'd check max hold time here
        # This requires tracking entry times in our learning system
        # For now, Alpaca's stops will handle exits
        
        return False, "hold"
    
    def manage_positions(self, paper: bool = True):
        """
        Check all open positions and close if needed.
        """
        client = get_alpaca_client(paper=paper)
        if not client:
            log.error("Cannot manage positions without Alpaca connection")
            return
        
        try:
            positions = client.get_all_positions()
            
            if not positions:
                log.info("📊 No open positions to manage")
                return
            
            log.info(f"📊 Managing {len(positions)} open positions...")
            
            for position in positions:
                should_close, reason = self.should_close_position(position.__dict__, paper)
                
                if should_close:
                    symbol = position.symbol
                    qty = float(position.qty)
                    entry_price = float(position.avg_entry_price)
                    exit_price = float(position.current_price)
                    realized_pnl = float(position.unrealized_pl)
                    realized_pnl_pct = float(position.unrealized_plpc)
                    market_value = float(position.market_value)
                    
                    # Close position
                    try:
                        client.close_position(symbol)
                        log.info(f"✅ Closed {symbol} position ({qty} shares) - Reason: {reason}")
                        
                        # Record the closed trade
                        self._record_closed_trade(
                            symbol=symbol,
                            qty=qty,
                            entry_price=entry_price,
                            exit_price=exit_price,
                            realized_pnl=realized_pnl,
                            realized_pnl_pct=realized_pnl_pct,
                            market_value=market_value,
                            reason=reason
                        )
                        
                    except Exception as e:
                        log.error(f"Failed to close {symbol}: {e}")
                else:
                    symbol = position.symbol
                    pnl = float(position.unrealized_pl)
                    pnl_pct = float(position.unrealized_plpc)
                    
                    emoji = "🟢" if pnl >= 0 else "🔴"
                    log.info(f"  {emoji} {symbol}: ${pnl:,.2f} ({pnl_pct:+.1%}) - Holding")
        
        except Exception as e:
            log.error(f"Error managing positions: {e}")
    
    def _record_closed_trade(self, symbol: str, qty: float, entry_price: float, 
                             exit_price: float, realized_pnl: float, 
                             realized_pnl_pct: float, market_value: float, reason: str):
        """Record a closed trade to the closed_trades.json file."""
        try:
            # Load existing closed trades
            closed_trades = []
            if os.path.exists(CLOSED_TRADES_FILE):
                with open(CLOSED_TRADES_FILE, 'r') as f:
                    closed_trades = json.load(f)
            
            # Create closed trade record
            trading_mode = self.config.get('trading_mode', 'swing')
            closed_trade = {
                'symbol': symbol,
                'qty': qty,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'realized_pnl': realized_pnl,
                'realized_pnl_pct': realized_pnl_pct,
                'market_value': market_value,
                'reason': reason,  # 'take_profit' or 'stop_loss'
                'is_winner': realized_pnl > 0,
                'trading_mode': trading_mode,  # 'swing' or 'micro' for performance comparison
                'closed_at': datetime.now().isoformat(),
                'date': datetime.now().strftime('%Y-%m-%d')
            }
            
            closed_trades.append(closed_trade)
            
            # Save back to file
            os.makedirs(os.path.dirname(CLOSED_TRADES_FILE), exist_ok=True)
            with open(CLOSED_TRADES_FILE, 'w') as f:
                json.dump(closed_trades, f, indent=2)
            
            emoji = "🎯" if reason == "take_profit" else "🛑"
            result = "WIN" if realized_pnl > 0 else "LOSS"
            log.info(f"{emoji} CLOSED TRADE RECORDED: {symbol} {result} ${realized_pnl:+.2f} ({realized_pnl_pct:+.1%})")
            
        except Exception as e:
            log.error(f"Failed to record closed trade: {e}")
    
    def get_position_summary(self, paper: bool = True) -> Dict:
        """
        Get summary of all positions.
        """
        client = get_alpaca_client(paper=paper)
        if not client:
            return {}
        
        try:
            positions = client.get_all_positions()
            
            total_value = 0.0
            total_pnl = 0.0
            winners = 0
            losers = 0
            
            for pos in positions:
                market_value = float(pos.market_value)
                unrealized_pl = float(pos.unrealized_pl)
                
                total_value += market_value
                total_pnl += unrealized_pl
                
                if unrealized_pl > 0:
                    winners += 1
                elif unrealized_pl < 0:
                    losers += 1
            
            return {
                'num_positions': len(positions),
                'total_value': total_value,
                'total_pnl': total_pnl,
                'winners': winners,
                'losers': losers,
                'win_rate': winners / len(positions) if positions else 0
            }
        
        except Exception as e:
            log.error(f"Error getting position summary: {e}")
            return {}


# Helper function for main.py
def manage_swing_positions(config: Dict, paper: bool = True):
    """
    Manage positions for both swing and micro/day trading modes.
    TP/SL thresholds come from config (micro mode overrides applied in main).
    """
    manager = PositionManager(config)
    manager.manage_positions(paper=paper)

    summary = manager.get_position_summary(paper=paper)
    if summary:
        log.info(f"📊 Position Summary: {summary['num_positions']} open, "
                f"${summary['total_pnl']:.2f} P&L, "
                f"{summary['win_rate']:.0%} winning")


def get_closed_trades_summary() -> Dict:
    """
    Get summary of all closed trades for win rate calculation.
    
    Returns:
        Dict with closed trade statistics
    """
    try:
        if not os.path.exists(CLOSED_TRADES_FILE):
            return {
                'total_closed': 0,
                'winners': 0,
                'losers': 0,
                'win_rate': 0.0,
                'total_realized_pnl': 0.0,
                'avg_winner': 0.0,
                'avg_loser': 0.0,
                'take_profits': 0,
                'stop_losses': 0
            }
        
        with open(CLOSED_TRADES_FILE, 'r') as f:
            closed_trades = json.load(f)
        
        if not closed_trades:
            return {
                'total_closed': 0,
                'winners': 0,
                'losers': 0,
                'win_rate': 0.0,
                'total_realized_pnl': 0.0,
                'avg_winner': 0.0,
                'avg_loser': 0.0,
                'take_profits': 0,
                'stop_losses': 0
            }
        
        winners = [t for t in closed_trades if t.get('is_winner', False)]
        losers = [t for t in closed_trades if not t.get('is_winner', True)]
        take_profits = [t for t in closed_trades if t.get('reason') == 'take_profit']
        stop_losses = [t for t in closed_trades if t.get('reason') == 'stop_loss']
        
        total_pnl = sum(t.get('realized_pnl', 0) for t in closed_trades)
        avg_winner = sum(t.get('realized_pnl', 0) for t in winners) / len(winners) if winners else 0
        avg_loser = sum(t.get('realized_pnl', 0) for t in losers) / len(losers) if losers else 0
        
        win_rate = len(winners) / len(closed_trades) if closed_trades else 0.0
        
        return {
            'total_closed': len(closed_trades),
            'winners': len(winners),
            'losers': len(losers),
            'win_rate': win_rate,
            'total_realized_pnl': total_pnl,
            'avg_winner': avg_winner,
            'avg_loser': avg_loser,
            'take_profits': len(take_profits),
            'stop_losses': len(stop_losses),
            'trades': closed_trades  # Include raw data for detailed analysis
        }
        
    except Exception as e:
        log.error(f"Failed to get closed trades summary: {e}")
        return {
            'total_closed': 0,
            'winners': 0,
            'losers': 0,
            'win_rate': 0.0,
            'total_realized_pnl': 0.0,
            'error': str(e)
        }


def get_recent_closed_trades(days: int = 7) -> List[Dict]:
    """Get closed trades from the last N days."""
    try:
        if not os.path.exists(CLOSED_TRADES_FILE):
            return []
        
        with open(CLOSED_TRADES_FILE, 'r') as f:
            closed_trades = json.load(f)
        
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        recent = [t for t in closed_trades if t.get('closed_at', '') >= cutoff]
        
        return recent
        
    except Exception as e:
        log.error(f"Failed to get recent closed trades: {e}")
        return []




