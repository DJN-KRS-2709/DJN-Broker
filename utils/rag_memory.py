"""
RAG Memory System for Trading Bot

Stores and retrieves historical insights, market conditions, and trade outcomes
using ChromaDB for semantic search and long-term learning.
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from utils.logger import get_logger

log = get_logger("rag_memory")


class TradingMemory:
    """
    RAG-based memory system for the trading bot
    
    Features:
    - Store weekend insights with embeddings
    - Store trade outcomes and results
    - Query similar historical market conditions
    - Learn from past successes and failures
    """
    
    def __init__(self, storage_path: str = "./storage/chroma_db", model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the RAG memory system
        
        Args:
            storage_path: Path to store ChromaDB database
            model_name: Sentence transformer model for embeddings
        """
        self.storage_path = storage_path
        os.makedirs(storage_path, exist_ok=True)
        
        # Initialize ChromaDB
        log.info(f"🧠 Initializing RAG memory at {storage_path}")
        self.client = chromadb.PersistentClient(
            path=storage_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Initialize embedding model
        log.info(f"📦 Loading embedding model: {model_name}")
        self.embedding_model = SentenceTransformer(model_name)
        
        # Create collections
        self.insights_collection = self.client.get_or_create_collection(
            name="weekend_insights",
            metadata={"description": "Historical weekend analysis insights"}
        )
        
        self.trades_collection = self.client.get_or_create_collection(
            name="trade_outcomes",
            metadata={"description": "Historical trade results and outcomes"}
        )
        
        self.patterns_collection = self.client.get_or_create_collection(
            name="market_patterns",
            metadata={"description": "Identified market patterns and conditions"}
        )
        
        log.info("✅ RAG memory initialized successfully")
    
    def store_weekend_insight(self, insight: Dict, timestamp: str = None):
        """
        Store a single weekend insight with embedding
        
        Args:
            insight: Dictionary with ticker, signal, confidence, reasoning, etc.
            timestamp: ISO timestamp (defaults to now)
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        ticker = insight.get('ticker', 'UNKNOWN')
        signal = insight.get('signal', 'NEUTRAL')
        confidence = insight.get('confidence', 0.0)
        reasoning = insight.get('reasoning', '')
        key_factors = insight.get('key_factors', [])
        risk_factors = insight.get('risk_factors', [])
        
        # Create text for embedding
        text = f"""
        Ticker: {ticker}
        Signal: {signal}
        Confidence: {confidence}
        Reasoning: {reasoning}
        Key Factors: {', '.join(key_factors)}
        Risk Factors: {', '.join(risk_factors)}
        """.strip()
        
        # Generate embedding
        embedding = self.embedding_model.encode(text).tolist()
        
        # Create unique ID
        doc_id = f"{ticker}_{timestamp}"
        
        # Store in ChromaDB
        self.insights_collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                'ticker': ticker,
                'signal': signal,
                'confidence': confidence,
                'timestamp': timestamp,
                'reasoning': reasoning,
                'key_factors': json.dumps(key_factors),
                'risk_factors': json.dumps(risk_factors)
            }],
            ids=[doc_id]
        )
        
        log.debug(f"💾 Stored insight: {ticker} {signal} (confidence: {confidence:.2f})")
    
    def store_weekend_analysis(self, analysis: Dict):
        """
        Store entire weekend analysis with all insights
        
        Args:
            analysis: Full weekend analysis output from Tree of Thoughts
        """
        timestamp = analysis.get('timestamp', datetime.now().isoformat())
        insights = analysis.get('insights', [])
        hypotheses = analysis.get('top_hypotheses', [])
        
        log.info(f"💾 Storing weekend analysis: {len(insights)} insights, {len(hypotheses)} hypotheses")
        
        # Store each insight
        for insight in insights:
            self.store_weekend_insight(insight, timestamp)
        
        # Store overall market pattern
        market_summary = f"""
        Weekend Analysis - {timestamp}
        Total Insights: {len(insights)}
        Top Signals: {', '.join([f"{i['ticker']}:{i['signal']}" for i in insights[:5]])}
        Hypotheses Evaluated: {analysis.get('hypotheses_evaluated', 0)}
        """.strip()
        
        embedding = self.embedding_model.encode(market_summary).tolist()
        
        self.patterns_collection.add(
            embeddings=[embedding],
            documents=[market_summary],
            metadatas=[{
                'timestamp': timestamp,
                'num_insights': len(insights),
                'analysis_type': analysis.get('analysis_type', 'weekend_tree_of_thoughts')
            }],
            ids=[f"pattern_{timestamp}"]
        )
        
        log.info(f"✅ Weekend analysis stored successfully")
    
    def query_similar_insights(self, ticker: str, signal: str = None, n_results: int = 5) -> List[Dict]:
        """
        Find similar historical insights for a ticker
        
        Args:
            ticker: Stock ticker to query
            signal: Optional signal type filter (BULLISH, BEARISH, NEUTRAL)
            n_results: Number of results to return
            
        Returns:
            List of similar historical insights
        """
        query_text = f"Ticker: {ticker}"
        if signal:
            query_text += f" Signal: {signal}"
        
        query_embedding = self.embedding_model.encode(query_text).tolist()
        
        # Query with metadata filter
        where_filter = {'ticker': ticker}
        if signal:
            where_filter['signal'] = signal
        
        try:
            results = self.insights_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where=where_filter if signal else {'ticker': ticker}
            )
            
            # Parse results
            insights = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    metadata = results['metadatas'][0][i]
                    insights.append({
                        'ticker': metadata.get('ticker'),
                        'signal': metadata.get('signal'),
                        'confidence': metadata.get('confidence'),
                        'timestamp': metadata.get('timestamp'),
                        'reasoning': metadata.get('reasoning'),
                        'key_factors': json.loads(metadata.get('key_factors', '[]')),
                        'risk_factors': json.loads(metadata.get('risk_factors', '[]')),
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return insights
        except Exception as e:
            log.warning(f"Query failed: {e}")
            return []
    
    def query_market_conditions(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Find similar historical market conditions
        
        Args:
            query: Natural language query (e.g., "high volatility tech stocks bullish")
            n_results: Number of results to return
            
        Returns:
            List of similar market conditions
        """
        query_embedding = self.embedding_model.encode(query).tolist()
        
        try:
            results = self.patterns_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results
            )
            
            patterns = []
            if results['documents']:
                for i in range(len(results['documents'][0])):
                    metadata = results['metadatas'][0][i]
                    patterns.append({
                        'timestamp': metadata.get('timestamp'),
                        'num_insights': metadata.get('num_insights'),
                        'summary': results['documents'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })
            
            return patterns
        except Exception as e:
            log.warning(f"Query failed: {e}")
            return []
    
    def store_trade_outcome(self, trade: Dict):
        """
        Store trade outcome for learning
        
        Args:
            trade: Trade information with outcome
        """
        timestamp = trade.get('timestamp', datetime.now().isoformat())
        ticker = trade.get('ticker', 'UNKNOWN')
        action = trade.get('action', 'BUY')
        entry_price = trade.get('entry_price', 0.0)
        exit_price = trade.get('exit_price', 0.0)
        outcome = trade.get('outcome', 'OPEN')  # OPEN, WIN, LOSS, NEUTRAL
        pnl = trade.get('pnl', 0.0)
        reasoning = trade.get('reasoning', '')
        
        text = f"""
        Trade: {ticker} {action}
        Entry: ${entry_price:.2f}
        Exit: ${exit_price:.2f}
        Outcome: {outcome}
        PnL: ${pnl:.2f}
        Reasoning: {reasoning}
        """.strip()
        
        embedding = self.embedding_model.encode(text).tolist()
        
        doc_id = f"trade_{ticker}_{timestamp}"
        
        self.trades_collection.add(
            embeddings=[embedding],
            documents=[text],
            metadatas=[{
                'ticker': ticker,
                'action': action,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'outcome': outcome,
                'pnl': pnl,
                'timestamp': timestamp,
                'reasoning': reasoning
            }],
            ids=[doc_id]
        )
        
        log.info(f"💰 Stored trade outcome: {ticker} {outcome} (PnL: ${pnl:.2f})")
    
    def get_ticker_history(self, ticker: str, n_results: int = 10) -> Dict:
        """
        Get complete history for a ticker (insights + trades)
        
        Args:
            ticker: Stock ticker
            n_results: Number of results per category
            
        Returns:
            Dictionary with insights and trades
        """
        log.info(f"📚 Retrieving history for {ticker}")
        
        # Get insights
        insights = self.query_similar_insights(ticker, n_results=n_results)
        
        # Get trades
        query_text = f"Trade: {ticker}"
        query_embedding = self.embedding_model.encode(query_text).tolist()
        
        try:
            trade_results = self.trades_collection.query(
                query_embeddings=[query_embedding],
                n_results=n_results,
                where={'ticker': ticker}
            )
            
            trades = []
            if trade_results['documents']:
                for i in range(len(trade_results['documents'][0])):
                    metadata = trade_results['metadatas'][0][i]
                    trades.append({
                        'ticker': metadata.get('ticker'),
                        'action': metadata.get('action'),
                        'outcome': metadata.get('outcome'),
                        'pnl': metadata.get('pnl'),
                        'timestamp': metadata.get('timestamp'),
                        'reasoning': metadata.get('reasoning')
                    })
        except Exception as e:
            log.warning(f"Trade query failed: {e}")
            trades = []
        
        return {
            'ticker': ticker,
            'insights': insights,
            'trades': trades,
            'total_insights': len(insights),
            'total_trades': len(trades)
        }
    
    def get_stats(self) -> Dict:
        """Get memory statistics"""
        try:
            insights_count = self.insights_collection.count()
            trades_count = self.trades_collection.count()
            patterns_count = self.patterns_collection.count()
            
            return {
                'total_insights': insights_count,
                'total_trades': trades_count,
                'total_patterns': patterns_count,
                'storage_path': self.storage_path
            }
        except Exception as e:
            log.error(f"Failed to get stats: {e}")
            return {}

