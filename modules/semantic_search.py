"""
semantic_search.py - Semantic search over processed paper chunks.
Returns ranked results with similarity scores and source attribution.
"""

import logging
from dataclasses import dataclass
from typing import List

from modules.embeddings import EmbeddingEngine
from modules.chunking import TextChunk

logger = logging.getLogger("SmartPaperAnalyst.SemanticSearch")


@dataclass
class SearchResult:
    """A single semantic search result."""
    chunk: TextChunk
    score: float
    score_pct: str
    rank: int

    @property
    def paper_name(self) -> str:
        return self.chunk.paper_display_name

    @property
    def preview(self) -> str:
        """First 300 chars of the chunk as a preview."""
        return self.chunk.text[:300].strip() + ("..." if len(self.chunk.text) > 300 else "")


class SemanticSearchEngine:
    """Performs semantic search over indexed paper chunks."""

    def __init__(self, embedding_engine: EmbeddingEngine):
        self.engine = embedding_engine

    def search(self, query: str, top_k: int = 8) -> List[SearchResult]:
        """
        Semantic search returning ranked results with scores.
        """
        if not query or not query.strip():
            logger.warning("Empty search query")
            return []
        
        if not self.engine.is_ready:
            logger.warning("Search engine not ready")
            return []

        try:
            query = query.strip()
            if len(query) > 500:
                logger.warning(f"Query truncated from {len(query)} to 500 chars")
                query = query[:500]
            
            raw_results = self.engine.search(query, top_k=top_k)
        except ValueError as e:
            logger.error(f"Invalid search query: {e}")
            raise RuntimeError(f"Invalid search query: {str(e)}")
        except RuntimeError as e:
            logger.error(f"Search engine error: {e}")
            raise
        except Exception as e:
            logger.error(f"Semantic search failed: {e}", exc_info=True)
            raise RuntimeError(f"Search failed: {str(e)}")

        results = []
        for rank, (chunk, score) in enumerate(raw_results, 1):
            score_pct = f"{score * 100:.1f}%"
            results.append(SearchResult(
                chunk=chunk,
                score=score,
                score_pct=score_pct,
                rank=rank,
            ))

        logger.info(f"Semantic search '{query[:50]}' → {len(results)} results")
        return results
