"""
Intelligent Answer Formatter and Context Analyzer

Provides:
- Context-aware answer formatting
- Graceful partial matches
- Uncertainty explanations
- Related information suggestions
- Multi-query result synthesis

Ensures answers are always helpful, never failing with "no information."
"""

from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class FormattedAnswer:
    """Formatted answer with metadata"""
    content: str
    confidence: float
    is_exact_match: bool
    is_partial_match: bool
    related_topics: List[str]
    source_chunks: int
    has_fallback_context: bool
    clarification: Optional[str] = None


class AnswerFormatter:
    """
    Intelligently formats answers from retrieval results.
    
    Handles:
    - Exact matches (direct answers)
    - Partial matches (related information)
    - No matches (context from similar chunks)
    - Graceful uncertainty explanations
    """
    
    def __init__(self, debug: bool = False):
        """Initialize answer formatter."""
        self.debug = debug
        self.formatted_answers = []
    
    def format_answer(
        self,
        llm_response: str,
        retrieval_result,
        original_query: str,
        query_analysis=None,
        confidence_threshold: float = 0.3
    ) -> FormattedAnswer:
        """
        Format answer from LLM response and retrieval context.
        
        Args:
            llm_response: Raw response from LLM
            retrieval_result: RetrievalResult from semantic retriever
            original_query: User's original query
            query_analysis: Optional QueryAnalysis for context
            confidence_threshold: Minimum confidence for exact match
            
        Returns:
            FormattedAnswer with proper context and explanations
        """
        if not retrieval_result:
            return self._create_no_context_answer(original_query)
        
        # Determine match quality
        is_exact = self._is_exact_match(llm_response, retrieval_result)
        is_partial = self._is_partial_match(llm_response, retrieval_result)
        
        # Classify confidence
        confidence = retrieval_result.confidence
        
        # Extract related topics from chunks
        related_topics = self._extract_related_topics(
            retrieval_result.chunks,
            query_analysis.main_topics if query_analysis else []
        )
        
        # Format the response appropriately
        if is_exact:
            formatted = self._format_exact_answer(
                llm_response, retrieval_result, original_query
            )
        elif is_partial or confidence > confidence_threshold:
            formatted = self._format_partial_answer(
                llm_response, retrieval_result, original_query, related_topics
            )
        else:
            formatted = self._format_fallback_answer(
                llm_response, retrieval_result, original_query, related_topics
            )
        
        # Add source attribution
        formatted = self._add_source_attribution(formatted, retrieval_result)
        
        result = FormattedAnswer(
            content=formatted,
            confidence=confidence,
            is_exact_match=is_exact,
            is_partial_match=is_partial,
            related_topics=related_topics,
            source_chunks=len(retrieval_result.chunks),
            has_fallback_context=not is_exact and not is_partial
        )
        
        self.formatted_answers.append(result)
        return result
    
    def _is_exact_match(self, response: str, retrieval_result) -> bool:
        """
        Detect if answer is an exact match to query.
        
        Signs of exact match:
        - Direct statements
        - Named entities match
        - Specific numbers/dates
        """
        if not response or not retrieval_result.chunks:
            return False
        
        # Check for negation phrases that indicate hard failure
        failure_phrases = [
            "does not contain",
            "is not mentioned",
            "does not discuss",
            "document does not",
            "no information",
        ]
        
        response_lower = response.lower()
        
        # If contains failure phrase, it's NOT exact
        if any(phrase in response_lower for phrase in failure_phrases):
            return False
        
        # If confident retrieval and good response, probably exact
        if retrieval_result.confidence > 0.7 and len(response) > 100:
            return True
        
        return False
    
    def _is_partial_match(self, response: str, retrieval_result) -> bool:
        """
        Detect if answer is a partial/related match.
        
        Signs of partial match:
        - Discusses related concepts
        - Provides context around query
        - Medium confidence
        """
        if not response or not retrieval_result.chunks:
            return False
        
        response_lower = response.lower()
        
        # Partial match indicators
        partial_indicators = [
            "related to",
            "similar to",
            "concept of",
            "approach to",
            "methodology",
            "technique",
            "while the document",
            "the document discusses",
        ]
        
        has_indicator = any(ind in response_lower for ind in partial_indicators)
        
        # Check confidence level
        is_medium_confidence = 0.3 < retrieval_result.confidence <= 0.7
        
        return has_indicator or (is_medium_confidence and len(response) > 50)
    
    def _format_exact_answer(
        self,
        response: str,
        retrieval_result,
        original_query: str
    ) -> str:
        """Format answer for exact match."""
        preamble = "Based on the document, "
        
        if not response.startswith(preamble):
            return f"{preamble}{response}"
        
        return response
    
    def _format_partial_answer(
        self,
        response: str,
        retrieval_result,
        original_query: str,
        related_topics: List[str]
    ) -> str:
        """Format answer for partial/related match."""
        # Check if response already has context
        has_explicit_context = any(phrase in response.lower() for phrase in [
            "while", "however", "related", "similar", "although"
        ])
        
        if has_explicit_context:
            return response
        
        # Add contextual preface
        preface = "I couldn't find an exact match, but the document discusses related concepts: "
        
        if len(related_topics) > 0:
            topics_str = ", ".join(related_topics[:3])
            preface += f"{topics_str}. "
        
        preface += "Based on this related information: "
        
        return preface + response
    
    def _format_fallback_answer(
        self,
        response: str,
        retrieval_result,
        original_query: str,
        related_topics: List[str]
    ) -> str:
        """Format answer when limited context is available."""
        # Don't say "no information" - say what WAS found
        preface_options = [
            f"While I couldn't find a direct answer about '{original_query.strip()}', ",
            "The document appears to discuss related topics: ",
            "I found related information that may be helpful: ",
            "Based on available context in the document: ",
        ]
        
        # Choose based on related topics
        if related_topics:
            preface = preface_options[0] + f"the document does mention {related_topics[0]}. "
        else:
            preface = preface_options[1]
        
        # Clean up bad responses
        response_clean = response.strip()
        
        # Remove failure phrases
        failure_phrases = [
            "The document does not contain information",
            "This is not mentioned",
            "I cannot find",
            "There is no",
        ]
        
        for phrase in failure_phrases:
            response_clean = response_clean.replace(phrase, "").strip()
        
        # If still empty or too short, provide generic context
        if not response_clean or len(response_clean) < 20:
            response_clean = self._generate_fallback_context(related_topics)
        
        return preface + response_clean
    
    def _generate_fallback_context(self, related_topics: List[str]) -> str:
        """Generate helpful fallback context."""
        if not related_topics:
            return "The document contains various topics that may be related to your query. Please try rephrasing your question or asking about specific topics mentioned in the document."
        
        topics_str = ", ".join(related_topics[:5])
        return f"The document discusses the following related areas: {topics_str}. You may want to ask about these specific topics."
    
    def _add_source_attribution(self, formatted_answer: str, retrieval_result) -> str:
        """Add source attribution to answer using paper names."""
        if not retrieval_result.chunks:
            return formatted_answer

        # Prefer paper names from chunk.source; filter out generic chunk_N IDs
        sources = []
        seen = set()
        for c in retrieval_result.chunks[:5]:
            src = getattr(c, 'source', '')
            # Skip generic chunk_N labels
            if src and not src.startswith('chunk_') and src not in seen:
                sources.append(src)
                seen.add(src)

        if not sources:
            return formatted_answer

        source_str = " | ".join(sources)
        attribution = f"\n\n📚 *Sources: {source_str}*"
        return formatted_answer + attribution
    
    def _extract_related_topics(
        self,
        chunks,
        query_topics: List[str]
    ) -> List[str]:
        """Extract related topics from chunks."""
        topics = set()
        
        # Keywords to look for
        topic_indicators = [
            "introduces", "discusses", "covers", "explains",
            "presents", "analyzes", "examines"
        ]
        
        for chunk in chunks[:5]:  # Examine top 5 chunks
            content_lower = chunk.content.lower()
            
            # Simple topic extraction from chunk text
            words = content_lower.split()
            
            # Look for significant terms (capitalized or repeated)
            for i, word in enumerate(words):
                if len(word) > 4 and word.strip('.,;:!?').isalpha():
                    # If word appears multiple times, it's likely a topic
                    if content_lower.count(word) > 2 and word not in query_topics:
                        topics.add(word.strip('.,;:!?'))
        
        return sorted(list(topics))[:5]  # Return top 5
    
    def _create_no_context_answer(self, original_query: str) -> FormattedAnswer:
        """Create answer when no retrieval context available."""
        content = f"I couldn't retrieve specific information about '{original_query}' from the document. This could mean the document doesn't contain information about this topic, or it may be phrased differently than expected. You might try rephrasing your question or asking about related concepts."
        
        return FormattedAnswer(
            content=content,
            confidence=0.1,
            is_exact_match=False,
            is_partial_match=False,
            related_topics=[],
            source_chunks=0,
            has_fallback_context=True,
            clarification="Retrieval failed - try rephrasing"
        )
    
    def enhance_conversational(self, answer: str, query: str) -> str:
        """
        Make answer more conversational and helpful.
        
        Adjusts tone based on query style.
        """
        # If query is casual, make answer conversational
        casual_markers = ["what's", "what is", "i'm", "can you", "could you"]
        is_casual = any(marker in query.lower() for marker in casual_markers)
        
        if is_casual and not any(word in answer.lower() for word in ["you know", "essentially", "basically"]):
            # Add conversational flair
            if answer.startswith("Based"):
                answer = answer.replace("Based on", "So based on", 1)
        
        # Add clarifying questions at end
        if len(answer) > 200 and "?" not in answer[-50:]:
            clarifications = [
                "\n\nDoes this answer your question, or would you like me to explain any of these concepts further?",
                "\n\nWould you like more details about any part of this?",
                "\n\nIs there a specific aspect you'd like me to focus on?",
            ]
            
            import random
            answer += random.choice(clarifications)
        
        return answer
    
    def get_formatting_stats(self) -> Dict:
        """Get answer formatting statistics."""
        if not self.formatted_answers:
            return {"total_answers": 0}
        
        total = len(self.formatted_answers)
        exact = sum(1 for a in self.formatted_answers if a.is_exact_match)
        partial = sum(1 for a in self.formatted_answers if a.is_partial_match)
        fallback = sum(1 for a in self.formatted_answers if a.has_fallback_context)
        
        avg_confidence = sum(a.confidence for a in self.formatted_answers) / total
        
        return {
            "total_answers": total,
            "exact_matches": exact,
            "partial_matches": partial,
            "fallback_answers": fallback,
            "avg_confidence": avg_confidence,
            "exact_rate": exact / total if total > 0 else 0,
            "fallback_rate": fallback / total if total > 0 else 0,
        }


def create_answer_formatter(debug: bool = False) -> AnswerFormatter:
    """Factory function to create answer formatter."""
    return AnswerFormatter(debug=debug)
