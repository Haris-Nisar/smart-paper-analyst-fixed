"""
research_gap.py - Research gap identification and future direction suggestions.
"""

import logging
from typing import List

from modules.pdf_processor import ProcessedPaper
from modules.rag_pipeline import RAGPipeline
from utils.prompts import RESEARCH_GAP_PROMPT
from utils.helpers import truncate_text

logger = logging.getLogger("SmartPaperAnalyst.ResearchGap")


class ResearchGapAnalyzer:
    """Identifies research gaps and future directions from papers."""

    def __init__(self, rag_pipeline: RAGPipeline):
        self.rag = rag_pipeline

    def analyze(self, papers: List[ProcessedPaper]) -> str:
        """Analyze one or more papers for research gaps."""
        if not papers:
            return "⚠️ No papers available for gap analysis."

        logger.info(f"Analyzing research gaps for {len(papers)} paper(s)")

        # Combine paper content (focus on conclusions/limitations sections)
        paper_content = ""
        chars_per_paper = 6000 // len(papers)

        for paper in papers:
            if not paper or not paper.full_text:
                continue
            truncated = truncate_text(paper.full_text, max_chars=chars_per_paper)
            paper_content += f"\n\n--- PAPER: {paper.display_name} ---\n{truncated}"

        if not paper_content or not paper_content.strip():
            return "❌ Papers have no extractable content for gap analysis."

        prompt = RESEARCH_GAP_PROMPT.format(paper_content=paper_content)

        try:
            gaps = self.rag.generate_with_prompt(prompt, max_tokens=1500)
            
            if not gaps or not gaps.strip():
                raise ValueError("LLM returned empty gap analysis")
            
            logger.info("Research gap analysis complete")
            return gaps
        except TimeoutError as e:
            logger.error(f"Gap analysis timeout: {e}")
            raise RuntimeError(f"Analysis timed out: {str(e)}")
        except Exception as e:
            logger.error(f"Research gap analysis failed: {e}")
            raise RuntimeError(f"Failed to analyze research gaps: {str(e)}")
