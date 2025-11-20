#!/usr/bin/env python3
"""
Test script for Alpaca Broker API - Advanced Insights

Shows enhanced portfolio analytics, performance metrics,
and detailed account insights beyond standard Trading API.
"""

from trade.broker_insights import BrokerInsights, print_portfolio_report
from utils.logger import get_logger

log = get_logger("broker_test")

def main():
    print("=" * 70)
    print("🔍 ALPACA BROKER API - ADVANCED INSIGHTS TEST")
    print("=" * 70)
    print()
    
    try:
        # Initialize Broker Insights
        print("📡 Connecting to Alpaca Broker API (Sandbox)...")
        insights = BrokerInsights(sandbox=True)
        print("✅ Connected successfully!")
        print()
        
        # Get account insights
        print("1️⃣ Account Insights:")
        print("-" * 70)
        account = insights.get_account_insights()
        if account:
            print(f"   Account ID: {account.get('account_number')}")
            print(f"   Status: {account.get('status')}")
            print(f"   Portfolio Value: ${account.get('portfolio_value', 0):,.2f}")
            print(f"   Cash: ${account.get('cash', 0):,.2f}")
            print(f"   Buying Power: ${account.get('buying_power', 0):,.2f}")
            print(f"   Day Trade Count: {account.get('daytrade_count', 0)}")
            print(f"   Pattern Day Trader: {account.get('pattern_day_trader', False)}")
            
            if 'monthly_return' in account:
                return_pct = account['monthly_return']
                emoji = "📈" if return_pct > 0 else "📉"
                print(f"   30-Day Return: {emoji} {return_pct:+.2f}%")
        else:
            print("   ❌ Could not retrieve account insights")
        
        print()
        
        # Get portfolio analytics
        print("2️⃣ Portfolio Analytics:")
        print("-" * 70)
        analytics = insights.get_portfolio_analytics()
        if analytics:
            print(f"   Total Positions: {analytics.get('total_positions', 0)}")
            print(f"   Total Market Value: ${analytics.get('total_market_value', 0):,.2f}")
            total_pnl = analytics.get('total_unrealized_pnl', 0)
            pnl_emoji = "💚" if total_pnl > 0 else "❤️"
            print(f"   Unrealized P&L: {pnl_emoji} ${total_pnl:+,.2f}")
            print()
            
            positions = analytics.get('positions', [])
            if positions:
                print("   Top Holdings:")
                for i, pos in enumerate(positions[:5], 1):
                    pl_emoji = "🟢" if pos['unrealized_pl'] > 0 else "🔴"
                    print(f"   {i}. {pl_emoji} {pos['symbol']:6} - "
                          f"{pos['portfolio_weight']:5.1f}% | "
                          f"${pos['market_value']:,.2f} | "
                          f"P&L: ${pos['unrealized_pl']:+,.2f} "
                          f"({pos['unrealized_pl_percent']:+.2f}%)")
        else:
            print("   ❌ Could not retrieve portfolio analytics")
        
        print()
        
        # Get trade history
        print("3️⃣ Recent Trade History (Last 30 Days):")
        print("-" * 70)
        trades = insights.get_trade_history(days=30)
        if trades:
            print(f"   Total Trades: {len(trades)}")
            print()
            print("   Last 5 Trades:")
            for trade in trades[:5]:
                side_emoji = "🟢" if trade['side'] == 'buy' else "🔴"
                print(f"   {side_emoji} {trade['side'].upper():4} {trade['qty']:6.2f} "
                      f"{trade['symbol']:6} @ ${trade['price']:7.2f} | "
                      f"{trade['transaction_time'][:19]}")
        else:
            print("   No trades found in the last 30 days")
        
        print()
        
        # Get performance summary
        print("4️⃣ Performance Summary:")
        print("-" * 70)
        summary = insights.get_performance_summary()
        if summary:
            print(f"   Period: {summary.get('period')}")
            print(f"   Total Trades: {summary.get('total_trades', 0)}")
            print(f"   Portfolio Value: ${summary.get('portfolio_value', 0):,.2f}")
            print(f"   Open Positions: {summary.get('open_positions', 0)}")
            
            total_pnl = summary.get('total_unrealized_pnl', 0)
            pnl_emoji = "💚" if total_pnl > 0 else "❤️"
            print(f"   Total P&L: {pnl_emoji} ${total_pnl:+,.2f}")
            
            if 'best_position' in summary:
                best = summary['best_position']
                print(f"   🏆 Best Position: {best['symbol']} "
                      f"({best['unrealized_pl_percent']:+.2f}%)")
            
            if 'worst_position' in summary:
                worst = summary['worst_position']
                print(f"   ⚠️  Worst Position: {worst['symbol']} "
                      f"({worst['unrealized_pl_percent']:+.2f}%)")
            
            if 'largest_position' in summary:
                largest = summary['largest_position']
                print(f"   📊 Largest Position: {largest['symbol']} "
                      f"({largest['portfolio_weight']:.1f}% of portfolio)")
        
        print()
        print("=" * 70)
        print("✅ BROKER API TEST COMPLETE!")
        print("=" * 70)
        print()
        print("💡 The Broker API provides enhanced insights beyond Trading API:")
        print("   • Detailed portfolio analytics")
        print("   • Advanced performance metrics")
        print("   • Risk analysis")
        print("   • Enhanced trade history")
        print("   • Account management features")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("   1. Check your Broker API credentials in .env")
        print("   2. Verify you're using the sandbox endpoint")
        print("   3. Make sure you have an active Alpaca account")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())


