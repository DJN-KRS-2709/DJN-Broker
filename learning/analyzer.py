"""
Performance Analyzer - Extracts learnings from trade history
Analyzes patterns, calculates metrics, and generates insights.
"""
import pandas as pd
import numpy as np
from typing import Dict, List
from datetime import datetime, timedelta
from learning.trade_memory import TradeMemory
from utils.logger import get_logger

log = get_logger("analyzer")


class PerformanceAnalyzer:
    """
    Analyzes trading performance and extracts actionable learnings.
    """
    
    def __init__(self, memory: TradeMemory):
        self.memory = memory
    
    def analyze_performance(self, days: int = 7) -> Dict:
        """
        Comprehensive performance analysis.
        Returns metrics and insights.
        """
        trades = self.memory.get_recent_trades(days=days)
        
        if not trades:
            log.info("No trades to analyze yet")
            return {
                'total_trades': 0,
                'win_rate': 0,
                'total_pnl': 0,
                'insights': []
            }
        
        df = pd.DataFrame(trades)
        
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'analysis_period_days': days,
            'total_trades': len(df),
            'winning_trades': len(df[df.get('pnl', 0) > 0]) if 'pnl' in df.columns else 0,
            'losing_trades': len(df[df.get('pnl', 0) < 0]) if 'pnl' in df.columns else 0,
            'win_rate': 0,
            'total_pnl': 0,
            'avg_win': 0,
            'avg_loss': 0,
            'best_stock': None,
            'worst_stock': None,
            'insights': []
        }
        
        if 'pnl' in df.columns:
            metrics['total_pnl'] = float(df['pnl'].sum())
            metrics['win_rate'] = metrics['winning_trades'] / len(df) if len(df) > 0 else 0
            
            winning_trades = df[df['pnl'] > 0]
            losing_trades = df[df['pnl'] < 0]
            
            metrics['avg_win'] = float(winning_trades['pnl'].mean()) if len(winning_trades) > 0 else 0
            metrics['avg_loss'] = float(losing_trades['pnl'].mean()) if len(losing_trades) > 0 else 0
        
        if 'ticker' in df.columns and 'pnl' in df.columns:
            stock_performance = df.groupby('ticker')['pnl'].sum().sort_values(ascending=False)
            if len(stock_performance) > 0:
                metrics['best_stock'] = stock_performance.index[0]
                metrics['worst_stock'] = stock_performance.index[-1]
        
        # Generate insights
        insights = self._generate_insights(metrics, df)
        metrics['insights'] = insights
        
        # Store metrics
        self.memory.update_performance_metrics(metrics)
        
        log.info(f"📊 Analysis complete: {metrics['total_trades']} trades, "
                f"{metrics['win_rate']:.1%} win rate, ${metrics['total_pnl']:.2f} P&L")
        
        return metrics
    
    def _generate_insights(self, metrics: Dict, df: pd.DataFrame) -> List[str]:
        """Generate actionable insights from metrics."""
        insights = []
        
        # Win rate insights
        if metrics['win_rate'] > 0.6:
            insights.append("🟢 Strong win rate! Strategy is working well.")
            self.memory.store_learning({
                'category': 'win_rate',
                'insight': 'High win rate detected',
                'value': metrics['win_rate'],
                'action': 'maintain_strategy'
            })
        elif metrics['win_rate'] < 0.4 and metrics['total_trades'] > 10:
            insights.append("🔴 Low win rate. Consider adjusting sentiment threshold.")
            self.memory.store_learning({
                'category': 'win_rate',
                'insight': 'Low win rate detected',
                'value': metrics['win_rate'],
                'action': 'increase_sentiment_threshold'
            })
        
        # Risk/reward insights
        if metrics['avg_win'] > 0 and metrics['avg_loss'] < 0:
            ratio = abs(metrics['avg_win'] / metrics['avg_loss'])
            if ratio > 2:
                insights.append(f"🟢 Excellent risk/reward ratio: {ratio:.2f}:1")
                self.memory.store_learning({
                    'category': 'risk_reward',
                    'insight': 'Strong risk/reward ratio',
                    'value': ratio,
                    'action': 'maintain_strategy'
                })
            elif ratio < 1:
                insights.append(f"🔴 Poor risk/reward ratio: {ratio:.2f}:1. Wins too small or losses too big.")
                self.memory.store_learning({
                    'category': 'risk_reward',
                    'insight': 'Poor risk/reward ratio',
                    'value': ratio,
                    'action': 'adjust_take_profit_stop_loss'
                })
        
        # Stock performance insights
        if metrics.get('best_stock') and metrics.get('worst_stock'):
            insights.append(f"📈 Best performer: {metrics['best_stock']}")
            insights.append(f"📉 Worst performer: {metrics['worst_stock']}")
            
            self.memory.store_learning({
                'category': 'stock_performance',
                'insight': f"Best: {metrics['best_stock']}, Worst: {metrics['worst_stock']}",
                'action': 'focus_on_best_performers'
            })
        
        # Volume insights
        if metrics['total_trades'] < 5 and metrics['analysis_period_days'] >= 7:
            insights.append("⚠️ Low trading frequency. Consider lowering entry thresholds.")
            self.memory.store_learning({
                'category': 'frequency',
                'insight': 'Low trading frequency',
                'value': metrics['total_trades'],
                'action': 'lower_sentiment_threshold'
            })
        
        return insights
    
    def get_strategy_recommendations(self) -> Dict:
        """
        Generate strategy recommendations based on learnings.
        """
        learnings = self.memory.get_learnings()
        
        if len(learnings) < 5:
            return {
                'ready': False,
                'message': 'Need more trades to generate recommendations',
                'min_trades_needed': 10
            }
        
        recommendations = {
            'ready': True,
            'adjustments': [],
            'confidence': 'medium'
        }
        
        # Analyze recent learnings
        recent_learnings = learnings[-10:]  # Last 10 learnings
        
        action_counts = {}
        for learning in recent_learnings:
            action = learning.get('action')
            if action:
                action_counts[action] = action_counts.get(action, 0) + 1
        
        # Most common actions become recommendations
        for action, count in sorted(action_counts.items(), key=lambda x: x[1], reverse=True):
            if count >= 2:  # Action suggested multiple times
                recommendations['adjustments'].append({
                    'action': action,
                    'frequency': count,
                    'confidence': 'high' if count >= 3 else 'medium'
                })
        
        return recommendations
    
    def should_trade_stock(self, ticker: str) -> bool:
        """
        Decide if we should trade a specific stock based on history.
        """
        best_stocks = self.memory.get_best_performing_stocks(limit=5)
        
        if not best_stocks:
            return True  # No history, allow all
        
        # Check if stock is in top performers
        return ticker in best_stocks or len(best_stocks) < 3
    
    def get_optimal_position_size(self, base_size: float) -> float:
        """
        Adjust position size based on recent performance.
        """
        metrics = self.memory.get_performance_metrics()
        win_rate = metrics.get('win_rate', 0.5)
        
        # Increase size if winning, decrease if losing
        if win_rate > 0.6:
            return base_size * 1.2  # 20% larger positions when winning
        elif win_rate < 0.4:
            return base_size * 0.8  # 20% smaller positions when losing
        
        return base_size

