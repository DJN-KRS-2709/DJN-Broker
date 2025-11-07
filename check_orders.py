#!/usr/bin/env python3
"""
Check recent orders and positions in Alpaca account.
"""
from trade.alpaca_broker import get_alpaca_client

client = get_alpaca_client(paper=True)

if not client:
    print("❌ Failed to connect to Alpaca")
    exit(1)

print("=" * 60)
print("📋 Recent Orders")
print("=" * 60)

# Get recent orders
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.enums import QueryOrderStatus

order_request = GetOrdersRequest(
    status=QueryOrderStatus.ALL,
    limit=10
)
orders = client.get_orders(filter=order_request)

if orders:
    for order in orders:
        status_emoji = {
            'accepted': '⏳',
            'pending_new': '⏳',
            'new': '⏳',
            'filled': '✅',
            'partially_filled': '🔄',
            'canceled': '❌',
            'rejected': '❌'
        }.get(order.status, '❓')
        
        print(f"\n{status_emoji} Order ID: {order.id}")
        print(f"   Symbol: {order.symbol}")
        print(f"   Side: {order.side}")
        print(f"   Type: {order.type}")
        print(f"   Status: {order.status}")
        print(f"   Submitted: {order.submitted_at}")
        if order.filled_at:
            print(f"   Filled: {order.filled_at}")
        if order.filled_avg_price:
            print(f"   Fill Price: ${float(order.filled_avg_price):.2f}")
else:
    print("\nNo orders found")

print("\n" + "=" * 60)
print("📊 Current Positions")
print("=" * 60)

positions = client.get_all_positions()

if positions:
    total_value = 0
    for pos in positions:
        market_value = float(pos.market_value)
        total_value += market_value
        unrealized_pl = float(pos.unrealized_pl)
        pl_pct = float(pos.unrealized_plpc) * 100
        
        pl_emoji = "🟢" if unrealized_pl >= 0 else "🔴"
        
        print(f"\n{pl_emoji} {pos.symbol}")
        print(f"   Quantity: {pos.qty} shares")
        print(f"   Entry Price: ${float(pos.avg_entry_price):.2f}")
        print(f"   Current Price: ${float(pos.current_price):.2f}")
        print(f"   Market Value: ${market_value:,.2f}")
        print(f"   P&L: ${unrealized_pl:,.2f} ({pl_pct:+.2f}%)")
    
    print(f"\n{'='*60}")
    print(f"Total Position Value: ${total_value:,.2f}")
else:
    print("\n No open positions yet")

print("\n" + "=" * 60)

