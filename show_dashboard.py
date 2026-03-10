#!/usr/bin/env python3
"""
Simple daily performance dashboard.
Run to quickly see today's P&L, win rate, signal count, and last run.
"""
import os
import json
import re
from datetime import date

CLOSED_TRADES_FILE = "storage/learning/closed_trades.json"
DAILY_SUMMARY_FILE = "storage/daily_summary.csv"


def show_dashboard():
    today = date.today().isoformat()
    print("=" * 50)
    print(f"  DAILY DASHBOARD  {today}")
    print("=" * 50)

    # Today's closed trades
    today_pnl = 0.0
    today_winners = 0
    today_losers = 0
    today_trades = []

    if os.path.exists(CLOSED_TRADES_FILE):
        with open(CLOSED_TRADES_FILE, "r") as f:
            all_trades = json.load(f)
        today_trades = [t for t in all_trades if t.get("date") == today]
        today_pnl = sum(t.get("realized_pnl", 0) for t in today_trades)
        today_winners = len([t for t in today_trades if t.get("is_winner", False)])
        today_losers = len([t for t in today_trades if not t.get("is_winner", True)])

    today_win_rate = today_winners / len(today_trades) if today_trades else 0.0

    # Today's runs from daily_summary (CSV may have inconsistent columns)
    today_signals = 0
    last_run = None
    if os.path.exists(DAILY_SUMMARY_FILE):
        try:
            with open(DAILY_SUMMARY_FILE, "r") as f:
                lines = f.readlines()
            for line in lines[1:]:  # skip header
                parts = line.strip().split(",")
                if len(parts) >= 2 and re.match(r"\d{4}-\d{2}-\d{2}", parts[0]):
                    last_run = parts[0]
                    if parts[0][:10] == today and len(parts) >= 2:
                        try:
                            today_signals += int(float(parts[1]))
                        except (ValueError, TypeError):
                            pass
        except Exception:
            pass

    # Display
    print(f"\n  TODAY'S P&L:        ${today_pnl:+,.2f}")
    print(f"  TODAY'S WIN RATE:   {today_win_rate:.0%}  ({today_winners}W / {today_losers}L)")
    print(f"  TODAY'S SIGNALS:    {today_signals}")
    print(f"  LAST RUN:          {last_run or 'N/A'}")
    if today_trades:
        print(f"\n  Today's trades:")
        for t in today_trades:
            emoji = "🟢" if t.get("is_winner") else "🔴"
            print(f"    {emoji} {t.get('symbol')}: ${t.get('realized_pnl', 0):+,.2f} ({t.get('reason', '?')})")

    # All-time quick stats
    if os.path.exists(CLOSED_TRADES_FILE):
        with open(CLOSED_TRADES_FILE, "r") as f:
            all_trades = json.load(f)
        total_pnl = sum(t.get("realized_pnl", 0) for t in all_trades)
        total_wr = len([t for t in all_trades if t.get("is_winner")]) / len(all_trades) if all_trades else 0
        print(f"\n  ALL-TIME: ${total_pnl:+,.2f} | {total_wr:.0%} win rate | {len(all_trades)} trades")

    print("=" * 50)


if __name__ == "__main__":
    show_dashboard()
