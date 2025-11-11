"""
Live Broker Integration Module

⚠️  WARNING: THIS MODULE EXECUTES REAL TRADES WITH REAL MONEY ⚠️

Only enable after completing all safety checks in LIVE_TRADING_PLAN.md
"""

import os
from typing import List, Dict, Optional
from datetime import datetime
from utils.logger import get_logger

log = get_logger("live_broker")


class LiveBroker:
    """
    Base class for live broker integration
    
    SAFETY FEATURES:
    - Pre-trade validation
    - Circuit breakers
    - Kill switch
    - Position limits
    - Real-time monitoring
    """
    
    def __init__(self, config: Dict):
        """
        Initialize broker connection
        
        Args:
            config: Configuration dictionary with broker settings
        """
        self.config = config
        self.live_trading_enabled = config.get('live_trading', {}).get('enabled', False)
        self.paper_mode = config.get('live_trading', {}).get('paper_mode', True)
        self.account_number = config.get('live_trading', {}).get('account_number', '')
        
        # Safety settings
        self.daily_loss_limit = config.get('live_trading', {}).get('daily_loss_limit_pct', 0.03)
        self.max_trades_per_day = config.get('live_trading', {}).get('max_trades_per_day', 5)
        self.max_consecutive_losses = config.get('live_trading', {}).get('max_consecutive_losses', 3)
        
        # State tracking
        self.trades_today = 0
        self.consecutive_losses = 0
        self.daily_pnl = 0.0
        self.positions = {}
        
        # Kill switch check
        if self._check_kill_switch():
            log.critical("🚨 KILL SWITCH ACTIVATED - Trading disabled!")
            self.live_trading_enabled = False
        
        if self.live_trading_enabled and not self.paper_mode:
            log.warning("⚠️  LIVE TRADING MODE ENABLED - REAL MONEY AT RISK")
        elif self.live_trading_enabled and self.paper_mode:
            log.info("📄 Paper trading mode enabled")
        else:
            log.info("✅ Live trading disabled (simulation only)")
    
    def _check_kill_switch(self) -> bool:
        """Check if emergency kill switch file exists"""
        kill_switch_path = os.path.join(os.path.dirname(__file__), '..', 'STOP_TRADING.txt')
        return os.path.exists(kill_switch_path)
    
    def check_circuit_breakers(self) -> tuple[bool, str]:
        """
        Check all circuit breakers before allowing trade
        
        Returns:
            (can_trade, reason)
        """
        # Kill switch
        if self._check_kill_switch():
            return False, "Kill switch activated"
        
        # Daily loss limit
        if self.daily_pnl < -(self.daily_loss_limit * self.get_account_value()):
            return False, f"Daily loss limit exceeded: {self.daily_pnl:.2f}"
        
        # Max trades per day
        if self.trades_today >= self.max_trades_per_day:
            return False, f"Max trades per day reached: {self.trades_today}/{self.max_trades_per_day}"
        
        # Consecutive losses
        if self.consecutive_losses >= self.max_consecutive_losses:
            return False, f"Max consecutive losses reached: {self.consecutive_losses}"
        
        return True, "All checks passed"
    
    def pre_trade_validation(self, signal: Dict) -> tuple[bool, str]:
        """
        Validate trade before execution
        
        Args:
            signal: Trading signal dictionary
            
        Returns:
            (is_valid, reason)
        """
        # Check circuit breakers
        can_trade, reason = self.check_circuit_breakers()
        if not can_trade:
            return False, reason
        
        # Validate signal structure
        required_keys = ['ticker', 'action', 'strength']
        if not all(key in signal for key in required_keys):
            return False, "Invalid signal structure"
        
        # Check market hours
        if not self.is_market_open():
            return False, "Market is closed"
        
        # Check buying power
        if not self.has_sufficient_buying_power(signal):
            return False, "Insufficient buying power"
        
        # Check position limits
        if len(self.positions) >= self.config['risk']['max_positions']:
            return False, f"Max positions reached: {len(self.positions)}"
        
        return True, "Validation passed"
    
    def place_order(self, signal: Dict) -> Optional[Dict]:
        """
        Place order with broker
        
        ⚠️  THIS EXECUTES REAL TRADES ⚠️
        
        Args:
            signal: Trading signal
            
        Returns:
            Order confirmation or None if failed
        """
        if not self.live_trading_enabled:
            log.info(f"📋 Simulated order: {signal['ticker']} {signal['action']}")
            return None
        
        # Pre-trade validation
        is_valid, reason = self.pre_trade_validation(signal)
        if not is_valid:
            log.warning(f"⚠️  Trade validation failed: {reason}")
            return None
        
        log.info(f"🚀 Placing order: {signal['ticker']} {signal['action']}")
        
        try:
            # This method should be overridden by specific broker implementation
            order = self._execute_order(signal)
            
            if order:
                self.trades_today += 1
                log.info(f"✅ Order placed: {order}")
                self._send_alert(f"Trade executed: {signal['ticker']} {signal['action']}")
            
            return order
            
        except Exception as e:
            log.error(f"❌ Order placement failed: {e}", exc_info=True)
            self._send_alert(f"ERROR: Order failed for {signal['ticker']}: {str(e)}")
            return None
    
    def _execute_order(self, signal: Dict) -> Optional[Dict]:
        """
        Execute order with specific broker API
        
        MUST BE OVERRIDDEN BY SUBCLASS (Alpaca, IB, etc.)
        """
        raise NotImplementedError("Subclass must implement _execute_order()")
    
    def get_account_value(self) -> float:
        """Get current account value"""
        raise NotImplementedError("Subclass must implement get_account_value()")
    
    def has_sufficient_buying_power(self, signal: Dict) -> bool:
        """Check if sufficient buying power for trade"""
        raise NotImplementedError("Subclass must implement has_sufficient_buying_power()")
    
    def is_market_open(self) -> bool:
        """Check if market is currently open"""
        # Simple check - can be enhanced
        now = datetime.now()
        if now.weekday() >= 5:  # Weekend
            return False
        if now.hour < 9 or (now.hour == 9 and now.minute < 30):  # Before 9:30 AM
            return False
        if now.hour >= 16:  # After 4:00 PM
            return False
        return True
    
    def get_positions(self) -> Dict:
        """Get all open positions"""
        raise NotImplementedError("Subclass must implement get_positions()")
    
    def close_position(self, ticker: str) -> bool:
        """Close position for ticker"""
        raise NotImplementedError("Subclass must implement close_position()")
    
    def close_all_positions(self) -> int:
        """Close all open positions (emergency)"""
        log.warning("🚨 CLOSING ALL POSITIONS")
        count = 0
        for ticker in list(self.positions.keys()):
            if self.close_position(ticker):
                count += 1
        return count
    
    def _send_alert(self, message: str):
        """Send alert via email/SMS/Discord"""
        log.info(f"📢 ALERT: {message}")
        # TODO: Implement email/SMS/Discord notifications
    
    def update_daily_stats(self):
        """Update daily P&L and reset counters"""
        log.info(f"📊 Daily Stats - Trades: {self.trades_today}, P&L: ${self.daily_pnl:.2f}")
        self.trades_today = 0
        self.daily_pnl = 0.0


class AlpacaBroker(LiveBroker):
    """
    Alpaca broker integration
    
    Get API keys from: https://app.alpaca.markets/
    """
    
    def __init__(self, config: Dict):
        super().__init__(config)
        
        if self.live_trading_enabled:
            try:
                import alpaca_trade_api as tradeapi
                
                api_key = os.getenv('ALPACA_API_KEY')
                api_secret = os.getenv('ALPACA_API_SECRET')
                base_url = 'https://paper-api.alpaca.markets' if self.paper_mode else 'https://api.alpaca.markets'
                
                if not api_key or not api_secret:
                    raise ValueError("Alpaca API credentials not found in environment")
                
                self.api = tradeapi.REST(api_key, api_secret, base_url, api_version='v2')
                log.info(f"✅ Connected to Alpaca ({'paper' if self.paper_mode else 'live'} account)")
                
                # Verify account
                account = self.api.get_account()
                log.info(f"Account: {account.account_number}")
                log.info(f"Buying power: ${float(account.buying_power):.2f}")
                
            except ImportError:
                log.error("❌ alpaca-trade-api not installed. Run: pip install alpaca-trade-api")
                self.live_trading_enabled = False
            except Exception as e:
                log.error(f"❌ Failed to connect to Alpaca: {e}")
                self.live_trading_enabled = False
    
    def _execute_order(self, signal: Dict) -> Optional[Dict]:
        """Execute order on Alpaca"""
        try:
            ticker = signal['ticker']
            action = signal['action'].lower()  # 'buy' or 'sell'
            
            # Calculate quantity based on allocation
            account = self.api.get_account()
            buying_power = float(account.buying_power)
            max_alloc = buying_power * self.config['risk']['max_alloc_per_trade']
            
            # Get current price
            bars = self.api.get_latest_bar(ticker)
            price = float(bars.c)
            
            qty = int(max_alloc / price)
            
            if qty <= 0:
                log.warning(f"Quantity too small for {ticker}")
                return None
            
            # Place market order
            order = self.api.submit_order(
                symbol=ticker,
                qty=qty,
                side=action,
                type='market',
                time_in_force='day'
            )
            
            return {
                'order_id': order.id,
                'ticker': ticker,
                'action': action,
                'qty': qty,
                'price': price,
                'status': order.status
            }
            
        except Exception as e:
            log.error(f"Alpaca order failed: {e}")
            return None
    
    def get_account_value(self) -> float:
        try:
            account = self.api.get_account()
            return float(account.equity)
        except:
            return 0.0
    
    def has_sufficient_buying_power(self, signal: Dict) -> bool:
        try:
            account = self.api.get_account()
            buying_power = float(account.buying_power)
            required = buying_power * self.config['risk']['max_alloc_per_trade']
            return buying_power >= required
        except:
            return False
    
    def get_positions(self) -> Dict:
        try:
            positions = self.api.list_positions()
            return {p.symbol: p for p in positions}
        except:
            return {}
    
    def close_position(self, ticker: str) -> bool:
        try:
            self.api.close_position(ticker)
            log.info(f"✅ Closed position: {ticker}")
            return True
        except Exception as e:
            log.error(f"Failed to close {ticker}: {e}")
            return False


def create_broker(config: Dict) -> LiveBroker:
    """
    Factory function to create appropriate broker instance
    """
    broker_name = config.get('live_trading', {}).get('broker', '').lower()
    
    if broker_name == 'alpaca':
        return AlpacaBroker(config)
    else:
        log.warning(f"Unknown broker: {broker_name}, using simulation")
        return LiveBroker(config)

