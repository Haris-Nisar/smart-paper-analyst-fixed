"""
pdf_processor.py - PDF text extraction using PyMuPDF (fitz).
Handles single/multiple PDFs, page-by-page extraction, and text cleaning.
"""

import io
import logging
from dataclasses import dataclass, field
from typing import List, Optional

import fitz  # PyMuPDF

from utils.helpers import clean_text, get_file_hash, validate_pdf_file, extract_paper_name

logger = logging.getLogger("SmartPaperAnalyst.PDFProcessor")


@dataclass
class ProcessedPaper:
    """Represents a fully processed research paper."""
    filename: str
    display_name: str
    file_hash: str
    full_text: str
    pages: List[str]           # Text per page
    num_pages: int
    num_words: int
    metadata: dict = field(default_factory=dict)

    def __repr__(self):
        return f"ProcessedPaper('{self.display_name}', {self.num_pages} pages, {self.num_words} words)"


class PDFProcessor:
    """
    Handles PDF loading, text extraction, and preprocessing.
    Uses PyMuPDF for fast, accurate text extraction.
    """

    def __init__(self, max_size_mb: int = 50):
        self.max_size_mb = max_size_mb
        logger.info("PDFProcessor initialized")

    def process_pdf(self, file_bytes: bytes, filename: str) -> tuple[Optional[ProcessedPaper], str]:
        """
        Process a single PDF file.
        Returns (ProcessedPaper, error_message). Error is empty string on success.
        """
        # ── Validate ──────────────────────────────────────────────────────────
        is_valid, error = validate_pdf_file(file_bytes, filename, self.max_size_mb)
        if not is_valid:
            return None, error

        try:
            # ── Open PDF from bytes ───────────────────────────────────────────
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")

            if pdf_doc.page_count == 0:
                return None, f"'{filename}' appears to be an empty PDF."

            # ── Extract text page by page ─────────────────────────────────────
            pages_text = []
            for page_num in range(pdf_doc.page_count):
                page = pdf_doc[page_num]

                # Extract text with layout preservation
                text = page.get_text("text")  # "text" mode preserves reading order
                cleaned = clean_text(text)

                if cleaned:
                    pages_text.append(cleaned)
                else:
                    pages_text.append("")  # Keep page index alignment

            pdf_doc.close()

            # ── Build full text ───────────────────────────────────────────────
            full_text = "\n\n".join(p for p in pages_text if p)

            if not full_text.strip():
                return None, (
                    f"'{filename}' contains no extractable text. "
                    "It may be a scanned image PDF (OCR not supported in this version)."
                )

            # ── Extract metadata ──────────────────────────────────────────────
            metadata = self._extract_metadata(file_bytes, filename)

            # ── Build result ──────────────────────────────────────────────────
            paper = ProcessedPaper(
                filename=filename,
                display_name=extract_paper_name(filename),
                file_hash=get_file_hash(file_bytes),
                full_text=full_text,
                pages=pages_text,
                num_pages=len(pages_text),
                num_words=len(full_text.split()),
                metadata=metadata,
            )

            logger.info(f"Processed '{filename}': {paper.num_pages} pages, {paper.num_words} words")
            return paper, ""

        except fitz.FileDataError as e:
            return None, f"'{filename}' is corrupted or not a valid PDF: {e}"
        except Exception as e:
            logger.error(f"Unexpected error processing '{filename}': {e}", exc_info=True)
            return None, f"Failed to process '{filename}': {str(e)}"

    def process_multiple_pdfs(
        self, uploaded_files: list
    ) -> tuple[List[ProcessedPaper], List[str]]:
        """
        Process multiple uploaded Streamlit file objects.
        Returns (successful_papers, error_messages).
        Includes detailed error reporting.
        """
        if not uploaded_files:
            return [], ["No files provided for processing."]
        
        papers = []
        errors = []

        for i, uploaded_file in enumerate(uploaded_files, 1):
            try:
                if not uploaded_file:
                    errors.append(f"File #{i}: Invalid file object")
                    continue
                
                file_bytes = uploaded_file.read()
                
                if not file_bytes:
                    errors.append(f"'{uploaded_file.name}': File is empty")
                    continue
                
                paper, error = self.process_pdf(file_bytes, uploaded_file.name)

                if paper:
                    papers.append(paper)
                    logger.info(f"Successfully processed: {uploaded_file.name}")
                else:
                    errors.append(error or f"'{uploaded_file.name}': Unknown error")

            except Exception as e:
                error_msg = f"'{uploaded_file.name}': {str(e)}"
                logger.error(error_msg, exc_info=True)
                errors.append(error_msg)

        logger.info(f"PDF processing complete: {len(papers)} successful, {len(errors)} errors")
        return papers, errors

    def _extract_metadata(self, file_bytes: bytes, filename: str) -> dict:
        """Extract PDF metadata (title, author, etc.) if available."""
        try:
            pdf_doc = fitz.open(stream=file_bytes, filetype="pdf")
            meta = pdf_doc.metadata or {}
            
            # Safely extract metadata with fallbacks
            metadata = {
                "title": str(meta.get("title", "")).strip() or extract_paper_name(filename),
                "author": str(meta.get("author", "Unknown")).strip() or "Unknown",
                "subject": str(meta.get("subject", "")).strip() or "",
                "keywords": str(meta.get("keywords", "")).strip() or "",
                "creator": str(meta.get("creator", "")).strip() or "",
                "creation_date": str(meta.get("creation_date", "")).strip() or "",
            }
            
            pdf_doc.close()
            return metadata
            
        except Exception as e:
            logger.warning(f"Could not extract metadata from {filename}: {e}")
            return {
                "title": extract_paper_name(filename),
                "author": "Unknown"
            }
