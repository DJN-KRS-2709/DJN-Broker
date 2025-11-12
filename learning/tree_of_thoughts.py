"""
Tree of Thoughts - Strategy exploration and optimization
Explores multiple strategy variations to find the best approach.
"""
import copy
from typing import Dict, List, Tuple
from learning.trade_memory import TradeMemory
from learning.analyzer import PerformanceAnalyzer
from utils.logger import get_logger

log = get_logger("tree_of_thoughts")


class StrategyNode:
    """Represents one strategy variation in the tree."""
    
    def __init__(self, name: str, params: Dict, parent=None):
        self.name = name
        self.params = params
        self.parent = parent
        self.children = []
        self.score = 0.0
        self.simulated_pnl = 0.0
        self.simulated_win_rate = 0.0
        self.trades_simulated = 0
    
    def add_child(self, child):
        self.children.append(child)
        child.parent = self


class TreeOfThoughts:
    """
    Explores multiple strategy paths to find optimal configuration.
    Uses historical data to simulate different approaches.
    """
    
    def __init__(self, memory: TradeMemory, analyzer: PerformanceAnalyzer):
        self.memory = memory
        self.analyzer = analyzer
        self.root = None
        self.best_strategy = None
    
    def explore_strategies(self, base_config: Dict, depth: int = 2) -> Dict:
        """
        Explore different strategy variations.
        
        Args:
            base_config: Current strategy configuration
            depth: How many levels to explore (2-3 recommended)
        
        Returns:
            Best strategy configuration found
        """
        log.info("🌳 Starting Tree of Thoughts exploration...")
        
        # Create root node with current strategy
        self.root = StrategyNode("current", base_config)
        
        # Get historical trades for simulation
        historical_trades = self.memory.get_recent_trades(days=7)
        historical_signals = self.memory.get_recent_signals(days=7)
        
        if len(historical_trades) < 10:
            log.warning("⚠️ Need at least 10 historical trades for ToT analysis")
            return base_config
        
        # Explore branches
        self._explore_branch(self.root, historical_signals, depth=depth, current_depth=0)
        
        # Find best strategy
        self.best_strategy = self._find_best_strategy()
        
        log.info(f"✅ Best strategy found: {self.best_strategy.name}")
        log.info(f"   Simulated Win Rate: {self.best_strategy.simulated_win_rate:.1%}")
        log.info(f"   Simulated P&L: ${self.best_strategy.simulated_pnl:.2f}")
        
        return self.best_strategy.params
    
    def _explore_branch(self, node: StrategyNode, signals: List[Dict], depth: int, current_depth: int):
        """Recursively explore strategy variations."""
        
        if current_depth >= depth:
            return
        
        # Generate strategy variations
        variations = self._generate_variations(node.params)
        
        for var_name, var_params in variations:
            # Create child node
            child = StrategyNode(var_name, var_params, parent=node)
            node.add_child(child)
            
            # Simulate this strategy on historical data
            child.score, child.simulated_pnl, child.simulated_win_rate = self._simulate_strategy(
                var_params, signals
            )
            
            log.info(f"  {'  ' * current_depth}└─ {var_name}: "
                    f"Score={child.score:.2f}, Win Rate={child.simulated_win_rate:.1%}")
            
            # Explore further if this looks promising
            if child.score > 0.5:  # Only explore promising branches
                self._explore_branch(child, signals, depth, current_depth + 1)
    
    def _generate_variations(self, base_params: Dict) -> List[Tuple[str, Dict]]:
        """Generate strategy variations to explore."""
        variations = []
        
        # Variation 1: Higher sentiment threshold (more conservative)
        params_high_sent = copy.deepcopy(base_params)
        current_sent = params_high_sent.get('min_sentiment', 0.4)
        params_high_sent['min_sentiment'] = min(current_sent + 0.1, 0.7)
        variations.append((f"High Sentiment ({params_high_sent['min_sentiment']:.2f})", params_high_sent))
        
        # Variation 2: Lower sentiment threshold (more aggressive)
        params_low_sent = copy.deepcopy(base_params)
        params_low_sent['min_sentiment'] = max(current_sent - 0.1, 0.2)
        variations.append((f"Low Sentiment ({params_low_sent['min_sentiment']:.2f})", params_low_sent))
        
        # Variation 3: Wider take profit
        params_wide_tp = copy.deepcopy(base_params)
        params_wide_tp['take_profit_pct'] = params_wide_tp.get('take_profit_pct', 0.10) * 1.3
        variations.append((f"Wide TP ({params_wide_tp['take_profit_pct']:.1%})", params_wide_tp))
        
        # Variation 4: Tighter stop loss
        params_tight_sl = copy.deepcopy(base_params)
        params_tight_sl['stop_loss_pct'] = params_tight_sl.get('stop_loss_pct', 0.04) * 0.8
        variations.append((f"Tight SL ({params_tight_sl['stop_loss_pct']:.1%})", params_tight_sl))
        
        # Variation 5: Focus on best 3 stocks
        best_stocks = self.memory.get_best_performing_stocks(3)
        if best_stocks:
            params_focus = copy.deepcopy(base_params)
            params_focus['focus_stocks'] = best_stocks
            variations.append((f"Focus Best 3", params_focus))
        
        # Variation 6: Larger position sizes
        params_large_pos = copy.deepcopy(base_params)
        params_large_pos['position_size_multiplier'] = 1.3
        variations.append((f"Large Positions (1.3x)", params_large_pos))
        
        # Variation 7: Smaller position sizes
        params_small_pos = copy.deepcopy(base_params)
        params_small_pos['position_size_multiplier'] = 0.7
        variations.append((f"Small Positions (0.7x)", params_small_pos))
        
        return variations
    
    def _simulate_strategy(self, params: Dict, signals: List[Dict]) -> Tuple[float, float, float]:
        """
        Simulate a strategy on historical signals.
        Returns: (score, simulated_pnl, simulated_win_rate)
        """
        wins = 0
        losses = 0
        total_pnl = 0.0
        trades = 0
        
        min_sentiment = params.get('min_sentiment', 0.4)
        focus_stocks = params.get('focus_stocks', [])
        
        for signal in signals:
            ticker = signal.get('ticker')
            sentiment = signal.get('context', {}).get('avg_sentiment', 0)
            
            # Apply filters from this strategy variation
            if sentiment < min_sentiment:
                continue
            
            if focus_stocks and ticker not in focus_stocks:
                continue
            
            # Simulate trade outcome (simplified)
            # In reality, you'd use actual historical prices
            # For now, use a probabilistic model based on sentiment
            win_probability = sentiment * 0.6 + 0.3  # Higher sentiment = higher win chance
            
            trades += 1
            
            # Simulate win/loss
            import random
            if random.random() < win_probability:
                wins += 1
                # Simulate profit
                tp_pct = params.get('take_profit_pct', 0.10)
                pnl = 100 * tp_pct  # Assume $100 position
                total_pnl += pnl
            else:
                losses += 1
                # Simulate loss
                sl_pct = params.get('stop_loss_pct', 0.04)
                pnl = -100 * sl_pct
                total_pnl += pnl
        
        if trades == 0:
            return 0.0, 0.0, 0.0
        
        win_rate = wins / trades
        
        # Score combines win rate and P&L
        # Prioritize win rate but consider profitability
        score = (win_rate * 0.7) + (min(total_pnl / 1000, 1.0) * 0.3)
        
        return score, total_pnl, win_rate
    
    def _find_best_strategy(self) -> StrategyNode:
        """Find the best performing strategy in the tree."""
        best = self.root
        best_score = self.root.score
        
        def traverse(node):
            nonlocal best, best_score
            if node.score > best_score:
                best = node
                best_score = node.score
            for child in node.children:
                traverse(child)
        
        traverse(self.root)
        return best
    
    def visualize_tree(self) -> str:
        """Generate ASCII visualization of the strategy tree."""
        lines = []
        lines.append("\n🌳 STRATEGY EXPLORATION TREE")
        lines.append("=" * 70)
        
        def print_node(node, prefix="", is_last=True):
            # Node info
            marker = "└─" if is_last else "├─"
            lines.append(f"{prefix}{marker} {node.name}")
            lines.append(f"{prefix}{'   ' if is_last else '│  '}   Score: {node.score:.2f}, "
                        f"Win Rate: {node.simulated_win_rate:.1%}, "
                        f"P&L: ${node.simulated_pnl:.2f}")
            
            # Children
            child_prefix = prefix + ("   " if is_last else "│  ")
            for i, child in enumerate(node.children):
                is_last_child = (i == len(node.children) - 1)
                print_node(child, child_prefix, is_last_child)
        
        print_node(self.root)
        lines.append("=" * 70)
        
        if self.best_strategy:
            lines.append(f"\n⭐ BEST STRATEGY: {self.best_strategy.name}")
            lines.append(f"   Win Rate: {self.best_strategy.simulated_win_rate:.1%}")
            lines.append(f"   Simulated P&L: ${self.best_strategy.simulated_pnl:.2f}")
            lines.append(f"   Score: {self.best_strategy.score:.2f}")
        
        return "\n".join(lines)
    
    def get_strategy_path(self, node: StrategyNode = None) -> List[str]:
        """Get the path from root to a node."""
        if node is None:
            node = self.best_strategy
        
        path = []
        current = node
        while current is not None:
            path.append(current.name)
            current = current.parent
        
        return list(reversed(path))




