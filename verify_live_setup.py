#!/usr/bin/env python3
"""
Verify Alpaca LIVE credentials and account (run locally: python verify_live_setup.py).

Does not print secrets. Set in .env or environment:
  ALPACA_LIVE_API_KEY
  ALPACA_LIVE_API_SECRET
"""
import os
import sys

from dotenv import load_dotenv

load_dotenv()


def main() -> int:
    key = os.getenv("ALPACA_LIVE_API_KEY")
    secret = os.getenv("ALPACA_LIVE_API_SECRET")

    print("=" * 50)
    print("Alpaca LIVE verification")
    print("=" * 50)

    if not key or not secret:
        print("FAIL: ALPACA_LIVE_API_KEY or ALPACA_LIVE_API_SECRET missing.")
        print("      Add them to .env or export in the shell.")
        return 1

    print(f"OK: Key present (length {len(key)}), secret present (length {len(secret)})")

    try:
        from alpaca.trading.client import TradingClient

        client = TradingClient(key, secret, paper=False)
        acct = client.get_account()
    except Exception as e:
        print(f"FAIL: Could not connect to Alpaca LIVE: {e}")
        return 1

    print(f"OK: Connected to LIVE account")
    print(f"    Status: {acct.status}")
    print(f"    Buying power: ${float(acct.buying_power):,.2f}")
    print(f"    Portfolio value: ${float(acct.portfolio_value):,.2f}")
    print(f"    Equity: ${float(acct.equity):,.2f}")

    try:
        positions = client.get_all_positions()
        print(f"    Open positions: {len(positions)}")
    except Exception as e:
        print(f"WARN: Could not list positions: {e}")

    print("=" * 50)
    print("Next: add the same two secrets to GitHub → Settings → Secrets → Actions")
    print("      (names: ALPACA_LIVE_API_KEY, ALPACA_LIVE_API_SECRET)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
