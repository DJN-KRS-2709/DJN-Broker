"""
Position Manager - Handles swing trading hold periods and exits
"""
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta, timezone
from trade.alpaca_broker import get_alpaca_client, get_position_entry_time, remove_position_tracking
from utils.logger import get_logger

log = get_logger("position_manager")


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
    
    def should_close_position(self, position: Dict, entry_time: Optional[datetime] = None, paper: bool = True) -> Tuple[bool, str]:
        """
        Determine if a position should be closed.
        
        Approach C (Hybrid): After 7 days, sell if any profit OR small loss (<-1%)
        Always check take profit and stop loss regardless of time.
        
        Args:
            position: Position dict with symbol, P&L, etc.
            entry_time: When the position was opened (datetime object)
            paper: Paper trading mode flag
        
        Returns:
            (should_close: bool, reason: str)
        """
        symbol = position['symbol']
        qty = float(position['qty'])
        avg_entry = float(position['avg_entry_price'])
        current_price = float(position['current_price'])
        unrealized_pl_pct = float(position['unrealized_plpc'])
        
        # Check take profit (any time)
        if unrealized_pl_pct >= self.take_profit_pct:
            log.info(f"✅ {symbol}: Take profit hit ({unrealized_pl_pct:.1%} >= {self.take_profit_pct:.1%})")
            return True, "take_profit"
        
        # Check stop loss (any time)
        if unrealized_pl_pct <= -self.stop_loss_pct:
            log.info(f"🛑 {symbol}: Stop loss hit ({unrealized_pl_pct:.1%} <= -{self.stop_loss_pct:.1%})")
            return True, "stop_loss"
        
        # Check max hold time (swing trading specific)
        if self.trading_style == 'swing' and entry_time:
            now = datetime.now(timezone.utc)
            hold_time = now - entry_time
            hold_days = hold_time.days
            hold_hours = hold_time.total_seconds() / 3600
            
            # Check minimum hold time first (don't sell too early)
            if hold_hours < self.min_hold_hours:
                log.debug(f"⏳ {symbol}: Below min hold time ({hold_hours:.1f}h < {self.min_hold_hours}h)")
                return False, "min_hold_not_met"
            
            # Check maximum hold time (7 days)
            if hold_days >= self.max_hold_days:
                # Approach C (Hybrid): Sell after 7 days if profit OR small loss
                if unrealized_pl_pct > 0:
                    log.info(f"⏰ {symbol}: Max hold time ({hold_days}d) + profit ({unrealized_pl_pct:.1%}) → SELL")
                    return True, "max_hold_time_profit"
                elif unrealized_pl_pct > -0.01:  # Small loss (< -1%)
                    log.info(f"⏰ {symbol}: Max hold time ({hold_days}d) + small loss ({unrealized_pl_pct:.1%}) → SELL")
                    return True, "max_hold_time_small_loss"
                else:
                    # Bigger loss, let stop-loss handle it
                    log.info(f"⏰ {symbol}: Max hold time ({hold_days}d) but loss ({unrealized_pl_pct:.1%}) → HOLD (wait for stop-loss)")
                    return False, "hold_for_stop_loss"
        
        return False, "hold"
    
    def manage_positions(self, paper: bool = True):
        """
        Check all open positions and close if needed.
        Uses entry time tracking to enforce max hold days.
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
                symbol = position.symbol
                
                # Get entry time from tracking system
                entry_time = get_position_entry_time(symbol)
                
                if entry_time:
                    hold_days = (datetime.now(timezone.utc) - entry_time).days
                    log.info(f"   📍 {symbol}: Held for {hold_days} days")
                else:
                    log.warning(f"   ⚠️  {symbol}: No entry time tracked (may be old position)")
                
                # Check if we should close
                should_close, reason = self.should_close_position(
                    position.__dict__, 
                    entry_time=entry_time,
                    paper=paper
                )
                
                if should_close:
                    qty = position.qty
                    pnl = float(position.unrealized_pl)
                    pnl_pct = float(position.unrealized_plpc)
                    
                    # Close position
                    try:
                        client.close_position(symbol)
                        log.info(f"✅ CLOSED {symbol}: {qty} shares, ${pnl:,.2f} ({pnl_pct:+.1%}) - Reason: {reason}")
                        
                        # Remove from tracking
                        remove_position_tracking(symbol)
                        
                    except Exception as e:
                        log.error(f"Failed to close {symbol}: {e}")
                else:
                    pnl = float(position.unrealized_pl)
                    pnl_pct = float(position.unrealized_plpc)
                    
                    emoji = "🟢" if pnl >= 0 else "🔴"
                    log.info(f"  {emoji} HOLDING {symbol}: ${pnl:,.2f} ({pnl_pct:+.1%})")
        
        except Exception as e:
            log.error(f"Error managing positions: {e}")
    
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
    Convenience function to manage positions from main.py
    """
    if config.get('trading_style') == 'swing':
        manager = PositionManager(config)
        manager.manage_positions(paper=paper)
        
        summary = manager.get_position_summary(paper=paper)
        if summary:
            log.info(f"📊 Position Summary: {summary['num_positions']} open, "
                    f"${summary['total_pnl']:.2f} P&L, "
                    f"{summary['win_rate']:.0%} winning")




