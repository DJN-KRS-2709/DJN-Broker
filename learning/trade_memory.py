"""
Trade Memory System - RAG Database for Learning
Stores all trades, signals, and outcomes for learning and optimization.
"""
import os
import json
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from utils.logger import get_logger

log = get_logger("trade_memory")


class TradeMemory:
    """
    RAG-style memory system for storing and retrieving trading knowledge.
    """
    
    def __init__(self, storage_dir: str = "storage/learning"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)
        
        self.trades_file = os.path.join(storage_dir, "trades_history.json")
        self.signals_file = os.path.join(storage_dir, "signals_history.json")
        self.learnings_file = os.path.join(storage_dir, "learnings.json")
        self.performance_file = os.path.join(storage_dir, "performance_metrics.json")
        
    def store_trade(self, trade: Dict):
        """Store a completed trade with outcome."""
        trade['timestamp'] = datetime.now().isoformat()
        trade['date'] = datetime.now().strftime('%Y-%m-%d')
        
        trades = self._load_json(self.trades_file, [])
        trades.append(trade)
        self._save_json(self.trades_file, trades)
        
        log.info(f"Stored trade: {trade.get('ticker')} {trade.get('action')} @ ${trade.get('price', 0):.2f}")
    
    def store_signal(self, signal: Dict, context: Dict):
        """Store a trading signal with market context."""
        signal_record = {
            **signal,
            'timestamp': datetime.now().isoformat(),
            'date': datetime.now().strftime('%Y-%m-%d'),
            'context': context  # sentiment, momentum, etc.
        }
        
        signals = self._load_json(self.signals_file, [])
        signals.append(signal_record)
        self._save_json(self.signals_file, signals)
    
    def store_learning(self, learning: Dict):
        """Store a learning/insight discovered from analysis."""
        learning['timestamp'] = datetime.now().isoformat()
        learning['date'] = datetime.now().strftime('%Y-%m-%d')
        
        learnings = self._load_json(self.learnings_file, [])
        learnings.append(learning)
        self._save_json(self.learnings_file, learnings)
        
        log.info(f"💡 New learning: {learning.get('insight', 'Unknown')}")
    
    def get_recent_trades(self, days: int = 7) -> List[Dict]:
        """Retrieve trades from last N days."""
        trades = self._load_json(self.trades_file, [])
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        return [t for t in trades if t.get('timestamp', '') >= cutoff]
    
    def get_recent_signals(self, days: int = 7) -> List[Dict]:
        """Retrieve signals from last N days."""
        signals = self._load_json(self.signals_file, [])
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        return [s for s in signals if s.get('timestamp', '') >= cutoff]
    
    def get_learnings(self, category: Optional[str] = None) -> List[Dict]:
        """Retrieve all learnings, optionally filtered by category."""
        learnings = self._load_json(self.learnings_file, [])
        if category:
            return [l for l in learnings if l.get('category') == category]
        return learnings
    
    def get_performance_metrics(self) -> Dict:
        """Get latest performance metrics."""
        return self._load_json(self.performance_file, {})
    
    def update_performance_metrics(self, metrics: Dict):
        """Update performance metrics."""
        metrics['timestamp'] = datetime.now().isoformat()
        self._save_json(self.performance_file, metrics)
        log.info(f"📊 Performance updated: Win rate {metrics.get('win_rate', 0):.1%}")
    
    def get_best_performing_stocks(self, limit: int = 5) -> List[str]:
        """Find stocks with best historical performance."""
        trades = self._load_json(self.trades_file, [])
        
        if not trades:
            return []
        
        df = pd.DataFrame(trades)
        if 'ticker' not in df.columns or 'pnl' not in df.columns:
            return []
        
        # Group by ticker and calculate total PnL
        performance = df.groupby('ticker')['pnl'].sum().sort_values(ascending=False)
        return performance.head(limit).index.tolist()
    
    def get_best_entry_times(self) -> Dict:
        """Analyze best times of day for entries."""
        trades = self._load_json(self.trades_file, [])
        
        if not trades:
            return {}
        
        df = pd.DataFrame(trades)
        if 'timestamp' not in df.columns:
            return {}
        
        # Extract hour and calculate win rate by hour
        df['hour'] = pd.to_datetime(df['timestamp']).dt.hour
        hourly_performance = df.groupby('hour').agg({
            'pnl': ['sum', 'mean', 'count']
        }).to_dict()
        
        return hourly_performance
    
    def get_sentiment_patterns(self) -> Dict:
        """Analyze which sentiment ranges lead to best outcomes."""
        signals = self._load_json(self.signals_file, [])
        
        if not signals:
            return {}
        
        # Analyze sentiment vs outcomes
        sentiment_bins = {
            'very_positive': [],  # > 0.6
            'positive': [],       # 0.4 - 0.6
            'neutral': [],        # 0.2 - 0.4
            'negative': []        # < 0.2
        }
        
        for signal in signals:
            sentiment = signal.get('context', {}).get('avg_sentiment', 0)
            outcome = signal.get('outcome', 0)  # If we track outcomes
            
            if sentiment > 0.6:
                sentiment_bins['very_positive'].append(outcome)
            elif sentiment > 0.4:
                sentiment_bins['positive'].append(outcome)
            elif sentiment > 0.2:
                sentiment_bins['neutral'].append(outcome)
            else:
                sentiment_bins['negative'].append(outcome)
        
        return sentiment_bins
    
    def _load_json(self, filepath: str, default):
        """Load JSON file or return default."""
        if not os.path.exists(filepath):
            return default
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception as e:
            log.error(f"Failed to load {filepath}: {e}")
            return default
    
    def _save_json(self, filepath: str, data):
        """Save data to JSON file."""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            log.error(f"Failed to save {filepath}: {e}")

