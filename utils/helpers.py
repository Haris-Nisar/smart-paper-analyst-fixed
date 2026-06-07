"""
helpers.py - General utility functions used across the application.
"""

import os
import re
import time
import logging
import hashlib
import pickle
from typing import Optional
from datetime import datetime

# ─── Logging Setup ─────────────────────────────────────────────────────────
import sys

# Create logger
logger = logging.getLogger("SmartPaperAnalyst")
logger.setLevel(logging.INFO)

# Avoid duplicate handlers
if not logger.handlers:
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Format
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s — %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)

# Prevent propagation to avoid duplicate logs
logger.propagate = False


def get_file_hash(file_bytes: bytes) -> str:
    """Generate a unique MD5 hash for a file to detect duplicates."""
    return hashlib.md5(file_bytes).hexdigest()


def clean_text(text: str) -> str:
    """
    Clean raw extracted PDF text.
    - Remove excessive whitespace and newlines
    - Remove non-printable characters
    - Preserve paragraph structure
    """
    if not text:
        return ""

    # Remove non-printable characters (keep standard ASCII + unicode letters)
    text = re.sub(r'[^\x20-\x7E\u00C0-\u024F\u0370-\u03FF\n\r\t]', ' ', text)

    # Normalize multiple spaces to single space
    text = re.sub(r'[ \t]+', ' ', text)

    # Normalize multiple newlines (preserve paragraph breaks)
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove lines that are just noise (single chars, page numbers, etc.)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        # Skip lines shorter than 3 chars (likely noise)
        if len(stripped) >= 3 or stripped == '':
            cleaned_lines.append(stripped)

    text = '\n'.join(cleaned_lines)
    return text.strip()


def truncate_text(text: str, max_chars: int = 10000) -> str:
    """Truncate text to a maximum character limit for LLM context windows."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + "\n\n[... Content truncated for processing ...]"


def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human-readable file size."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 ** 2:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 ** 3:
        return f"{size_bytes / (1024**2):.1f} MB"
    return f"{size_bytes / (1024**3):.1f} GB"


def validate_pdf_file(file_bytes: bytes, filename: str, max_size_mb: int = 50) -> tuple[bool, str]:
    """
    Validate an uploaded PDF file.
    Returns (is_valid, error_message).
    """
    # Check extension
    if not filename.lower().endswith('.pdf'):
        return False, f"'{filename}' is not a PDF file."

    # Check file size
    size_mb = len(file_bytes) / (1024 ** 2)
    if size_mb > max_size_mb:
        return False, f"'{filename}' is too large ({size_mb:.1f} MB). Max allowed: {max_size_mb} MB."

    # Check PDF magic bytes
    if not file_bytes.startswith(b'%PDF'):
        return False, f"'{filename}' does not appear to be a valid PDF file."

    return True, ""


def ensure_directories(*dirs: str) -> None:
    """Create directories if they don't exist."""
    for d in dirs:
        os.makedirs(d, exist_ok=True)


def save_pickle(data: object, path: str) -> None:
    """Save Python object to pickle file."""
    ensure_directories(os.path.dirname(path) if os.path.dirname(path) else ".")
    with open(path, 'wb') as f:
        pickle.dump(data, f)
    logger.info(f"Saved pickle to {path}")


def load_pickle(path: str) -> Optional[object]:
    """Load Python object from pickle file. Returns None if not found."""
    if not os.path.exists(path):
        return None
    try:
        with open(path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        logger.error(f"Failed to load pickle from {path}: {e}")
        return None


def get_timestamp() -> str:
    """Return formatted current timestamp."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def extract_paper_name(filename: str) -> str:
    """Extract a clean display name from a PDF filename."""
    name = os.path.splitext(filename)[0]
    # Replace underscores/hyphens with spaces
    name = re.sub(r'[_\-]+', ' ', name)
    # Title-case
    return name.strip().title()


def format_similarity_score(score: float) -> str:
    """Format FAISS similarity score as percentage."""
    # FAISS L2 distance: lower = more similar; cosine: higher = more similar
    pct = max(0.0, min(1.0, score)) * 100
    return f"{pct:.1f}%"


def chunk_list(lst: list, n: int) -> list:
    """Split a list into chunks of size n."""
    return [lst[i:i + n] for i in range(0, len(lst), n)]
