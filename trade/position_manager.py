"""
Position Manager - Handles swing trading hold periods and exits
"""
from typing import Dict, List
from datetime import datetime, timedelta
from trade.alpaca_broker import get_alpaca_client
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
                    qty = position.qty
                    
                    # Close position
                    try:
                        client.close_position(symbol)
                        log.info(f"✅ Closed {symbol} position ({qty} shares) - Reason: {reason}")
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




