#!/usr/bin/env python3
"""
Learning Dashboard - Shows what the system has learned
"""
from learning.trade_memory import TradeMemory
from learning.analyzer import PerformanceAnalyzer
from learning.strategy_optimizer import StrategyOptimizer
import json

def main():
    memory = TradeMemory()
    analyzer = PerformanceAnalyzer(memory)
    optimizer = StrategyOptimizer(memory, analyzer)
    
    print("\n" + "=" * 70)
    print("🧠 LEARNING SYSTEM DASHBOARD")
    print("=" * 70)
    
    # Performance Metrics
    metrics = memory.get_performance_metrics()
    if metrics:
        print("\n📊 CURRENT PERFORMANCE:")
        print(f"  Total Trades: {metrics.get('total_trades', 0)}")
        print(f"  Win Rate: {metrics.get('win_rate', 0):.1%}")
        print(f"  Winning Trades: {metrics.get('winning_trades', 0)}")
        print(f"  Losing Trades: {metrics.get('losing_trades', 0)}")
        print(f"  Total P&L: ${metrics.get('total_pnl', 0):.2f}")
        print(f"  Avg Win: ${metrics.get('avg_win', 0):.2f}")
        print(f"  Avg Loss: ${metrics.get('avg_loss', 0):.2f}")
        print(f"  Best Stock: {metrics.get('best_stock', 'N/A')}")
        print(f"  Worst Stock: {metrics.get('worst_stock', 'N/A')}")
        
        print("\n💡 INSIGHTS:")
        for insight in metrics.get('insights', []):
            print(f"  {insight}")
    else:
        print("\n📊 No performance data yet - run some trades first!")
    
    # Recent Trades
    trades = memory.get_recent_trades(days=7)
    print(f"\n📈 RECENT TRADES (Last 7 days): {len(trades)}")
    if trades:
        for trade in trades[-5:]:  # Show last 5
            print(f"  • {trade.get('ticker')} {trade.get('action')} @ ${trade.get('price', 0):.2f}")
            print(f"    Notional: ${trade.get('notional', 0):.2f}, P&L: ${trade.get('pnl', 0):.2f}")
    
    # Learnings
    learnings = memory.get_learnings()
    print(f"\n🎓 STORED LEARNINGS: {len(learnings)}")
    if learnings:
        # Group by category
        categories = {}
        for learning in learnings:
            cat = learning.get('category', 'other')
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(learning)
        
        for cat, items in categories.items():
            print(f"\n  📁 {cat.upper()}:")
            for item in items[-3:]:  # Show last 3 per category
                print(f"    • {item.get('insight', 'Unknown')}")
                if 'value' in item:
                    print(f"      Value: {item['value']}")
                if 'action' in item:
                    print(f"      Action: {item['action']}")
    
    # Best Performers
    best_stocks = memory.get_best_performing_stocks(5)
    if best_stocks:
        print(f"\n⭐ BEST PERFORMING STOCKS:")
        for stock in best_stocks:
            print(f"  • {stock}")
    
    # Strategy Recommendations
    recommendations = analyzer.get_strategy_recommendations()
    if recommendations.get('ready'):
        print(f"\n🎯 STRATEGY RECOMMENDATIONS:")
        for adj in recommendations.get('adjustments', []):
            print(f"  • {adj['action']} (confidence: {adj['confidence']}, frequency: {adj['frequency']})")
    else:
        print(f"\n🎯 STRATEGY RECOMMENDATIONS:")
        print(f"  ⏳ Need {recommendations.get('min_trades_needed', 10)} trades before recommendations available")
    
    # Optimization Summary
    opt_summary = optimizer.get_optimization_summary()
    print(f"\n⚙️  CURRENT OPTIMIZATIONS:")
    if opt_summary.get('current_params'):
        for key, value in opt_summary.get('current_params', {}).items():
            print(f"  • {key}: {value}")
    else:
        print("  No optimizations applied yet")
    
    print("\n" + "=" * 70)
    print("✅ Dashboard Complete")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

