"""
Strategy Optimizer - Adapts trading strategy based on learnings
Uses RAG insights to dynamically adjust parameters.
"""
from typing import Dict, List
from learning.trade_memory import TradeMemory
from learning.analyzer import PerformanceAnalyzer
from utils.logger import get_logger

log = get_logger("strategy_optimizer")


class StrategyOptimizer:
    """
    Adapts trading strategy based on performance learnings.
    PAPER MODE: Prioritizes learning over safety (trades more aggressively)
    LIVE MODE: Prioritizes safety over learning (trades conservatively)
    """
    
    def __init__(self, memory: TradeMemory, analyzer: PerformanceAnalyzer, paper_mode: bool = True):
        self.memory = memory
        self.analyzer = analyzer
        self.current_params = {}
        self.paper_mode = paper_mode
        
        if paper_mode:
            log.info("🧪 PAPER MODE: Optimizing for LEARNING (aggressive trading)")
        else:
            log.info("💰 LIVE MODE: Optimizing for SAFETY (conservative trading)")
    
    def optimize_strategy(self, base_config: Dict) -> Dict:
        """
        Optimize strategy parameters based on learnings.
        Returns adjusted config.
        """
        optimized = base_config.copy()
        
        # PAPER MODE: Keep sentiment threshold LOW to enable learning (ALWAYS, even without data)
        if self.paper_mode:
            # Force low threshold to ensure daily trades for learning
            optimized['min_sentiment'] = 0.10  # Very low threshold for paper trading
            log.info(f"🧪 PAPER MODE: Keeping sentiment threshold at 0.10 to maximize learning opportunities")
            # Return early - no need for complex optimization in paper mode
            return optimized
        
        # LIVE MODE: Use learnings to optimize
        # Get performance metrics
        metrics = self.memory.get_performance_metrics()
        recommendations = self.analyzer.get_strategy_recommendations()
        
        if not recommendations.get('ready'):
            log.info("📚 Not enough data for optimization yet")
            return optimized
        
        log.info("🧠 Optimizing strategy based on learnings...")
        
        # Apply recommended adjustments
        for adj in recommendations.get('adjustments', []):
            action = adj['action']
            confidence = adj['confidence']
            
            if action == 'increase_sentiment_threshold':
                # Require higher sentiment for trades
                current_threshold = optimized.get('min_sentiment', 0.4)
                new_threshold = min(current_threshold + 0.05, 0.7)  # Max 0.7
                optimized['min_sentiment'] = new_threshold
                log.info(f"📈 Increased sentiment threshold: {current_threshold} → {new_threshold}")
            
            elif action == 'lower_sentiment_threshold':
                # Allow more trades with lower sentiment
                current_threshold = optimized.get('min_sentiment', 0.4)
                new_threshold = max(current_threshold - 0.05, 0.2)  # Min 0.2
                optimized['min_sentiment'] = new_threshold
                log.info(f"📉 Lowered sentiment threshold: {current_threshold} → {new_threshold}")
            
            elif action == 'adjust_take_profit_stop_loss':
                # Widen take profit, tighten stop loss
                optimized['take_profit_pct'] = optimized.get('take_profit_pct', 0.10) * 1.2
                optimized['stop_loss_pct'] = optimized.get('stop_loss_pct', 0.04) * 0.9
                log.info(f"🎯 Adjusted TP/SL: TP={optimized['take_profit_pct']:.2%}, SL={optimized['stop_loss_pct']:.2%}")
            
            elif action == 'focus_on_best_performers':
                # Get best performing stocks
                best_stocks = self.memory.get_best_performing_stocks(limit=3)
                if best_stocks:
                    optimized['focus_stocks'] = best_stocks
                    log.info(f"⭐ Focusing on best performers: {', '.join(best_stocks)}")
        
        # Adjust position sizing based on win rate
        win_rate = metrics.get('win_rate', 0.5)
        if win_rate > 0.6:
            # Increase position size when winning
            optimized['position_size_multiplier'] = 1.2
            log.info(f"💪 Increased position size by 20% (win rate: {win_rate:.1%})")
        elif win_rate < 0.4:
            # Decrease position size when losing
            optimized['position_size_multiplier'] = 0.8
            log.info(f"⚠️ Decreased position size by 20% (win rate: {win_rate:.1%})")
        
        self.current_params = optimized
        return optimized
    
    def filter_signals_by_learning(self, signals: List[Dict]) -> List[Dict]:
        """
        Filter trading signals based on historical learnings.
        Only keep signals likely to be profitable.
        """
        if not signals:
            return signals
        
        filtered = []
        best_stocks = self.memory.get_best_performing_stocks(limit=5)
        
        for signal in signals:
            ticker = signal.get('ticker')
            
            # Filter by stock performance if we have history
            if best_stocks:
                if ticker not in best_stocks:
                    log.info(f"⏭️  Skipping {ticker} (not in top performers)")
                    continue
            
            # Check sentiment strength
            strength = signal.get('strength', 0)
            min_strength = self.current_params.get('min_sentiment', 0.4)
            
            if strength < min_strength:
                log.info(f"⏭️  Skipping {ticker} (sentiment {strength:.2f} < {min_strength:.2f})")
                continue
            
            # Signal passes filters
            filtered.append(signal)
            log.info(f"✅ Approved signal: {ticker} (sentiment: {strength:.2f})")
        
        return filtered
    
    def adjust_capital_allocation(self, base_capital: float) -> float:
        """
        Adjust capital based on recent performance.
        More conservative when losing, more aggressive when winning.
        """
        metrics = self.memory.get_performance_metrics()
        win_rate = metrics.get('win_rate', 0.5)
        total_pnl = metrics.get('total_pnl', 0)
        
        # Start conservative, increase with success
        if win_rate > 0.6 and total_pnl > 0:
            multiplier = 1.3  # Use 130% of capital when consistently winning
            log.info(f"📈 Increasing capital allocation to {base_capital * multiplier:.2f}")
            return base_capital * multiplier
        elif win_rate < 0.4:
            multiplier = 0.7  # Use only 70% of capital when losing
            log.info(f"📉 Decreasing capital allocation to {base_capital * multiplier:.2f}")
            return base_capital * multiplier
        
        return base_capital
    
    def get_momentum_adjustment(self) -> float:
        """
        Adjust momentum requirements based on what's working.
        """
        learnings = self.memory.get_learnings(category='momentum')
        
        if not learnings:
            return 1.0  # No adjustment
        
        # Analyze if higher/lower momentum requirements help
        # For now, keep default
        return 1.0
    
    def should_pause_trading(self) -> bool:
        """
        Decide if we should pause trading due to poor performance.
        PAPER MODE: NEVER pause (we want to learn from failures)
        LIVE MODE: Pause if significant losses
        """
        # PAPER MODE: Never pause trading - we're here to LEARN!
        if self.paper_mode:
            log.info("🧪 PAPER MODE: Trading continues regardless of performance (learning phase)")
            return False
        
        # LIVE MODE: Pause if losing significantly
        metrics = self.memory.get_performance_metrics()
        total_pnl = metrics.get('total_pnl', 0)
        total_trades = metrics.get('total_trades', 0)
        
        if total_trades >= 10:
            # If down more than 20% after 10+ trades, pause
            if total_pnl < -100:  # Lost $100 or more
                log.warning("🛑 PAUSING TRADING due to significant losses")
                return True
        
        return False
    
    def get_optimization_summary(self) -> Dict:
        """
        Get summary of current optimizations applied.
        """
        metrics = self.memory.get_performance_metrics()
        learnings = self.memory.get_learnings()
        
        return {
            'total_trades': metrics.get('total_trades', 0),
            'win_rate': metrics.get('win_rate', 0),
            'total_pnl': metrics.get('total_pnl', 0),
            'total_learnings': len(learnings),
            'best_stocks': self.memory.get_best_performing_stocks(3),
            'current_params': self.current_params,
            'insights': metrics.get('insights', [])
        }




