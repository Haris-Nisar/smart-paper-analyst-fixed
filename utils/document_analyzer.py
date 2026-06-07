"""
document_analyzer.py - Detect document type and recommend relevant questions
"""

import re
from typing import Literal
from collections import Counter

DocumentType = Literal["research_paper", "resume", "report", "notes", "other"]


class DocumentTypeDetector:
    """Detects document type from text content."""

    # Research paper indicators
    RESEARCH_PATTERNS = {
        "abstract": r"\babstract\b",
        "introduction": r"\bintroduction\b",
        "methodology": r"\bmethodology|methods|approach\b",
        "results": r"\bresults|findings\b",
        "conclusion": r"\bconclusion|conclusion\b",
        "references": r"\breferences|bibliography|citations\b",
        "literature": r"\bliterature review\b",
        "hypothesis": r"\bhypothesis\b",
        "experiment": r"\bexperiment|experimental\b",
        "dataset": r"\bdataset|data collection\b",
        "publication": r"\bpublish|conference|journal\b",
    }

    # Resume indicators
    RESUME_PATTERNS = {
        "education": r"\beducation\b",
        "experience": r"\bexperience|employment\b",
        "skills": r"\bskills|technical skills|competencies\b",
        "objective": r"\bobjectiv|career summary|professional summary\b",
        "certifications": r"\bcertifications?|licenses?\b",
        "projects": r"\bproject[s]?\b",
        "languages": r"\blanguages?\b",
    }

    # Report indicators
    REPORT_PATTERNS = {
        "executive_summary": r"\bexecutive summary\b",
        "overview": r"\boverview\b",
        "recommendations": r"\brecommendations?\b",
        "analysis": r"\banalysis|findings\b",
        "stakeholders": r"\bstakeholder|client|customer\b",
        "fiscal": r"\bbudget|financial|cost|revenue\b",
        "metrics": r"\bmetrics?|kpi|performance\b",
        "risk": r"\brisk|challenge|issue\b",
    }

    # Notes indicators
    NOTES_PATTERNS = {
        "date": r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",
        "todo": r"\btodo\b|^[-*]\s+\[[\s×]\]",
        "heading_marks": r"^#+\s|^=+$|^-+$",
        "bullet_dense": r"^[-*•]\s+\S",
    }

    @classmethod
    def detect(cls, text: str) -> tuple[DocumentType, float]:
        """
        Detect document type from text.
        Returns (type, confidence) where confidence is 0.0-1.0
        """
        if not text or len(text.strip()) < 100:
            return "other", 0.0

        text_lower = text.lower()
        lines = text.split("\n")

        scores = {
            "research_paper": cls._score_patterns(text_lower, cls.RESEARCH_PATTERNS),
            "resume": cls._score_patterns(text_lower, cls.RESUME_PATTERNS),
            "report": cls._score_patterns(text_lower, cls.REPORT_PATTERNS),
            "notes": cls._score_patterns(text_lower, cls.NOTES_PATTERNS),
        }

        # Boost research papers if they have strong academic indicators
        research_indicators = sum(
            1 for pattern in ["abstract", "methodology", "results"]
            if re.search(cls.RESEARCH_PATTERNS[pattern], text_lower)
        )
        if research_indicators >= 2:
            scores["research_paper"] += 0.3

        # Boost resume if multiple education/experience sections exist
        exp_matches = len(re.findall(r"\bexperience\b", text_lower))
        if exp_matches >= 2:
            scores["resume"] += 0.2

        max_type = max(scores, key=scores.get)
        max_score = scores[max_type]
        confidence = min(1.0, max_score)

        # If all scores are very low, it's "other"
        if confidence < 0.15:
            return "other", 0.0

        return max_type, confidence

    @classmethod
    def _score_patterns(cls, text: str, patterns: dict) -> float:
        """Score text against a set of patterns."""
        matches = 0
        for pattern in patterns.values():
            if re.search(pattern, text):
                matches += 1
        return matches / len(patterns) if patterns else 0.0


def get_recommended_questions(doc_type: DocumentType) -> list[str]:
    """Get question suggestions based on document type."""
    suggestions = {
        "research_paper": [
            "What is the main objective of this research?",
            "What methodology was used in this study?",
            "What are the key findings and conclusions?",
            "What datasets were used in this research?",
            "What are the limitations of this work?",
            "What future research directions are suggested?",
            "How does this compare to related work?",
            "What are the technical contributions?",
        ],
        "resume": [
            "What are the main skills mentioned?",
            "Summarize this candidate's professional experience",
            "What technologies and tools are listed?",
            "What education and certifications does this person have?",
            "What are the key achievements and accomplishments?",
            "What is the career progression shown?",
            "What industries has this person worked in?",
            "What languages does this person speak?",
        ],
        "report": [
            "What is the executive summary?",
            "What are the main findings or conclusions?",
            "What recommendations are provided?",
            "What metrics or KPIs are discussed?",
            "What are the identified risks or challenges?",
            "What stakeholders are involved?",
            "What is the budget or financial impact?",
            "What is the timeline for implementation?",
        ],
        "notes": [
            "What are the main topics covered?",
            "What action items or TODOs are listed?",
            "What key points are highlighted?",
            "What dates or deadlines are mentioned?",
            "What are the summaries or conclusions?",
            "What questions or uncertainties are noted?",
            "What follow-up items are required?",
            "What references or related items are mentioned?",
        ],
        "other": [
            "What is the main topic of this document?",
            "What are the key points discussed?",
            "What conclusions or summary is provided?",
            "What information is most relevant?",
            "What actions or next steps are suggested?",
            "What entities or topics are mentioned?",
            "What data or evidence is presented?",
            "What is the purpose of this document?",
        ],
    }
    return suggestions.get(doc_type, suggestions["other"])


def analyze_document(text: str) -> dict:
    """
    Full document analysis.
    Returns: {
        "type": DocumentType,
        "confidence": float,
        "suggested_questions": list[str]
    }
    """
    doc_type, confidence = DocumentTypeDetector.detect(text)
    questions = get_recommended_questions(doc_type)

    return {
        "type": doc_type,
        "confidence": confidence,
        "suggested_questions": questions,
    }
