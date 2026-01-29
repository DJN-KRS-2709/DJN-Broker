#!/usr/bin/env python3
"""
Show trading performance summary - closed trades and real win rate.
Run this to check your actual trading results.
"""
import os
import json
from datetime import datetime, timedelta

CLOSED_TRADES_FILE = "storage/learning/closed_trades.json"


def show_performance():
    print("=" * 60)
    print("📊 TRADING PERFORMANCE SUMMARY")
    print("=" * 60)
    
    if not os.path.exists(CLOSED_TRADES_FILE):
        print("\n⚠️  No closed trades yet!")
        print("   Positions will close when they hit:")
        print("   • Take profit: +5%")
        print("   • Stop loss: -3%")
        print("\n   Keep the bot running and check back later.")
        return
    
    with open(CLOSED_TRADES_FILE, 'r') as f:
        trades = json.load(f)
    
    if not trades:
        print("\n⚠️  No closed trades yet!")
        return
    
    # Calculate stats
    winners = [t for t in trades if t.get('is_winner', False)]
    losers = [t for t in trades if not t.get('is_winner', True)]
    take_profits = [t for t in trades if t.get('reason') == 'take_profit']
    stop_losses = [t for t in trades if t.get('reason') == 'stop_loss']
    
    total_pnl = sum(t.get('realized_pnl', 0) for t in trades)
    avg_winner = sum(t.get('realized_pnl', 0) for t in winners) / len(winners) if winners else 0
    avg_loser = sum(t.get('realized_pnl', 0) for t in losers) / len(losers) if losers else 0
    win_rate = len(winners) / len(trades) if trades else 0
    
    print(f"\n📈 OVERALL STATS")
    print("-" * 40)
    print(f"   Total Closed Trades: {len(trades)}")
    print(f"   Winners: {len(winners)} 🟢")
    print(f"   Losers: {len(losers)} 🔴")
    print(f"   Win Rate: {win_rate:.1%}")
    print(f"   Total Realized P&L: ${total_pnl:+,.2f}")
    
    print(f"\n💰 AVERAGE TRADE")
    print("-" * 40)
    print(f"   Avg Winner: ${avg_winner:+,.2f}")
    print(f"   Avg Loser: ${avg_loser:+,.2f}")
    if avg_loser != 0:
        print(f"   Risk/Reward: {abs(avg_winner/avg_loser):.2f}:1")
    
    print(f"\n🎯 EXIT REASONS")
    print("-" * 40)
    print(f"   Take Profits (+5%): {len(take_profits)}")
    print(f"   Stop Losses (-3%): {len(stop_losses)}")
    
    # Recent trades
    print(f"\n📋 RECENT CLOSED TRADES")
    print("-" * 40)
    
    # Sort by date descending
    recent = sorted(trades, key=lambda x: x.get('closed_at', ''), reverse=True)[:10]
    
    for trade in recent:
        symbol = trade.get('symbol', '???')
        pnl = trade.get('realized_pnl', 0)
        pnl_pct = trade.get('realized_pnl_pct', 0)
        reason = trade.get('reason', '???')
        date = trade.get('date', '???')
        
        emoji = "🟢" if pnl > 0 else "🔴"
        reason_emoji = "🎯" if reason == "take_profit" else "🛑"
        
        print(f"   {emoji} {symbol}: ${pnl:+,.2f} ({pnl_pct:+.1%}) {reason_emoji} {reason} [{date}]")
    
    if len(trades) > 10:
        print(f"   ... and {len(trades) - 10} more trades")
    
    # Performance by stock
    print(f"\n📊 PERFORMANCE BY STOCK")
    print("-" * 40)
    
    stock_perf = {}
    for trade in trades:
        symbol = trade.get('symbol', '???')
        pnl = trade.get('realized_pnl', 0)
        if symbol not in stock_perf:
            stock_perf[symbol] = {'pnl': 0, 'trades': 0, 'wins': 0}
        stock_perf[symbol]['pnl'] += pnl
        stock_perf[symbol]['trades'] += 1
        if pnl > 0:
            stock_perf[symbol]['wins'] += 1
    
    for symbol, stats in sorted(stock_perf.items(), key=lambda x: x[1]['pnl'], reverse=True):
        wr = stats['wins'] / stats['trades'] if stats['trades'] > 0 else 0
        emoji = "🟢" if stats['pnl'] > 0 else "🔴"
        print(f"   {emoji} {symbol}: ${stats['pnl']:+,.2f} ({stats['trades']} trades, {wr:.0%} win rate)")
    
    print("\n" + "=" * 60)
    
    # Go/No-go recommendation
    if len(trades) >= 5:
        if win_rate >= 0.5 and total_pnl > 0:
            print("✅ READY FOR LIVE TRADING!")
            print(f"   {len(trades)} closed trades with {win_rate:.0%} win rate")
            print(f"   Total profit: ${total_pnl:+,.2f}")
        else:
            print("⚠️  NOT READY FOR LIVE TRADING YET")
            print(f"   Win rate: {win_rate:.0%} (target: 50%+)")
            print(f"   P&L: ${total_pnl:+,.2f} (target: positive)")
            print("   Keep paper trading to improve!")
    else:
        print(f"📊 Need more data: {len(trades)}/5 closed trades")
        print("   Keep running to collect more results!")
    
    print("=" * 60)


if __name__ == "__main__":
    show_performance()



