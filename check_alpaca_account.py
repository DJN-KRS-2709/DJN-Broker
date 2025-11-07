#!/usr/bin/env python3
"""
Utility script to check your Alpaca account status.
Run this to verify your API credentials are working.
"""
from trade.alpaca_broker import get_account_summary
import sys

def main():
    print("=" * 60)
    print("Checking Alpaca Account Status...")
    print("=" * 60)
    
    # Check paper trading account
    print("\n📊 PAPER TRADING ACCOUNT:")
    paper_summary = get_account_summary(paper=True)
    
    if paper_summary:
        print(f"  ✅ Status: {paper_summary['status']}")
        print(f"  💵 Cash: ${paper_summary['cash']:,.2f}")
        print(f"  💼 Portfolio Value: ${paper_summary['portfolio_value']:,.2f}")
        print(f"  💰 Buying Power: ${paper_summary['buying_power']:,.2f}")
        print(f"  📈 Equity: ${paper_summary['equity']:,.2f}")
        print(f"  📊 Open Positions: {paper_summary['num_positions']}")
        
        if paper_summary['positions']:
            print("\n  Current Positions:")
            for pos in paper_summary['positions']:
                pl_emoji = "🟢" if pos['unrealized_pl'] >= 0 else "🔴"
                print(f"    {pl_emoji} {pos['symbol']}: {pos['qty']} shares, "
                      f"${pos['market_value']:,.2f} (P&L: ${pos['unrealized_pl']:,.2f})")
        else:
            print("  No open positions")
    else:
        print("  ❌ Failed to connect to paper trading account")
        print("  Make sure ALPACA_API_KEY and ALPACA_API_SECRET are set in .env")
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("✅ Alpaca connection successful!")
    print("=" * 60)

if __name__ == "__main__":
    main()

