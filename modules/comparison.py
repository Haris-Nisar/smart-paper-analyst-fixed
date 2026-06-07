"""
comparison.py - Multi-paper comparison and analysis module.
Compares objectives, methods, datasets, results, strengths, weaknesses.
"""

import logging
from typing import List

from modules.pdf_processor import ProcessedPaper
from modules.rag_pipeline import RAGPipeline
from utils.prompts import COMPARISON_PROMPT
from utils.helpers import truncate_text

logger = logging.getLogger("SmartPaperAnalyst.Comparison")


class PaperComparator:
    """Compares multiple research papers across key academic dimensions."""

    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag = rag_pipeline

    def compare(self, papers: List[ProcessedPaper]) -> str:
        """
        Generate a comprehensive comparison of multiple papers.
        """
        if not papers:
            return "⚠️ No papers provided for comparison."
        
        if len(papers) < 2:
            return "⚠️ Please upload at least 2 papers to enable comparison."

        logger.info(f"Comparing {len(papers)} papers")

        # Build combined content string (truncated per paper)
        papers_content = ""
        chars_per_paper = 5000 // len(papers)  # Distribute context budget

        for i, paper in enumerate(papers, 1):
            truncated = truncate_text(paper.full_text, max_chars=chars_per_paper)
            papers_content += f"\n\n{'='*60}\nPAPER {i}: {paper.display_name}\n{'='*60}\n{truncated}"

        if not papers_content or not papers_content.strip():
            return "❌ Papers have no extractable content for comparison."

        prompt = COMPARISON_PROMPT.format(papers_content=papers_content)

        try:
            comparison = self.rag.generate_with_prompt(prompt, max_tokens=2000)
            
            if not comparison or not comparison.strip():
                raise ValueError("LLM returned empty comparison")
            
            logger.info("Comparison generated successfully")
            return comparison
        except TimeoutError as e:
            logger.error(f"Comparison timeout: {e}")
            raise RuntimeError(f"Comparison timed out: {str(e)}")
        except Exception as e:
            logger.error(f"Comparison failed: {e}")
            raise RuntimeError(f"Failed to generate comparison: {str(e)}")
