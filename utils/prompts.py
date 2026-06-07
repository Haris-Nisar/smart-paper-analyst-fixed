"""
prompts.py - Centralized prompt templates for all LLM tasks.
Using structured, academic-grade prompts for high-quality outputs.
"""

# ─── RAG / Chat Prompt ────────────────────────────────────────────────────────
RAG_PROMPT = """You are an expert academic research assistant with deep knowledge of research papers.
Your task is to answer the user's question using ONLY the context provided from research papers.

INSTRUCTIONS:
1. Use ONLY information from the provided Context sections below
2. Be precise, factual, and use academic language
3. Cite which paper/source the information comes from (e.g., "According to Paper 1...")
4. If information is incomplete, say so clearly (e.g., "The paper mentions X but does not specify Y")
5. If the context does NOT contain the answer, respond with: "The provided papers do not contain information about this topic."
6. Format your answer clearly with bullet points or paragraphs as appropriate
7. Do NOT use external knowledge or hallucinate information
8. Do NOT make assumptions beyond what is stated in the context

Context from papers:
{context}

Conversation History:
{chat_history}

User Question: {question}

Answer:"""


# ─── Summarization Prompt ─────────────────────────────────────────────────────
SUMMARIZATION_PROMPT = """You are an expert academic summarizer. Generate a comprehensive,
structured summary of the following research paper content.

Paper content:
{paper_content}

Generate a detailed academic summary with EXACTLY these sections. Use bullet points within each section:

## 📌 Objective
[What is the main goal/purpose of this research?]

## ❓ Problem Statement
[What problem does the paper address?]

## 🔬 Methodology
[What methods, techniques, or approaches were used?]

## 📊 Dataset
[What datasets were used? Include size, type, source if mentioned.]

## 🏆 Key Findings
[What are the main results and discoveries?]

## ⚠️ Limitations
[What are the stated limitations of the work?]

## 🔭 Future Work
[What future directions are suggested?]

## ✅ Final Conclusion
[Summarize the overall contribution and impact of this paper.]

Keep each section concise (3-6 bullet points) but informative. Use academic writing style."""


# ─── Comparison Prompt ────────────────────────────────────────────────────────
COMPARISON_PROMPT = """You are an expert academic analyst. Compare the following research papers
based on their content extracted below.

Papers Content:
{papers_content}

Generate a thorough academic comparison covering these dimensions:

## 🎯 Objectives Comparison
[Compare the goals of each paper]

## 🔬 Methodology Comparison
[Compare their methods and approaches]

## 🤖 Models/Algorithms Used
[Compare models, algorithms, or techniques]

## 📊 Datasets Compared
[Compare datasets: type, size, domain]

## 📈 Results & Performance
[Compare results, accuracy, benchmarks]

## 💪 Strengths Analysis
[Key strengths of each paper]

## ⚠️ Weaknesses Analysis
[Limitations and weaknesses of each paper]

## 🏁 Conclusions
[Overall comparative conclusion — which approach is more effective and why?]

Format each section with clear sub-headings per paper. Be analytical and objective."""


# ─── Research Gap Prompt ──────────────────────────────────────────────────────
RESEARCH_GAP_PROMPT = """You are an expert academic researcher and research strategist.
Analyze the following research paper(s) and identify significant research gaps,
unexplored areas, and future research opportunities.

Paper content:
{paper_content}

Generate a comprehensive Research Gap Analysis:

## 🔍 Identified Research Gaps
[List specific gaps and unexplored areas found in the research]

## 🚀 Suggested Future Research Directions
[Concrete, actionable research ideas to address these gaps]

## 🧪 Potential Methodological Improvements
[Ways to improve or extend the current methodology]

## 📊 Dataset & Evaluation Gaps
[Missing datasets, evaluation metrics, or experimental setups]

## 🌐 Broader Impact & Applications
[Unexplored applications or societal implications]

## 💡 Novel Research Ideas
[Specific new research questions that arise from this work]

Use academic writing style. Be specific and constructive. Each point should be
a clear, actionable research opportunity."""


# ─── Semantic Search Context Prompt ──────────────────────────────────────────
SEMANTIC_SEARCH_PROMPT = """Based on the following retrieved text chunks from research papers,
provide a concise, relevant answer or summary related to the search query.

Query: {query}

Retrieved Chunks:
{chunks}

Provide a brief synthesis of the most relevant information found. Be factual and cite
which paper/section the information comes from if identifiable."""


# ─── Citation Extraction Prompt ───────────────────────────────────────────────
CITATION_EXTRACTION_PROMPT = """Extract all academic references and citations from the
following text. Format each as a proper academic citation.

Text:
{text}

List all citations found in IEEE or APA format. If no citations are found, say "No citations detected."
"""
