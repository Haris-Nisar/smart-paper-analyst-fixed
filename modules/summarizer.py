"""
summarizer.py - Generate structured academic summaries for research papers.
"""

import logging
from typing import Optional

from modules.pdf_processor import ProcessedPaper
from modules.rag_pipeline import RAGPipeline
from utils.prompts import SUMMARIZATION_PROMPT
from utils.helpers import truncate_text

logger = logging.getLogger("SmartPaperAnalyst.Summarizer")


class PaperSummarizer:
    """Generates structured academic summaries using the LLM."""

    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag = rag_pipeline

    def summarize(self, paper: ProcessedPaper) -> str:
        """
        Generate a full structured summary for a paper.
        The paper text is truncated to fit the LLM context window.
        """
        if not paper or not paper.full_text:
            raise ValueError("Paper has no content to summarize")
        
        logger.info(f"Summarizing: '{paper.display_name}'")

        # Use first ~8000 chars of the paper (intro, methods, results, conclusion)
        # This gives the LLM the most important parts without overloading context
        paper_content = truncate_text(paper.full_text, max_chars=8000)

        if not paper_content or not paper_content.strip():
            raise ValueError(f"Paper '{paper.display_name}' has no extractable content")

        prompt = SUMMARIZATION_PROMPT.format(paper_content=paper_content)

        try:
            summary = self.rag.generate_with_prompt(prompt, max_tokens=1500)
            
            if not summary or not summary.strip():
                raise ValueError("LLM returned empty summary")
            
            logger.info(f"Summary generated for '{paper.display_name}'")
            return summary
            
        except TimeoutError as e:
            logger.error(f"Summarization timeout for '{paper.display_name}': {e}")
            raise RuntimeError(f"Summarization timed out: {str(e)}")
        except Exception as e:
            logger.error(f"Summarization failed for '{paper.display_name}': {e}")
            raise RuntimeError(f"Failed to generate summary: {str(e)}")

    def summarize_multiple(self, papers: list) -> dict:
        """
        Summarize multiple papers and return a dict: {paper_name: summary}.
        """
        summaries = {}
        for paper in papers:
            try:
                summaries[paper.display_name] = self.summarize(paper)
            except Exception as e:
                summaries[paper.display_name] = f"❌ Summary failed: {str(e)}"
        return summaries
