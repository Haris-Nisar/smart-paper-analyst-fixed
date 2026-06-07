"""
embeddings.py - Embedding generation and FAISS vector store management.
Uses sentence-transformers all-MiniLM-L6-v2 for fast, high-quality embeddings.
"""

import os
import logging
import numpy as np
from typing import List, Optional, Tuple

import faiss
from sentence_transformers import SentenceTransformer

from modules.chunking import TextChunk
from utils.config import config
from utils.helpers import save_pickle, load_pickle, ensure_directories

logger = logging.getLogger("SmartPaperAnalyst.Embeddings")


class EmbeddingEngine:
    """
    Manages:
    - Sentence-transformer embedding generation
    - FAISS index creation, saving, and loading
    - Semantic similarity search
    """

    def __init__(self, model_name: str = None):
        self.model_name = model_name or config.EMBEDDING_MODEL
        self._model: Optional[SentenceTransformer] = None
        self._model_load_error: Optional[str] = None
        self.index: Optional[faiss.IndexFlatIP] = None   # Inner Product (cosine-like)
        self.chunks: List[TextChunk] = []
        self.embeddings: Optional[np.ndarray] = None

        ensure_directories(config.VECTOR_STORE_DIR)
        logger.info(f"EmbeddingEngine initialized with model: {self.model_name}")

    @property
    def model(self) -> SentenceTransformer:
        """Lazy-load the embedding model (only when first needed)."""
        if self._model is None:
            if self._model_load_error:
                raise RuntimeError(self._model_load_error)
            
            try:
                logger.info(f"Loading embedding model: {self.model_name}")
                self._model = SentenceTransformer(self.model_name)
                logger.info("Embedding model loaded successfully")
            except Exception as e:
                error_msg = f"Failed to load embedding model '{self.model_name}': {str(e)}"
                logger.error(error_msg, exc_info=True)
                self._model_load_error = error_msg
                raise RuntimeError(error_msg)
        
        return self._model

    def embed_texts(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        """
        Generate normalized embeddings for a list of texts.
        Normalization enables cosine similarity via inner product.
        """
        logger.info(f"Generating embeddings for {len(texts)} texts...")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=False,
            normalize_embeddings=True,   # L2-normalize → cosine sim via inner product
            convert_to_numpy=True,
        )
        logger.info(f"Embeddings shape: {embeddings.shape}")
        return embeddings.astype(np.float32)

    def build_index(self, chunks: List[TextChunk]) -> None:
        """
        Build a FAISS index from a list of text chunks.
        Uses IndexFlatIP (inner product) for cosine similarity search.
        """
        if not chunks:
            raise ValueError("Cannot build index: no chunks provided.")

        logger.info(f"Building index with {len(chunks)} chunks...")
        self.chunks = chunks
        texts = [chunk.text for chunk in chunks]

        # Generate embeddings
        logger.info("Generating embeddings...")
        self.embeddings = self.embed_texts(texts)

        # Build FAISS index
        dim = self.embeddings.shape[1]
        logger.info(f"Creating FAISS index (dimension={dim})...")
        self.index = faiss.IndexFlatIP(dim)  # Inner Product for normalized vectors
        self.index.add(self.embeddings)

        logger.info(
            f"✅ FAISS index built: {self.index.ntotal} vectors, dim={dim}"
        )

    def search(
        self, query: str, top_k: int = None
    ) -> List[Tuple[TextChunk, float]]:
        """
        Semantic similarity search.
        Returns list of (TextChunk, similarity_score) sorted by relevance.
        """
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        if self.index is None or not self.chunks:
            raise RuntimeError("Index not built. Please process papers first.")

        # Normalize top_k to available chunks
        k = min(top_k or config.TOP_K_RETRIEVAL, len(self.chunks), self.index.ntotal)
        
        if k <= 0:
            logger.warning("No chunks available for search")
            return []

        # Embed the query
        query_embedding = self.embed_texts([query])  # shape: (1, dim)

        # Search FAISS
        scores, indices = self.index.search(query_embedding, k)

        # Log all scores for debugging
        logger.info(f"🔍 FAISS search - Top {k} scores: {scores[0]}")
        logger.info(f"   Threshold: {config.SIMILARITY_THRESHOLD}")

        results = []
        for rank, (score, idx) in enumerate(zip(scores[0], indices[0]), 1):
            if idx == -1:  # FAISS returns -1 for invalid indices
                continue
            if idx >= len(self.chunks):
                logger.warning(f"Invalid chunk index {idx}, skipping")
                continue
            
            passed_threshold = score >= config.SIMILARITY_THRESHOLD
            status = "✅ PASS" if passed_threshold else "❌ FAIL"
            chunk_name = self.chunks[idx].paper_display_name
            logger.info(f"   [{rank}] {status} Score={score:.4f} | {chunk_name}")
            
            if passed_threshold:
                results.append((self.chunks[idx], float(score)))

        logger.info(f"✅ Search returned {len(results)}/{k} results for query: '{query[:60]}'")
        return results

    def save_index(
        self,
        index_path: str = None,
        metadata_path: str = None,
    ) -> None:
        """Save FAISS index and chunk metadata to disk for reuse."""
        if self.index is None:
            raise RuntimeError("No index to save.")

        idx_path = index_path or config.FAISS_INDEX_PATH
        meta_path = metadata_path or config.FAISS_METADATA_PATH

        ensure_directories(os.path.dirname(idx_path))

        faiss.write_index(self.index, idx_path)
        save_pickle({"chunks": self.chunks, "embeddings": self.embeddings}, meta_path)

        logger.info(f"Index saved: {idx_path} | Metadata: {meta_path}")

    def load_index(
        self,
        index_path: str = None,
        metadata_path: str = None,
    ) -> bool:
        """
        Load FAISS index and metadata from disk.
        Returns True if successful, False otherwise.
        Safely handles corrupted files without hanging.
        """
        idx_path = index_path or config.FAISS_INDEX_PATH
        meta_path = metadata_path or config.FAISS_METADATA_PATH

        if not os.path.exists(idx_path) or not os.path.exists(meta_path):
            logger.info("No saved index found.")
            return False

        try:
            # Try to load index with a timeout approach
            # If files are corrupted, log and return False gracefully
            logger.info(f"Attempting to load FAISS index from {idx_path}")
            self.index = faiss.read_index(idx_path)
            
            # Verify index is valid
            if self.index is None or self.index.ntotal == 0:
                logger.warning("Loaded index is empty or invalid")
                self.index = None
                return False
                
            data = load_pickle(meta_path)
            if data:
                self.chunks = data.get("chunks", [])
                self.embeddings = data.get("embeddings")
                
                if not self.chunks:
                    logger.warning("Loaded metadata has no chunks")
                    self.index = None
                    return False
                    
            logger.info(f"Index loaded successfully: {self.index.ntotal} vectors, {len(self.chunks)} chunks")
            return True
            
        except EOFError as e:
            logger.error(f"Index file is corrupted or incomplete: {e}")
            self.index = None
            return False
        except Exception as e:
            logger.error(f"Failed to load index: {e}", exc_info=True)
            self.index = None
            return False

    def clear_index(self) -> None:
        """Clear the current index and chunks from memory."""
        self.index = None
        self.chunks = []
        self.embeddings = None
        logger.info("Index cleared from memory.")

    @property
    def is_ready(self) -> bool:
        """Check if the index is built and ready for search."""
        return self.index is not None and len(self.chunks) > 0

    def get_stats(self) -> dict:
        """Return index statistics."""
        if not self.is_ready:
            return {"status": "Not built"}
        papers = list({c.paper_display_name for c in self.chunks})
        return {
            "status": "Ready",
            "total_vectors": self.index.ntotal,
            "total_chunks": len(self.chunks),
            "num_papers": len(papers),
            "papers": papers,
            "embedding_model": self.model_name,
        }
