"""
Advanced Query Understanding and Rewriting System

Analyzes user queries to:
- Detect intent and semantic meaning
- Identify synonyms and related concepts
- Rewrite queries for better retrieval
- Generate multiple semantic variations
- Support academic and casual phrasing
"""

import re
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json


@dataclass
class QueryAnalysis:
    """Analysis result for a user query"""
    original_query: str
    intent: str
    main_topics: List[str]
    synonyms: List[str]
    related_concepts: List[str]
    query_variations: List[str]
    is_academic: bool
    is_indirect: bool
    confidence: float

    def get_analysis_summary(self) -> str:
        """Return a human-readable summary of this analysis."""
        lines = [
            f"Query Analysis:",
            f'- Original: "{self.original_query}"',
            f"- Intent: {self.intent}",
            f"- Topics: {', '.join(self.main_topics)}",
            f"- Academic Style: {self.is_academic}",
            f"- Indirect: {self.is_indirect}",
            f"- Clarity Confidence: {self.confidence:.1%}",
            f"- Variations to Retrieve ({len(self.query_variations)}):",
        ]
        for v in self.query_variations[:5]:
            lines.append(f"  • {v}")
        return "\n".join(lines)


class QueryAnalyzer:
    """
    Advanced semantic query analyzer.
    
    Understands user intent and generates multiple retrieval variations.
    """
    
    def __init__(self):
        """Initialize the query analyzer with domain knowledge."""
        self.synonym_map = self._build_synonym_map()
        self.concept_relations = self._build_concept_relations()
        self.intent_patterns = self._build_intent_patterns()
        
    def _build_synonym_map(self) -> Dict[str, List[str]]:
        """Build comprehensive synonym dictionary."""
        return {
            # General synonyms
            "advantages": ["benefits", "strengths", "pros", "positive aspects", "improvements"],
            "disadvantages": ["limitations", "drawbacks", "weaknesses", "cons", "challenges", "issues"],
            "method": ["approach", "technique", "strategy", "methodology", "process"],
            "results": ["findings", "outcomes", "conclusions", "results"],
            "purpose": ["goal", "objective", "aim", "target", "intent"],
            "explain": ["describe", "clarify", "elaborate", "discuss", "outline"],
            "show": ["demonstrate", "illustrate", "exhibit", "display", "present"],
            "compare": ["contrast", "differentiate", "distinguish", "compare"],
            "help": ["assist", "support", "aid", "facilitate"],
            "problem": ["issue", "challenge", "difficulty", "obstacle", "problem"],
            "solution": ["answer", "fix", "remedy", "resolution", "approach"],
            "create": ["develop", "build", "design", "construct", "generate"],
            "use": ["apply", "utilize", "employ", "leverage", "implement"],
            "important": ["significant", "critical", "crucial", "essential", "vital"],
            "work": ["function", "operate", "perform", "execute", "work"],
            "structure": ["organization", "framework", "architecture", "design", "layout"],
            "performance": ["efficiency", "effectiveness", "speed", "quality", "accuracy"],
            "system": ["framework", "platform", "architecture", "model", "tool"],
            "data": ["information", "dataset", "evidence", "input", "content"],
            "training": ["learning", "preparation", "teaching", "education", "instruction"],
            "model": ["network", "algorithm", "architecture", "system", "framework"],
            "neural": ["deep", "neural network", "machine learning", "AI", "artificial intelligence"],
            "weak": ["poor", "limited", "insufficient", "weak point", "weakness"],
            "strong": ["robust", "effective", "powerful", "strong point", "strength"],
            
            # Academic-specific
            "abstract": ["summary", "overview", "introduction", "synopsis"],
            "methodology": ["methods", "approach", "technique", "procedure"],
            "conclusion": ["findings", "summary", "outcome", "result"],
            "hypothesis": ["assumption", "theory", "proposal", "conjecture"],
            "experiment": ["study", "test", "evaluation", "analysis"],
            "validate": ["verify", "confirm", "test", "prove"],
            "quantitative": ["numerical", "numerical analysis", "metric", "measurement"],
            "qualitative": ["descriptive", "non-numerical", "subjective", "contextual"],
            
            # Document-specific
            "experience": ["skills", "background", "expertise", "proficiency", "experience"],
            "education": ["qualification", "degree", "training", "learning", "certification"],
            "skill": ["ability", "competency", "expertise", "proficiency", "talent"],
            "achievement": ["accomplishment", "success", "milestone", "award", "recognition"],
            "responsibility": ["duty", "role", "task", "obligation", "accountability"],
        }
    
    def _build_concept_relations(self) -> Dict[str, List[str]]:
        """Build knowledge about related concepts."""
        return {
            "accuracy": ["precision", "recall", "f1-score", "error rate", "performance"],
            "efficiency": ["speed", "latency", "throughput", "scalability", "optimization"],
            "robustness": ["stability", "reliability", "fault tolerance", "resilience", "consistency"],
            "scalability": ["large-scale", "distributed", "parallel", "performance", "capacity"],
            "optimization": ["improvement", "tuning", "enhancement", "refinement", "efficiency"],
            "complexity": ["time complexity", "space complexity", "computational cost", "algorithm"],
            "generalization": ["generalizability", "transfer learning", "domain adaptation", "flexibility"],
            "overfitting": ["underfitting", "regularization", "generalization", "validation"],
            "loss function": ["objective", "cost function", "metric", "error"],
            "gradient descent": ["optimization", "learning rate", "convergence", "training"],
            "attention": ["transformer", "mechanism", "neural network", "architecture"],
            "embedding": ["representation", "vector", "encoding", "feature"],
            "benchmark": ["evaluation", "dataset", "metric", "baseline", "performance"],
            "dataset": ["corpus", "data", "collection", "sample", "training data"],
        }
    
    def _build_intent_patterns(self) -> Dict[str, List[str]]:
        """Build patterns for detecting query intent."""
        return {
            "explanation": [
                r"what (is|are|do)",
                r"explain",
                r"describe",
                r"how does",
                r"what (does|do)",
                r"what's",
                r"tell me about",
                r"define",
                r"clarify",
            ],
            "comparison": [
                r"compare",
                r"difference between",
                r"versus",
                r"vs\.",
                r"similar to",
                r"like",
                r"contrasts",
            ],
            "evaluation": [
                r"pros and cons",
                r"advantages",
                r"disadvantages",
                r"benefits",
                r"drawbacks",
                r"limitations",
                r"strengths",
                r"weaknesses",
                r"better than",
                r"best way",
            ],
            "procedure": [
                r"how (to|do|does)",
                r"steps to",
                r"process of",
                r"implement",
                r"create",
                r"build",
                r"construct",
            ],
            "causality": [
                r"why",
                r"causes?",
                r"because",
                r"effect of",
                r"impact of",
                r"results in",
            ],
            "identification": [
                r"what (is|are) the",
                r"find",
                r"identify",
                r"locate",
                r"which",
            ],
        }
    
    def analyze(self, query: str) -> QueryAnalysis:
        """
        Analyze a user query comprehensively.
        
        Args:
            query: User's input query
            
        Returns:
            QueryAnalysis with intent, topics, synonyms, and variations
        """
        query_lower = query.lower()
        
        # Detect query properties
        is_academic = self._detect_academic_phrasing(query_lower)
        is_indirect = self._detect_indirect_question(query_lower)
        intent = self._detect_intent(query_lower)
        
        # Extract main topics
        main_topics = self._extract_topics(query_lower)
        
        # Find synonyms
        synonyms = self._find_synonyms(main_topics)
        
        # Find related concepts
        related_concepts = self._find_related_concepts(main_topics)
        
        # Generate variations
        variations = self._generate_variations(
            query, main_topics, synonyms, related_concepts, is_academic
        )
        
        # Calculate confidence
        confidence = self._calculate_confidence(query_lower, main_topics)
        
        return QueryAnalysis(
            original_query=query,
            intent=intent,
            main_topics=main_topics,
            synonyms=synonyms,
            related_concepts=related_concepts,
            query_variations=variations,
            is_academic=is_academic,
            is_indirect=is_indirect,
            confidence=confidence
        )
    
    def _detect_academic_phrasing(self, query: str) -> bool:
        """Detect if query uses academic language."""
        academic_markers = [
            "methodology", "hypothesis", "empirical", "theoretical",
            "quantitative", "qualitative", "validation", "benchmark",
            "performance metric", "algorithm", "architecture",
            "literature", "research", "study", "experiment",
            "framework", "model", "propose", "establish",
        ]
        return any(marker in query for marker in academic_markers)
    
    def _detect_indirect_question(self, query: str) -> bool:
        """Detect if question is indirectly phrased."""
        indirect_patterns = [
            r"i'm wondering",
            r"i'm curious",
            r"i'd like to know",
            r"can you help",
            r"could you explain",
            r"would you mind",
            r"is there any",
        ]
        return any(re.search(pattern, query) for pattern in indirect_patterns)
    
    def _detect_intent(self, query: str) -> str:
        """Detect the primary intent of the query."""
        for intent, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        return "general"
    
    def _extract_topics(self, query: str) -> List[str]:
        """Extract main topics/keywords from query."""
        # Remove common stop words
        stop_words = {
            "the", "a", "an", "and", "or", "but", "is", "are", "was", "were",
            "be", "been", "being", "have", "has", "had", "do", "does", "did",
            "will", "would", "could", "should", "may", "might", "must", "can",
            "i", "you", "he", "she", "it", "we", "they", "what", "which",
            "who", "when", "where", "why", "how", "this", "that", "these",
            "those", "to", "from", "in", "on", "at", "by", "for", "with",
            "about", "as", "of", "its", "my", "your", "his", "her", "our",
        }
        
        # Extract words
        words = re.findall(r'\b[a-z]+(?:[_-][a-z]+)?\b', query)
        
        # Filter stop words and short words
        topics = [w for w in words if w not in stop_words and len(w) > 2]
        
        return list(dict.fromkeys(topics))  # Remove duplicates, preserve order
    
    def _find_synonyms(self, topics: List[str]) -> List[str]:
        """Find synonyms for identified topics."""
        synonyms = []
        for topic in topics:
            if topic in self.synonym_map:
                synonyms.extend(self.synonym_map[topic])
        return list(dict.fromkeys(synonyms))  # Remove duplicates
    
    def _find_related_concepts(self, topics: List[str]) -> List[str]:
        """Find conceptually related terms."""
        related = []
        for topic in topics:
            if topic in self.concept_relations:
                related.extend(self.concept_relations[topic])
        return list(dict.fromkeys(related))  # Remove duplicates
    
    def _generate_variations(
        self,
        original: str,
        topics: List[str],
        synonyms: List[str],
        related: List[str],
        is_academic: bool
    ) -> List[str]:
        """Generate multiple retrieval variations of the query."""
        variations = set()
        variations.add(original)  # Keep original
        
        if not topics:
            return list(variations)
        
        # Variation 1: Replace with synonyms
        if synonyms:
            for synonym in synonyms[:3]:  # Use top 3
                variation = original.lower()
                # Try to replace topic words with synonyms
                for topic in topics:
                    if topic in variation:
                        variation = variation.replace(topic, synonym)
                        break
                if variation != original.lower():
                    variations.add(variation)
        
        # Variation 2: Add related concepts
        if related:
            for concept in related[:2]:  # Use top 2
                variations.add(f"{original} {concept}")
        
        # Variation 3: Topic-focused query
        topic_query = " ".join(topics[:5])  # Top 5 topics
        if topic_query:
            variations.add(topic_query)
        
        # Variation 4: Academic rephrase if needed
        if not is_academic and len(topics) > 0:
            academic_version = f"methodology approach implementation {' '.join(topics[:3])}"
            variations.add(academic_version)
        
        # Variation 5: Conceptual expansion
        if related:
            concept_version = f"{original} {' '.join(related[:3])}"
            variations.add(concept_version)
        
        # Variation 6: Synonym-enriched
        if synonyms:
            synonym_version = f"{original} {' '.join(synonyms[:3])}"
            variations.add(synonym_version)
        
        # Filter out very short variations
        variations = [v.strip() for v in variations if len(v.strip()) > 3]
        
        return list(dict.fromkeys(variations))  # Remove duplicates, preserve order
    
    def _calculate_confidence(self, query: str, topics: List[str]) -> float:
        """Calculate query clarity confidence (0.0-1.0)."""
        confidence = 0.5
        
        # Add points for clarity
        if len(query) > 10:
            confidence += 0.2
        if len(topics) >= 2:
            confidence += 0.2
        if len(query.split()) >= 4:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def rewrite_query(self, query: str) -> str:
        """
        Intelligently rewrite a query for better retrieval.
        
        Improves:
        - Conversational to formal
        - Vague to specific
        - Indirect to direct
        """
        query_lower = query.lower()
        rewritten = query_lower
        
        # Replace common conversational phrases
        conversational_replacements = {
            r"i'm wondering if": "does",
            r"i'm curious about": "explain",
            r"can you help me": "help me understand",
            r"would you mind": "please explain",
            r"could you tell me": "explain",
            r"what's the": "what is the",
            r"what's your": "what is your",
        }
        
        for pattern, replacement in conversational_replacements.items():
            rewritten = re.sub(pattern, replacement, rewritten)
        
        # Expand vague pronouns with context from topics
        topics = self._extract_topics(rewritten)
        if topics:
            # Replace "it" with first topic for clarity
            if "it" in rewritten and len(topics) > 0:
                rewritten = rewritten.replace("it ", f"{topics[0]} ")
        
        return rewritten.strip()
    
    def get_analysis_summary(self, analysis: QueryAnalysis) -> str:
        """Get a human-readable summary of query analysis."""
        summary = f"""
Query Analysis:
- Original: "{analysis.original_query}"
- Intent: {analysis.intent}
- Topics: {', '.join(analysis.main_topics)}
- Academic Style: {analysis.is_academic}
- Indirect: {analysis.is_indirect}
- Clarity Confidence: {analysis.confidence:.1%}
- Variations to Retrieve ({len(analysis.query_variations)}): 
  {chr(10).join(f'  • {v}' for v in analysis.query_variations[:5])}
"""
        return summary


def create_query_analyzer() -> QueryAnalyzer:
    """Factory function to create query analyzer."""
    return QueryAnalyzer()
