#!/usr/bin/env python3
"""
⚠️  LIVE ACCOUNT CHECKER - REAL MONEY ⚠️
Checks your LIVE Alpaca account status.
NO TRADES will be executed by this script.
"""
from trade.alpaca_broker import get_account_summary
import sys

print("\n" + "=" * 60)
print("⚠️  CHECKING LIVE ALPACA ACCOUNT (REAL MONEY) ⚠️")
print("=" * 60)

# Check live trading account
print("\n💰 LIVE TRADING ACCOUNT:")
live_summary = get_account_summary(paper=False)

if live_summary:
    print(f"  ✅ Status: {live_summary['status']}")
    print(f"  💵 Cash: ${live_summary['cash']:,.2f}")
    print(f"  💼 Portfolio Value: ${live_summary['portfolio_value']:,.2f}")
    print(f"  💰 Buying Power: ${live_summary['buying_power']:,.2f}")
    print(f"  📈 Equity: ${live_summary['equity']:,.2f}")
    print(f"  📊 Open Positions: {live_summary['num_positions']}")
    
    if live_summary['positions']:
        print("\n  Current Positions:")
        for pos in live_summary['positions']:
            pl_emoji = "🟢" if pos['unrealized_pl'] >= 0 else "🔴"
            print(f"    {pl_emoji} {pos['symbol']}: {pos['qty']} shares, "
                  f"${pos['market_value']:,.2f} (P&L: ${pos['unrealized_pl']:,.2f})")
    else:
        print("  No open positions")
    
    print("\n" + "⚠️ " * 20)
    print("THIS IS YOUR LIVE ACCOUNT WITH REAL MONEY")
    print("To enable live trading, set paper_trading: false in config.yaml")
    print("ONLY do this if you understand the risks!")
    print("⚠️ " * 20)
else:
    print("  ❌ Failed to connect to live trading account")
    print("  Make sure ALPACA_LIVE_API_KEY and ALPACA_LIVE_API_SECRET are set in .env")
    sys.exit(1)

print("\n" + "=" * 60)
print("✅ Live account connection verified!")
print("=" * 60 + "\n")




