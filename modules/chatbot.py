"""
chatbot.py - Chat session management with history and context memory.
"""

import logging
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime

from modules.rag_pipeline import RAGPipeline

logger = logging.getLogger("SmartPaperAnalyst.Chatbot")


@dataclass
class ChatMessage:
    """Single chat message with metadata."""
    role: str          # "user" or "assistant"
    content: str
    timestamp: str = field(default_factory=lambda: datetime.now().strftime("%H:%M"))
    sources: List[str] = field(default_factory=list)   # Source paper names


class ChatSession:
    """
    Manages a multi-turn chat session with context memory.
    Stores full history and interfaces with the RAG pipeline.
    """

    def __init__(self, rag_pipeline: RAGPipeline, max_history: int = 50):
        self.rag = rag_pipeline
        self.max_history = max_history
        self.messages: List[ChatMessage] = []
        logger.info("ChatSession initialized")

    def add_message(self, role: str, content: str, sources: List[str] = None):
        """Add a message to chat history."""
        msg = ChatMessage(role=role, content=content, sources=sources or [])
        self.messages.append(msg)

        # Trim history if too long
        if len(self.messages) > self.max_history:
            # Keep system messages and trim oldest
            self.messages = self.messages[-self.max_history:]

    def ask(self, question: str) -> tuple[str, List[str]]:
        """
        Ask a question through the RAG pipeline.
        Returns (answer, source_paper_names).
        """
        # Input validation
        if not question or not question.strip():
            raise ValueError("Question cannot be empty")
        
        question = question.strip()
        
        if len(question) > 1000:
            logger.warning(f"Question truncated from {len(question)} to 1000 chars")
            question = question[:1000]
        
        # Add user message to history
        self.add_message("user", question)

        # Build chat history for context (last 4 pairs)
        history_dicts = [
            {"role": m.role, "content": m.content}
            for m in self.messages[-8:]
        ]

        # Query RAG pipeline (use semantic query for intelligent retrieval)
        try:
            answer, chunks = self.rag.query_semantic(
                question=question,
                chat_history=history_dicts,
            )
        except Exception as e:
            logger.error(f"RAG query failed: {e}")
            answer = f"❌ Error querying papers: {str(e)}"
            chunks = []

        # Extract unique source paper names
        sources = list({chunk.paper_display_name for chunk in chunks}) if chunks else []

        # Add assistant response to history
        self.add_message("assistant", answer, sources=sources)

        return answer, sources

    def clear(self):
        """Clear chat history."""
        self.messages = []
        logger.info("Chat history cleared")

    @property
    def history(self) -> List[ChatMessage]:
        return self.messages

    @property
    def is_empty(self) -> bool:
        return len(self.messages) == 0
