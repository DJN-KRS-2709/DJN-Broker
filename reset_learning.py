#!/usr/bin/env python3
"""
Reset learning system for fresh start
Keeps trade history but clears learnings and resets metrics
"""
import os
import json

# Path to learning directory
learning_dir = "storage/learning"

# Clear learnings (keep as empty list)
learnings_file = os.path.join(learning_dir, "learnings.json")
if os.path.exists(learnings_file):
    with open(learnings_file, 'w') as f:
        json.dump([], f, indent=2)
    print(f"✅ Cleared {learnings_file}")

# Reset performance metrics
metrics_file = os.path.join(learning_dir, "performance_metrics.json")
if os.path.exists(metrics_file):
    metrics = {
        "total_trades": 0,
        "winning_trades": 0,
        "losing_trades": 0,
        "win_rate": 0.0,
        "total_pnl": 0.0,
        "avg_win": 0,
        "avg_loss": 0,
        "insights": []
    }
    with open(metrics_file, 'w') as f:
        json.dump(metrics, f, indent=2)
    print(f"✅ Reset {metrics_file}")

# Keep signals and trades history for reference
print(f"✅ Kept trade and signal history for analysis")
print()
print("🎉 Learning system reset complete!")
print("Next run will start with fresh learnings and paper mode optimizations")


