"""
Advanced Semantic Retrieval System

Features:
- Multi-query retrieval for better coverage
- Intelligent fallback strategies
- Semantic reranking and merging
- Neighboring chunk expansion
- Confidence scoring

Never gives up - finds the best available answer.
"""

import numpy as np
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class RetrievedChunk:
    """Single retrieved chunk with metadata"""
    content: str
    source: str
    score: float
    chunk_index: int
    query_index: int  # Which query retrieved this
    is_fallback: bool = False
    neighbor_offset: int = 0  # Distance from original chunk


@dataclass
class RetrievalResult:
    """Complete retrieval result with ranking and analysis"""
    chunks: List[RetrievedChunk]
    query_used: str
    queries_attempted: List[str]
    confidence: float
    is_fallback: bool
    analysis: str = ""


class SemanticRetriever:
    """
    Advanced semantic retriever with fallback logic.
    
    Never says "no information" - finds the best possible answer.
    """
    
    def __init__(self, embedding_engine, debug: bool = False):
        """
        Initialize semantic retriever.
        
        Args:
            embedding_engine: The FAISS embedding engine
            debug: Enable debug logging
        """
        self.embedding_engine = embedding_engine
        self.debug = debug
        self.retrieval_history = []
    
    def retrieve_semantic(
        self,
        queries: List[str],
        top_k: int = 8,
        strategy: str = "merge"
    ) -> Optional[RetrievalResult]:
        """
        Retrieve chunks using multiple queries with fallback strategy.
        
        Args:
            queries: List of query variations to try
            top_k: Number of chunks to retrieve
            strategy: "merge" (combine all), "best" (use best results), "expand" (add neighbors)
            
        Returns:
            RetrievalResult with chunks and metadata, or None if all retrieval fails
        """
        if not queries:
            return None
        
        all_chunks = []
        queries_attempted = []
        fallback_used = False
        
        # Try each query
        for query_idx, query in enumerate(queries):
            if not query or len(query.strip()) < 2:
                continue
            
            try:
                chunks = self._retrieve_single(query, top_k)
                if chunks:
                    # Add query index to each chunk
                    for chunk in chunks:
                        chunk.query_index = query_idx
                    all_chunks.extend(chunks)
                    queries_attempted.append(query)
                    
                    if self.debug:
                        logger.info(f"Query {query_idx}: Retrieved {len(chunks)} chunks")
            
            except Exception as e:
                logger.warning(f"Retrieval failed for query: {query}. Error: {e}")
                continue
        
        # If no results, try fallback strategies
        if not all_chunks:
            logger.info("No results from initial queries. Attempting fallback strategies...")
            result = self._fallback_retrieval(queries, top_k)
            if result:
                result.queries_attempted = queries_attempted
                return result
            else:
                # Even fallback failed
                return RetrievalResult(
                    chunks=[],
                    query_used="all queries failed",
                    queries_attempted=queries_attempted,
                    confidence=0.0,
                    is_fallback=True,
                    analysis="All retrieval strategies exhausted. Document may not contain relevant information."
                )
        
        # Merge and rank results
        merged = self._merge_and_rank(all_chunks, strategy)
        
        # Expand with neighboring chunks for context
        expanded = self._expand_with_neighbors(merged, top_k)
        
        # Calculate confidence
        confidence = self._calculate_retrieval_confidence(merged)
        
        analysis = self._generate_retrieval_analysis(
            queries_attempted, len(merged), confidence
        )
        
        return RetrievalResult(
            chunks=expanded[:top_k],
            query_used=queries_attempted[0] if queries_attempted else "unknown",
            queries_attempted=queries_attempted,
            confidence=confidence,
            is_fallback=fallback_used,
            analysis=analysis
        )
    
    def _retrieve_single(self, query: str, top_k: int) -> List[RetrievedChunk]:
        """Retrieve chunks for a single query using EmbeddingEngine.search()."""
        try:
            # Check readiness via property (not method call)
            if not self.embedding_engine.is_ready:
                logger.warning("Embedding engine not ready")
                return []

            # EmbeddingEngine.search() accepts a query string and returns
            # List[Tuple[TextChunk, float]] filtered by similarity threshold
            results = self.embedding_engine.search(query, top_k=top_k * 2)

            chunks = []
            for text_chunk, score in results:
                # Resolve chunk index from the engine's chunk list
                try:
                    idx = self.embedding_engine.chunks.index(text_chunk)
                except ValueError:
                    idx = -1

                chunk = RetrievedChunk(
                    content=text_chunk.text,
                    source=text_chunk.paper_display_name,
                    score=float(score),
                    chunk_index=idx,
                    query_index=0,
                )
                chunks.append(chunk)

            return chunks[:top_k]

        except Exception as e:
            logger.error(f"Error in single retrieval: {e}", exc_info=True)
            return []
    
    def _fallback_retrieval(self, queries: List[str], top_k: int) -> Optional[RetrievalResult]:
        """
        Intelligent fallback strategies when initial retrieval fails.
        
        Strategies (in order):
        1. Broader semantic search
        2. Topic extraction and search
        3. Generic high-level search
        4. Return nearest neighbors from vector space
        """
        strategies = [
            ("broader_search", self._broader_semantic_search),
            ("concept_search", self._concept_based_search),
            ("generic_search", self._generic_search),
            ("nearest_neighbors", self._nearest_neighbors_fallback),
        ]
        
        for strategy_name, strategy_fn in strategies:
            logger.info(f"Attempting fallback: {strategy_name}")
            try:
                chunks = strategy_fn(queries, top_k)
                if chunks:
                    logger.info(f"Fallback successful using {strategy_name}: {len(chunks)} chunks")
                    return RetrievalResult(
                        chunks=chunks,
                        query_used=f"fallback_{strategy_name}",
                        queries_attempted=[],
                        confidence=0.5,
                        is_fallback=True,
                        analysis=f"Initial retrieval found no results. Using {strategy_name} fallback."
                    )
            except Exception as e:
                logger.warning(f"Fallback strategy {strategy_name} failed: {e}")
                continue
        
        return None
    
    def _broader_semantic_search(self, queries: List[str], top_k: int) -> List[RetrievedChunk]:
        """
        Try broader search by removing specific terms.
        
        E.g., "What are the training steps?" → "training"
        """
        results = []
        
        for query in queries:
            # Extract shorter key terms
            words = query.split()
            if len(words) > 2:
                # Try progressively shorter queries
                for length in [len(words) - 1, len(words) - 2, 1]:
                    if length > 0:
                        shorter = " ".join(words[:length])
                        chunks = self._retrieve_single(shorter, top_k)
                        if chunks:
                            results.extend(chunks)
                            break
        
        return results[:top_k] if results else []
    
    def _concept_based_search(self, queries: List[str], top_k: int) -> List[RetrievedChunk]:
        """
        Search for high-level concepts related to queries.
        
        E.g., "training method" → search for "algorithm", "process", "approach"
        """
        concept_keywords = [
            "methodology", "approach", "technique", "process",
            "algorithm", "system", "framework", "architecture",
            "overview", "introduction", "background"
        ]
        
        results = []
        for keyword in concept_keywords:
            chunks = self._retrieve_single(keyword, top_k // 2)
            if chunks:
                results.extend(chunks)
        
        return results[:top_k] if results else []
    
    def _generic_search(self, queries: List[str], top_k: int) -> List[RetrievedChunk]:
        """
        Last resort: search for very generic terms.
        
        This ensures at least some context is available.
        """
        generic_terms = ["important", "significant", "key", "main"]
        
        results = []
        for term in generic_terms:
            chunks = self._retrieve_single(term, top_k // len(generic_terms))
            if chunks:
                results.extend(chunks)
        
        return results[:top_k] if results else []
    
    def _nearest_neighbors_fallback(self, queries: List[str], top_k: int) -> List[RetrievedChunk]:
        """
        Final fallback: return chunks near center of vector space.
        
        Ensures something is always returned.
        """
        try:
            # Create a zero vector (or center vector)
            dummy_query = " ".join(queries) if queries else "general information"
            chunks = self._retrieve_single(dummy_query, top_k * 2)
            
            # Return highest scored chunks
            return sorted(chunks, key=lambda c: c.score, reverse=True)[:top_k]
        
        except Exception as e:
            logger.error(f"Nearest neighbors fallback failed: {e}")
            return []
    
    def _merge_and_rank(
        self,
        chunks: List[RetrievedChunk],
        strategy: str = "merge"
    ) -> List[RetrievedChunk]:
        """
        Merge and rank chunks from multiple queries.
        
        Strategies:
        - merge: Combine all, rank by score
        - best: Keep only highest scoring
        - expand: Add neighboring chunks
        """
        if not chunks:
            return []
        
        if strategy == "best":
            return sorted(chunks, key=lambda c: c.score, reverse=True)
        
        elif strategy == "merge":
            # Deduplicate by content
            seen = {}
            merged = []
            
            for chunk in sorted(chunks, key=lambda c: c.score, reverse=True):
                # Simple dedup based on first 100 chars
                key = chunk.content[:100]
                if key not in seen:
                    seen[key] = True
                    merged.append(chunk)
            
            return merged
        
        else:  # expand
            return sorted(chunks, key=lambda c: c.score, reverse=True)
    
    def _expand_with_neighbors(
        self,
        chunks: List[RetrievedChunk],
        target_size: int
    ) -> List[RetrievedChunk]:
        """
        Expand results by including neighboring chunks for context.
        
        For each top chunk, add adjacent chunks to provide better context.
        """
        expanded = list(chunks)  # Start with original
        
        for chunk in chunks[:3]:  # Expand top 3 chunks
            # Try to find neighboring chunks
            for offset in [-1, 1]:  # Neighbors above and below
                neighbor_idx = chunk.chunk_index + offset
                
                try:
                    neighbor_content = self._get_chunk_content(neighbor_idx)
                    if neighbor_content and neighbor_content not in [c.content for c in expanded]:
                        neighbor = RetrievedChunk(
                            content=neighbor_content,
                            source=f"chunk_{neighbor_idx}",
                            score=chunk.score * 0.9,  # Slightly lower score
                            chunk_index=neighbor_idx,
                            query_index=chunk.query_index,
                            is_fallback=False,
                            neighbor_offset=offset
                        )
                        expanded.append(neighbor)
                
                except Exception:
                    continue
        
        return expanded[:target_size]
    
    def _calculate_retrieval_confidence(self, chunks: List[RetrievedChunk]) -> float:
        """
        Calculate confidence in retrieval results (0.0-1.0).
        
        Based on:
        - Number of chunks retrieved
        - Average score
        - Score variance
        """
        if not chunks:
            return 0.0
        
        confidence = 0.5  # Start at neutral
        
        # More chunks = higher confidence
        if len(chunks) >= 5:
            confidence += 0.2
        elif len(chunks) >= 3:
            confidence += 0.1
        
        # Higher scores = higher confidence
        avg_score = np.mean([c.score for c in chunks])
        if avg_score > 0.5:
            confidence += 0.2
        elif avg_score > 0.3:
            confidence += 0.1
        
        # Score variance (consistency)
        if len(chunks) > 1:
            scores = [c.score for c in chunks]
            variance = np.var(scores)
            if variance < 0.1:  # Low variance = consistent
                confidence += 0.1
        
        return min(confidence, 1.0)
    
    def _generate_retrieval_analysis(
        self,
        queries_attempted: List[str],
        chunks_found: int,
        confidence: float
    ) -> str:
        """Generate human-readable analysis of retrieval."""
        if chunks_found == 0:
            return "No relevant information found despite multiple retrieval strategies."
        
        confidence_text = "high" if confidence > 0.7 else "medium" if confidence > 0.4 else "low"
        
        return f"Retrieved {chunks_found} relevant chunks with {confidence_text} confidence using {len(queries_attempted)} query variations."
    
    def _get_chunk_content(self, index: int) -> Optional[str]:
        """Get chunk text content by index from the embedding engine."""
        try:
            if (
                hasattr(self.embedding_engine, 'chunks')
                and self.embedding_engine.chunks
                and 0 <= index < len(self.embedding_engine.chunks)
            ):
                chunk = self.embedding_engine.chunks[index]
                # TextChunk objects have a .text attribute
                if hasattr(chunk, 'text'):
                    return chunk.text
                return str(chunk)
        except Exception:
            pass
        return None
    
    def log_retrieval(self, result: RetrievalResult) -> None:
        """Log retrieval for analytics."""
        self.retrieval_history.append({
            "query": result.query_used,
            "chunks_retrieved": len(result.chunks),
            "confidence": result.confidence,
            "is_fallback": result.is_fallback,
        })
    
    def get_retrieval_stats(self) -> Dict:
        """Get retrieval statistics."""
        if not self.retrieval_history:
            return {"total_retrievals": 0}
        
        total = len(self.retrieval_history)
        fallbacks = sum(1 for r in self.retrieval_history if r["is_fallback"])
        avg_chunks = np.mean([r["chunks_retrieved"] for r in self.retrieval_history])
        avg_confidence = np.mean([r["confidence"] for r in self.retrieval_history])
        
        return {
            "total_retrievals": total,
            "fallback_count": fallbacks,
            "fallback_rate": fallbacks / total if total > 0 else 0,
            "avg_chunks_retrieved": avg_chunks,
            "avg_confidence": avg_confidence,
        }


def create_semantic_retriever(embedding_engine, debug: bool = False) -> SemanticRetriever:
    """Factory function to create semantic retriever."""
    return SemanticRetriever(embedding_engine, debug=debug)
