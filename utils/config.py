"""
config.py - Central configuration module for Smart Academic Paper Analyst
Handles all settings, API keys, model configs, and environment variables.
"""

import os
from dataclasses import dataclass, field
from typing import Optional

# ─── Load environment variables ───────────────────────────────────────────────
from dotenv import load_dotenv
load_dotenv()


@dataclass
class AppConfig:
    """Main application configuration."""

    # ── App Metadata ──
    APP_NAME: str = "Smart Academic Paper Analyst"
    APP_VERSION: str = "1.0.0"
    APP_ICON: str = "🔬"

    # ── LLM Provider ── (options: "openrouter", "mistral", "huggingface")
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "openrouter")

    # ── OpenRouter Settings ──
    OPENROUTER_API_KEY: str = os.getenv("OPENROUTER_API_KEY", "")
    OPENROUTER_BASE_URL: str = "https://openrouter.ai/api/v1"
    OPENROUTER_MODEL: str = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")

    # ── Mistral Direct API Settings ──
    MISTRAL_API_KEY: str = os.getenv("MISTRAL_API_KEY", "")
    MISTRAL_MODEL: str = "mistral-small-latest"

    # ── HuggingFace Settings ──
    HF_API_KEY: str = os.getenv("HF_API_KEY", "")
    HF_MODEL: str = "mistralai/Mistral-7B-Instruct-v0.1"

    # ── Embedding Model ──
    EMBEDDING_MODEL: str = "all-MiniLM-L6-v2"
    EMBEDDING_DIMENSION: int = 384

    # ── Chunking Settings (Advanced RAG) ──
    # Optimized for semantic boundaries and context preservation
    CHUNK_SIZE: int = 700           # 500-800 range: better semantic boundaries (~140-160 words)
    CHUNK_OVERLAP: int = 100        # 100-150 range: efficient overlap (~20-30 words)
    MAX_CHUNK_SIZE: int = 2000

    # ── Semantic Retrieval Settings (Advanced RAG) ──
    TOP_K_RETRIEVAL: int = 10       # 8-12 range: balance between context and noise
    SIMILARITY_THRESHOLD: float = 0.0   # Use 0.0 for IndexFlatIP (all inner products acceptable)
    
    # ── Advanced Query Understanding ──
    ENABLE_QUERY_REWRITING: bool = True     # Rewrite questions for better retrieval
    ENABLE_MULTI_QUERY: bool = True         # Generate multiple query variations
    ENABLE_SEMANTIC_FALLBACK: bool = True   # Use fallback strategies when initial retrieval fails
    
    # ── Semantic Reranking & Expansion ──
    ENABLE_NEIGHBOR_EXPANSION: bool = True  # Include neighboring chunks for context
    RETRIEVAL_MERGE_STRATEGY: str = "merge"  # "merge", "best", or "expand"
    
    # ── Retrieval Fallback Strategy (prevents hard failures) ──
    ENABLE_FALLBACK_STRATEGIES: bool = True
    FALLBACK_STRATEGIES: list = field(default_factory=lambda: [
        "broader_search",      # Try with fewer query terms
        "concept_search",      # Search for high-level concepts
        "generic_search",      # Search for generic keywords
        "nearest_neighbors",   # Return items near vector center
    ])

    # ── FAISS Settings ──
    FAISS_INDEX_PATH: str = "vector_store/faiss_index"
    FAISS_METADATA_PATH: str = "vector_store/metadata.pkl"

    # ── PDF Processing ──
    MAX_FILE_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list = field(default_factory=lambda: [".pdf"])

    # ── LLM Generation Settings ──
    MAX_TOKENS: int = 1024
    TEMPERATURE: float = 0.3        # Low temp for academic accuracy

    # ── UI Settings ──
    DEFAULT_THEME: str = "dark"
    CHAT_HISTORY_LIMIT: int = 50

    # ── Paths ──
    DATA_DIR: str = "data"
    VECTOR_STORE_DIR: str = "vector_store"
    STYLES_DIR: str = "styles"
    ASSETS_DIR: str = "assets"


# ─── Singleton config instance ─────────────────────────────────────────────
config = AppConfig()


def get_api_key() -> str:
    """Returns active LLM provider API key."""
    if config.LLM_PROVIDER == "openrouter":
        return config.OPENROUTER_API_KEY
    elif config.LLM_PROVIDER == "mistral":
        return config.MISTRAL_API_KEY
    elif config.LLM_PROVIDER == "huggingface":
        return config.HF_API_KEY
    return ""


def validate_config() -> tuple[bool, str]:
    """Validates configuration and returns (is_valid, error_message)."""
    key = get_api_key()
    if not key:
        provider = config.LLM_PROVIDER.upper()
        return False, (
            f"⚠️ {provider} API key not found. "
            f"Please set it in your .env file or Streamlit secrets."
        )
    return True, ""
