"""
RAG Memory Query Tool

Interactive tool to query and explore the trading bot's long-term memory.
"""

import yaml
import sys
from utils.rag_memory import TradingMemory
from utils.logger import get_logger

log = get_logger("rag_query")


def load_config(path: str = "config.yaml"):
    with open(path, "r") as f:
        return yaml.safe_load(f)


def show_stats():
    """Display RAG memory statistics"""
    cfg = load_config()
    
    if not cfg.get('rag', {}).get('enabled', False):
        print("❌ RAG is not enabled in config.yaml")
        return
    
    memory = TradingMemory(
        storage_path=cfg['rag'].get('storage_path', './storage/chroma_db'),
        model_name=cfg['rag'].get('model', 'all-MiniLM-L6-v2')
    )
    
    stats = memory.get_stats()
    
    print("\n" + "="*60)
    print("🧠 RAG MEMORY STATISTICS")
    print("="*60)
    print(f"📚 Total Insights Stored: {stats.get('total_insights', 0)}")
    print(f"💰 Total Trades Recorded: {stats.get('total_trades', 0)}")
    print(f"🔍 Market Patterns: {stats.get('total_patterns', 0)}")
    print(f"📁 Storage Path: {stats.get('storage_path', 'N/A')}")
    print("="*60 + "\n")


def query_ticker(ticker: str):
    """Query complete history for a ticker"""
    cfg = load_config()
    
    if not cfg.get('rag', {}).get('enabled', False):
        print("❌ RAG is not enabled")
        return
    
    memory = TradingMemory(
        storage_path=cfg['rag'].get('storage_path', './storage/chroma_db'),
        model_name=cfg['rag'].get('model', 'all-MiniLM-L6-v2')
    )
    
    print(f"\n🔍 Querying history for {ticker}...")
    history = memory.get_ticker_history(ticker, n_results=10)
    
    print("\n" + "="*60)
    print(f"📊 COMPLETE HISTORY: {ticker}")
    print("="*60)
    
    insights = history.get('insights', [])
    print(f"\n📚 HISTORICAL INSIGHTS ({len(insights)}):")
    print("-"*60)
    
    for i, insight in enumerate(insights[:5], 1):
        print(f"\n{i}. {insight.get('timestamp', 'N/A')}")
        print(f"   Signal: {insight.get('signal')} (Confidence: {insight.get('confidence', 0):.2f})")
        print(f"   Reasoning: {insight.get('reasoning', 'N/A')}")
        if insight.get('key_factors'):
            print(f"   Key Factors: {', '.join(insight.get('key_factors', [])[:3])}")
    
    trades = history.get('trades', [])
    print(f"\n\n💰 TRADE HISTORY ({len(trades)}):")
    print("-"*60)
    
    wins = sum(1 for t in trades if t.get('outcome') == 'WIN')
    losses = sum(1 for t in trades if t.get('outcome') == 'LOSS')
    
    if trades:
        print(f"Win Rate: {wins}W - {losses}L ({wins/(wins+losses)*100:.1f}% win rate)" if (wins+losses) > 0 else "No completed trades")
        
        for i, trade in enumerate(trades[:5], 1):
            print(f"\n{i}. {trade.get('timestamp', 'N/A')}")
            print(f"   {trade.get('action')} @ ${trade.get('entry_price', 0):.2f}")
            print(f"   Outcome: {trade.get('outcome')} (PnL: ${trade.get('pnl', 0):.2f})")
    else:
        print("No trades recorded yet")
    
    print("\n" + "="*60 + "\n")


def query_market_conditions(query: str):
    """Query similar market conditions"""
    cfg = load_config()
    
    if not cfg.get('rag', {}).get('enabled', False):
        print("❌ RAG is not enabled")
        return
    
    memory = TradingMemory(
        storage_path=cfg['rag'].get('storage_path', './storage/chroma_db'),
        model_name=cfg['rag'].get('model', 'all-MiniLM-L6-v2')
    )
    
    print(f"\n🔍 Searching for: '{query}'...")
    patterns = memory.query_market_conditions(query, n_results=5)
    
    print("\n" + "="*60)
    print(f"🔍 SIMILAR MARKET CONDITIONS")
    print("="*60)
    
    if patterns:
        for i, pattern in enumerate(patterns, 1):
            print(f"\n{i}. {pattern.get('timestamp', 'N/A')}")
            print(f"   Insights: {pattern.get('num_insights', 0)}")
            print(f"   Summary: {pattern.get('summary', 'N/A')[:200]}...")
            if pattern.get('distance'):
                print(f"   Similarity: {1 - pattern['distance']:.2%}")
    else:
        print("No similar patterns found")
    
    print("\n" + "="*60 + "\n")


def interactive_mode():
    """Interactive query mode"""
    cfg = load_config()
    
    if not cfg.get('rag', {}).get('enabled', False):
        print("❌ RAG is not enabled in config.yaml")
        print("Set rag.enabled: true in config.yaml to use this feature")
        return
    
    print("\n" + "="*60)
    print("🧠 RAG MEMORY INTERACTIVE QUERY")
    print("="*60)
    print("\nCommands:")
    print("  stats              - Show memory statistics")
    print("  ticker SYMBOL      - Query history for a ticker (e.g., 'ticker AAPL')")
    print("  query TEXT         - Search market conditions (e.g., 'query high volatility tech')")
    print("  exit               - Exit")
    print("="*60 + "\n")
    
    while True:
        try:
            cmd = input("rag> ").strip()
            
            if not cmd:
                continue
            
            if cmd.lower() == 'exit':
                print("👋 Goodbye!")
                break
            
            elif cmd.lower() == 'stats':
                show_stats()
            
            elif cmd.lower().startswith('ticker '):
                ticker = cmd.split()[1].upper()
                query_ticker(ticker)
            
            elif cmd.lower().startswith('query '):
                query_text = ' '.join(cmd.split()[1:])
                query_market_conditions(query_text)
            
            else:
                print("❌ Unknown command. Type 'exit' to quit.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")


if __name__ == "__main__":
    if len(sys.argv) == 1:
        # Interactive mode
        interactive_mode()
    elif sys.argv[1] == 'stats':
        show_stats()
    elif sys.argv[1] == 'ticker' and len(sys.argv) >= 3:
        query_ticker(sys.argv[2].upper())
    elif sys.argv[1] == 'query' and len(sys.argv) >= 3:
        query_market_conditions(' '.join(sys.argv[2:]))
    else:
        print("Usage:")
        print("  python query_rag_memory.py              - Interactive mode")
        print("  python query_rag_memory.py stats        - Show statistics")
        print("  python query_rag_memory.py ticker AAPL  - Query ticker history")
        print("  python query_rag_memory.py query TEXT   - Search market conditions")

