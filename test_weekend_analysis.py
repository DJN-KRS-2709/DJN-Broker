#!/usr/bin/env python3
"""
Test script to run weekend analysis manually (without waiting for the weekend)
This demonstrates the Tree of Thoughts pattern in action.
"""

from main import load_config
from nlp.weekend_analysis import run_weekend_analysis
from utils.logger import get_logger
import json
import os

log = get_logger("test_weekend")

def main():
    log.info("=" * 80)
    log.info("🧪 TESTING WEEKEND ANALYSIS (Tree of Thoughts)")
    log.info("=" * 80)
    log.info("This will run the weekend deep analysis regardless of the day of week")
    log.info("")
    
    cfg = load_config()
    
    try:
        result = run_weekend_analysis(cfg)
        
        log.info("\n" + "=" * 80)
        log.info("✅ Weekend analysis completed successfully!")
        log.info("=" * 80)
        
        # Display the insights
        insights_path = os.path.join('storage', 'weekend_insights.json')
        if os.path.exists(insights_path):
            with open(insights_path, 'r') as f:
                data = json.load(f)
            
            log.info(f"\n📊 Analysis Summary:")
            log.info(f"   Timestamp: {data.get('timestamp')}")
            log.info(f"   Hypotheses evaluated: {data.get('hypotheses_evaluated')}")
            log.info(f"   Actionable insights: {len(data.get('insights', []))}")
            
            log.info(f"\n💡 Top Insights:")
            for i, insight in enumerate(data.get('insights', [])[:5], 1):
                log.info(f"\n{i}. {insight['ticker']} - {insight['signal']}")
                log.info(f"   Confidence: {insight['confidence']:.2f}")
                log.info(f"   Reasoning: {insight['reasoning']}")
                if insight.get('key_factors'):
                    log.info(f"   Key factors:")
                    for factor in insight['key_factors'][:3]:
                        log.info(f"      • {factor}")
            
            log.info("\n" + "=" * 80)
            log.info(f"📁 Full results saved to: {insights_path}")
            log.info("=" * 80)
        
    except Exception as e:
        log.error(f"❌ Weekend analysis failed: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())



