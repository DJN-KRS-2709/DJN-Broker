#!/usr/bin/env python3
"""
Tree of Thoughts Strategy Exploration
Run this to explore multiple strategy variations and find the best one.
"""
from learning.trade_memory import TradeMemory
from learning.analyzer import PerformanceAnalyzer
from learning.tree_of_thoughts import TreeOfThoughts
import yaml

def main():
    # Load current config
    with open('config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    # Initialize learning components
    memory = TradeMemory()
    analyzer = PerformanceAnalyzer(memory)
    tot = TreeOfThoughts(memory, analyzer)
    
    print("\n" + "=" * 70)
    print("🌳 TREE OF THOUGHTS - STRATEGY EXPLORATION")
    print("=" * 70)
    print("\nThis will explore multiple strategy variations to find")
    print("the best configuration based on historical performance.\n")
    
    # Check if we have enough data
    trades = memory.get_recent_trades(days=7)
    if len(trades) < 10:
        print("⚠️  Need at least 10 historical trades for analysis")
        print(f"Current trades: {len(trades)}")
        print("\nRun the bot for a few days first, then come back!")
        return
    
    print(f"✅ Found {len(trades)} historical trades to analyze\n")
    
    # Current strategy
    base_strategy = {
        'min_sentiment': 0.4,
        'take_profit_pct': config['risk']['take_profit_pct'],
        'stop_loss_pct': config['risk']['stop_loss_pct'],
        'position_size_multiplier': 1.0
    }
    
    print("📊 Current Strategy:")
    for key, value in base_strategy.items():
        if 'pct' in key:
            print(f"  {key}: {value:.1%}")
        else:
            print(f"  {key}: {value}")
    print()
    
    # Explore strategy tree
    print("🔍 Exploring strategy variations...")
    print("(This may take a minute...)\n")
    
    best_strategy = tot.explore_strategies(base_strategy, depth=2)
    
    # Show results
    print("\n" + tot.visualize_tree())
    
    # Show recommended changes
    print("\n" + "=" * 70)
    print("💡 RECOMMENDATIONS")
    print("=" * 70)
    
    changes_made = False
    for key, new_value in best_strategy.items():
        old_value = base_strategy.get(key)
        if new_value != old_value:
            changes_made = True
            if 'pct' in key:
                print(f"  • {key}: {old_value:.1%} → {new_value:.1%}")
            else:
                print(f"  • {key}: {old_value} → {new_value}")
    
    if not changes_made:
        print("  ✅ Current strategy is already optimal!")
    else:
        print("\n⚠️  To apply these changes:")
        print("  1. Review the recommendations above")
        print("  2. Update config.yaml manually")
        print("  3. Or let the ReAct learning system apply them automatically")
    
    print("\n" + "=" * 70)
    print("✅ Strategy exploration complete!")
    print("=" * 70 + "\n")

if __name__ == "__main__":
    main()

