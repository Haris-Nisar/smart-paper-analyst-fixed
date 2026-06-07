"""
chunking.py - Intelligent text chunking using LangChain's RecursiveCharacterTextSplitter.
Preserves semantic meaning by splitting on natural boundaries (paragraphs, sentences).
"""

import logging
from dataclasses import dataclass
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from modules.pdf_processor import ProcessedPaper
from utils.config import config

logger = logging.getLogger("SmartPaperAnalyst.Chunking")


@dataclass
class TextChunk:
    """Represents a single text chunk with its metadata."""
    chunk_id: str
    text: str
    paper_filename: str
    paper_display_name: str
    chunk_index: int
    total_chunks: int
    word_count: int

    def __repr__(self):
        return f"TextChunk(paper='{self.paper_display_name}', idx={self.chunk_index}, words={self.word_count})"


class TextChunker:
    """
    Splits processed paper text into overlapping semantic chunks
    for embedding and retrieval.
    """

    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or config.CHUNK_SIZE
        self.chunk_overlap = chunk_overlap or config.CHUNK_OVERLAP

        # RecursiveCharacterTextSplitter splits on paragraphs → sentences → words
        # This preserves semantic boundaries much better than fixed-character splits
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=len,
            separators=[
                "\n\n",   # Paragraphs (highest priority)
                "\n",     # Lines
                ". ",     # Sentences
                "! ",
                "? ",
                "; ",
                ", ",
                " ",      # Words (last resort)
                "",       # Characters (absolute last resort)
            ],
            is_separator_regex=False,
        )

        logger.info(
            f"TextChunker initialized: chunk_size={self.chunk_size}, "
            f"overlap={self.chunk_overlap}"
        )

    def chunk_paper(self, paper: ProcessedPaper) -> List[TextChunk]:
        """
        Chunk a single processed paper into TextChunk objects.
        Each chunk retains paper metadata for retrieval attribution.
        """
        if not paper.full_text.strip():
            logger.warning(f"Paper '{paper.display_name}' has no text to chunk.")
            return []

        # Split the full text
        raw_chunks = self.splitter.split_text(paper.full_text)

        # Filter out very short chunks (less than 50 chars — likely noise)
        raw_chunks = [c for c in raw_chunks if len(c.strip()) >= 50]

        total = len(raw_chunks)
        chunks = []

        for idx, chunk_text in enumerate(raw_chunks):
            chunk = TextChunk(
                chunk_id=f"{paper.file_hash}_{idx}",
                text=chunk_text.strip(),
                paper_filename=paper.filename,
                paper_display_name=paper.display_name,
                chunk_index=idx,
                total_chunks=total,
                word_count=len(chunk_text.split()),
            )
            chunks.append(chunk)

        logger.info(
            f"Chunked '{paper.display_name}': {total} chunks "
            f"(avg {sum(c.word_count for c in chunks) // max(1, total)} words each)"
        )
        return chunks

    def chunk_multiple_papers(self, papers: List[ProcessedPaper]) -> List[TextChunk]:
        """
        Chunk multiple papers and return a combined flat list of all chunks.
        Handles errors gracefully.
        """
        if not papers:
            logger.warning("No papers provided for chunking")
            return []
        
        all_chunks = []
        for paper in papers:
            try:
                paper_chunks = self.chunk_paper(paper)
                all_chunks.extend(paper_chunks)
            except Exception as e:
                logger.error(f"Failed to chunk '{paper.display_name}': {e}", exc_info=True)
                continue

        if not all_chunks:
            logger.warning(f"No chunks created from {len(papers)} papers")
        else:
            logger.info(f"Total chunks across {len(papers)} papers: {len(all_chunks)}")
        
        return all_chunks

    def get_chunk_stats(self, chunks: List[TextChunk]) -> dict:
        """Return useful statistics about the chunked corpus."""
        if not chunks:
            return {}

        word_counts = [c.word_count for c in chunks]
        papers = list({c.paper_display_name for c in chunks})

        return {
            "total_chunks": len(chunks),
            "num_papers": len(papers),
            "avg_words_per_chunk": sum(word_counts) // len(word_counts),
            "min_words": min(word_counts),
            "max_words": max(word_counts),
            "total_words": sum(word_counts),
            "papers": papers,
        }
