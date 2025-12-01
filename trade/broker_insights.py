"""
Alpaca Broker API - Advanced Portfolio Insights & Analytics

The Broker API provides enhanced features:
- Detailed portfolio analytics
- Advanced account insights
- Fractional shares support
- Enhanced reporting
- Better position tracking
"""

import os
import requests
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
from utils.logger import get_logger

load_dotenv()
log = get_logger("broker_insights")


class BrokerInsights:
    """
    Enhanced portfolio insights using Alpaca Broker API.
    Provides advanced analytics beyond standard Trading API.
    """
    
    def __init__(self, sandbox: bool = True):
        """
        Initialize Broker API client.
        
        Args:
            sandbox: Use sandbox (paper trading) endpoint if True
        """
        self.base_url = os.getenv('ALPACA_BROKER_SANDBOX_URL', 'https://broker-api.sandbox.alpaca.markets')
        self.client_id = os.getenv('ALPACA_BROKER_CLIENT_ID')
        self.client_secret = os.getenv('ALPACA_BROKER_CLIENT_SECRET')
        
        if not self.client_id or not self.client_secret:
            raise ValueError("Broker API credentials not found in .env file")
        
        self.headers = {
            'Authorization': f'Basic {self._encode_credentials()}',
            'Content-Type': 'application/json'
        }
        
        log.info(f"Initialized Broker API client (sandbox={sandbox})")
    
    def _encode_credentials(self) -> str:
        """Encode client credentials for Basic Auth."""
        import base64
        credentials = f"{self.client_id}:{self.client_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return encoded
    
    def get_account_insights(self, account_id: Optional[str] = None) -> Dict:
        """
        Get advanced account insights and analytics.
        
        Args:
            account_id: Alpaca account ID (auto-detected if None)
        
        Returns:
            Dict with account insights, analytics, and performance metrics
        """
        try:
            # If no account_id, get from Trading API
            if not account_id:
                account_id = self._get_account_id()
            
            # Get account details
            url = f"{self.base_url}/v1/accounts/{account_id}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            account = response.json()
            
            # Get portfolio history
            history_url = f"{self.base_url}/v1/accounts/{account_id}/portfolio/history"
            params = {
                'period': '1M',
                'timeframe': '1D'
            }
            history_response = requests.get(history_url, headers=self.headers, params=params, timeout=10)
            
            insights = {
                'account_id': account_id,
                'account_number': account.get('account_number'),
                'status': account.get('status'),
                'portfolio_value': float(account.get('equity', 0)),
                'buying_power': float(account.get('buying_power', 0)),
                'cash': float(account.get('cash', 0)),
                'daytrade_count': account.get('daytrade_count', 0),
                'pattern_day_trader': account.get('pattern_day_trader', False),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add portfolio history if available
            if history_response.status_code == 200:
                history = history_response.json()
                insights['portfolio_history'] = history
                
                # Calculate performance metrics
                if history.get('equity'):
                    equity_values = history['equity']
                    if len(equity_values) > 1:
                        start_value = equity_values[0]
                        end_value = equity_values[-1]
                        insights['monthly_return'] = ((end_value - start_value) / start_value) * 100
            
            log.info(f"Retrieved account insights for {account_id}")
            return insights
            
        except Exception as e:
            log.error(f"Failed to get account insights: {e}")
            return {}
    
    def get_portfolio_analytics(self, account_id: Optional[str] = None) -> Dict:
        """
        Get detailed portfolio analytics including risk metrics.
        
        Returns:
            Dict with portfolio composition, risk metrics, performance
        """
        try:
            if not account_id:
                account_id = self._get_account_id()
            
            # Get positions
            positions_url = f"{self.base_url}/v1/accounts/{account_id}/positions"
            response = requests.get(positions_url, headers=self.headers, timeout=10)
            response.raise_for_status()
            positions = response.json()
            
            # Calculate analytics
            total_value = sum(float(p.get('market_value', 0)) for p in positions)
            total_pnl = sum(float(p.get('unrealized_pl', 0)) for p in positions)
            
            analytics = {
                'total_positions': len(positions),
                'total_market_value': total_value,
                'total_unrealized_pnl': total_pnl,
                'positions': []
            }
            
            # Analyze each position
            for pos in positions:
                symbol = pos.get('symbol')
                market_value = float(pos.get('market_value', 0))
                unrealized_pl = float(pos.get('unrealized_pl', 0))
                unrealized_plpc = float(pos.get('unrealized_plpc', 0)) * 100
                
                position_data = {
                    'symbol': symbol,
                    'qty': float(pos.get('qty', 0)),
                    'avg_entry_price': float(pos.get('avg_entry_price', 0)),
                    'current_price': float(pos.get('current_price', 0)),
                    'market_value': market_value,
                    'unrealized_pl': unrealized_pl,
                    'unrealized_pl_percent': unrealized_plpc,
                    'portfolio_weight': (market_value / total_value * 100) if total_value > 0 else 0
                }
                
                analytics['positions'].append(position_data)
            
            # Sort by portfolio weight
            analytics['positions'].sort(key=lambda x: x['portfolio_weight'], reverse=True)
            
            log.info(f"Retrieved portfolio analytics: {len(positions)} positions, ${total_value:.2f} total value")
            return analytics
            
        except Exception as e:
            log.error(f"Failed to get portfolio analytics: {e}")
            return {}
    
    def get_trade_history(self, account_id: Optional[str] = None, days: int = 30) -> List[Dict]:
        """
        Get detailed trade history with enhanced metadata.
        
        Args:
            account_id: Alpaca account ID
            days: Number of days to look back
        
        Returns:
            List of trades with detailed information
        """
        try:
            if not account_id:
                account_id = self._get_account_id()
            
            # Calculate date range
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)
            
            # Get activities (trades, fills, etc.)
            url = f"{self.base_url}/v1/accounts/{account_id}/activities"
            params = {
                'activity_types': 'FILL',
                'after': start_date.isoformat(),
                'direction': 'desc',
                'page_size': 100
            }
            
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            activities = response.json()
            
            trades = []
            for activity in activities:
                trade = {
                    'id': activity.get('id'),
                    'symbol': activity.get('symbol'),
                    'side': activity.get('side'),
                    'qty': float(activity.get('qty', 0)),
                    'price': float(activity.get('price', 0)),
                    'transaction_time': activity.get('transaction_time'),
                    'type': activity.get('type'),
                    'order_id': activity.get('order_id')
                }
                trades.append(trade)
            
            log.info(f"Retrieved {len(trades)} trades from last {days} days")
            return trades
            
        except Exception as e:
            log.error(f"Failed to get trade history: {e}")
            return []
    
    def get_performance_summary(self, account_id: Optional[str] = None) -> Dict:
        """
        Generate comprehensive performance summary.
        
        Returns:
            Dict with win rate, P&L, best/worst trades, etc.
        """
        try:
            trades = self.get_trade_history(account_id, days=30)
            analytics = self.get_portfolio_analytics(account_id)
            
            summary = {
                'period': '30 days',
                'total_trades': len(trades),
                'total_unrealized_pnl': analytics.get('total_unrealized_pnl', 0),
                'portfolio_value': analytics.get('total_market_value', 0),
                'open_positions': analytics.get('total_positions', 0),
                'timestamp': datetime.now().isoformat()
            }
            
            # Add position summaries
            if analytics.get('positions'):
                summary['best_position'] = max(analytics['positions'], 
                                              key=lambda x: x['unrealized_pl_percent'])
                summary['worst_position'] = min(analytics['positions'], 
                                               key=lambda x: x['unrealized_pl_percent'])
                summary['largest_position'] = max(analytics['positions'], 
                                                 key=lambda x: x['portfolio_weight'])
            
            log.info(f"Generated performance summary: {len(trades)} trades, ${summary['total_unrealized_pnl']:.2f} P&L")
            return summary
            
        except Exception as e:
            log.error(f"Failed to generate performance summary: {e}")
            return {}
    
    def _get_account_id(self) -> str:
        """Get account ID from Trading API."""
        # Use Trading API to get account
        from trade.alpaca_broker import get_account_summary
        account = get_account_summary(paper=True)
        
        if not account or 'account_number' not in account:
            raise ValueError("Could not retrieve account information")
        
        return account['account_number']


def print_portfolio_report(insights: BrokerInsights):
    """
    Print a formatted portfolio report with advanced insights.
    """
    try:
        log.info("=" * 60)
        log.info("📊 ADVANCED PORTFOLIO REPORT")
        log.info("=" * 60)
        
        # Get account insights
        account = insights.get_account_insights()
        if account:
            log.info(f"Account: {account.get('account_number')}")
            log.info(f"Status: {account.get('status')}")
            log.info(f"Portfolio Value: ${account.get('portfolio_value', 0):.2f}")
            log.info(f"Buying Power: ${account.get('buying_power', 0):.2f}")
            log.info(f"Cash: ${account.get('cash', 0):.2f}")
            
            if 'monthly_return' in account:
                log.info(f"30-Day Return: {account['monthly_return']:.2f}%")
        
        log.info("")
        log.info("📈 PORTFOLIO ANALYTICS")
        log.info("-" * 60)
        
        # Get portfolio analytics
        analytics = insights.get_portfolio_analytics()
        if analytics:
            log.info(f"Total Positions: {analytics.get('total_positions', 0)}")
            log.info(f"Total Value: ${analytics.get('total_market_value', 0):.2f}")
            log.info(f"Unrealized P&L: ${analytics.get('total_unrealized_pnl', 0):.2f}")
            
            log.info("")
            log.info("Top Holdings:")
            for pos in analytics.get('positions', [])[:5]:
                log.info(f"  {pos['symbol']:6} - {pos['portfolio_weight']:.1f}% | "
                        f"P&L: ${pos['unrealized_pl']:,.2f} ({pos['unrealized_pl_percent']:+.2f}%)")
        
        log.info("")
        log.info("=" * 60)
        
    except Exception as e:
        log.error(f"Failed to print portfolio report: {e}")


if __name__ == "__main__":
    # Test Broker API insights
    insights = BrokerInsights(sandbox=True)
    print_portfolio_report(insights)
    
    # Get performance summary
    summary = insights.get_performance_summary()
    print("\n📊 Performance Summary:")
    for key, value in summary.items():
        print(f"  {key}: {value}")



