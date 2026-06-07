"""
rag_pipeline.py - Core Retrieval-Augmented Generation (RAG) pipeline.
Connects FAISS retrieval with LLM generation for accurate, context-grounded answers.

Advanced semantic retrieval with multi-query, fallback logic, and intelligent answering.
"""

import logging
import requests
from typing import List, Optional, Tuple

from modules.embeddings import EmbeddingEngine
from modules.chunking import TextChunk
from modules.query_analyzer import create_query_analyzer
from modules.semantic_retriever import create_semantic_retriever
from modules.answer_formatter import create_answer_formatter
from utils.config import config
from utils.prompts import RAG_PROMPT
from utils.helpers import truncate_text

logger = logging.getLogger("SmartPaperAnalyst.RAGPipeline")


class LLMClient:
    """
    Unified LLM client supporting OpenRouter, Mistral API, and HuggingFace.
    Abstracts provider differences behind a single generate() method.
    """

    def __init__(self):
        self.provider = config.LLM_PROVIDER
        self.request_timeout = 120  # seconds
        logger.info(f"LLMClient initialized with provider: {self.provider}")

    def generate(self, prompt: str, max_tokens: int = None) -> str:
        """
        Generate text from the configured LLM.
        Returns the generated text string.
        Raises specific exceptions for different error types.
        """
        max_tokens = max_tokens or config.MAX_TOKENS

        # Validate prompt
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty")
        
        if len(prompt) > 32000:
            logger.warning(f"Prompt truncated: {len(prompt)} chars > 32000")
            prompt = prompt[:32000]

        try:
            if self.provider == "openrouter":
                return self._call_openrouter(prompt, max_tokens)
            elif self.provider == "mistral":
                return self._call_mistral(prompt, max_tokens)
            elif self.provider == "huggingface":
                return self._call_huggingface(prompt, max_tokens)
            else:
                raise ValueError(f"Unknown LLM provider: {self.provider}")
        except requests.exceptions.Timeout as e:
            logger.error(f"LLM API timeout after {self.request_timeout}s: {e}")
            raise TimeoutError(
                f"LLM API did not respond within {self.request_timeout} seconds. "
                "Please try again or contact support."
            )
        except requests.exceptions.ConnectionError as e:
            logger.error(f"Cannot connect to LLM API: {e}")
            raise ConnectionError(
                "Cannot connect to LLM API. Please check your internet connection "
                "and API key configuration."
            )
        except ValueError as e:
            logger.error(f"Invalid response from LLM: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected LLM error: {e}", exc_info=True)
            raise RuntimeError(f"LLM generation failed: {str(e)}")

    def _call_openrouter(self, prompt: str, max_tokens: int) -> str:
        """Call OpenRouter API (supports many open-source models)."""
        if not config.OPENROUTER_API_KEY:
            raise ValueError("OPENROUTER_API_KEY not configured")
        
        # Construct headers per official OpenRouter docs
        headers = {
            "Authorization": f"Bearer {config.OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://smart-paper-analyst.app",
            "X-OpenRouter-Title": "Smart Academic Paper Analyst",
        }
        
        # Construct payload per official OpenRouter API format
        payload = {
            "model": config.OPENROUTER_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": config.TEMPERATURE,
        }
        
        url = f"{config.OPENROUTER_BASE_URL}/chat/completions"
        
        # Log request details for debugging
        logger.info(f"🔗 OpenRouter URL: {url}")
        logger.info(f"📋 Model: {config.OPENROUTER_MODEL}")
        logger.info(f"📊 Request size: {len(prompt)} chars, max_tokens={max_tokens}")
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.request_timeout,
            )
            
            # Log response status
            logger.info(f"📬 Response status: {response.status_code}")
            
            # Handle errors BEFORE calling raise_for_status()
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    logger.error(f"❌ OpenRouter API error response: {error_data}")
                except:
                    logger.error(f"❌ OpenRouter API error (no JSON): {response.text[:500]}")
            
            # This will raise HTTPError for bad status codes
            response.raise_for_status()
            
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                logger.error("❌ Invalid OpenRouter API key (401 Unauthorized)")
                raise ValueError(
                    "Invalid OpenRouter API key. Please check your OPENROUTER_API_KEY in .env"
                )
            elif response.status_code == 404:
                try:
                    error_data = response.json()
                    error_msg = error_data.get("error", {}).get("message", "Unknown error")
                except:
                    error_msg = response.text
                logger.error(f"❌ OpenRouter 404 error: {error_msg}")
                raise ValueError(
                    f"OpenRouter API endpoint not found (404). "
                    f"Check that model '{config.OPENROUTER_MODEL}' exists. "
                    f"Error: {error_msg}"
                )
            elif response.status_code == 429:
                logger.error("⏱️ OpenRouter rate limited (429)")
                raise RuntimeError(
                    "OpenRouter rate limit exceeded. Please wait before retrying."
                )
            elif response.status_code >= 500:
                logger.error(f"🔥 OpenRouter server error ({response.status_code})")
                raise RuntimeError(
                    "OpenRouter API server error. Please try again later."
                )
            else:
                logger.error(f"❌ OpenRouter HTTP error: {response.status_code}")
                raise ValueError(f"OpenRouter API error: {str(e)}")
        
        except requests.exceptions.Timeout as e:
            logger.error(f"⏱️ OpenRouter timeout after {self.request_timeout}s")
            raise TimeoutError(
                f"OpenRouter API did not respond within {self.request_timeout} seconds"
            )
        except requests.exceptions.ConnectionError as e:
            logger.error(f"🔌 Cannot connect to OpenRouter: {e}")
            raise ConnectionError(
                "Cannot connect to OpenRouter. Check your internet connection."
            )
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ OpenRouter request failed: {e}")
            raise RuntimeError(f"OpenRouter API request failed: {str(e)}")
        
        # Parse response
        try:
            data = response.json()
        except ValueError as e:
            logger.error(f"❌ Cannot parse OpenRouter response as JSON: {e}")
            logger.error(f"Response text: {response.text[:500]}")
            raise ValueError("OpenRouter returned invalid JSON response")
        
        logger.info(f"📦 Response keys: {list(data.keys())}")
        
        # Validate response structure per OpenRouter docs
        if not isinstance(data, dict):
            logger.error(f"❌ Unexpected response type: {type(data)}")
            raise ValueError("OpenRouter response is not a JSON object")
        
        # Check for error in response
        if "error" in data:
            error_info = data.get("error", {})
            error_msg = error_info.get("message", "Unknown error")
            logger.error(f"❌ OpenRouter error: {error_msg}")
            raise ValueError(f"OpenRouter API error: {error_msg}")
        
        # Extract completion from choices
        choices = data.get("choices", [])
        if not choices:
            logger.error(f"❌ Empty choices array in response")
            logger.error(f"Full response: {data}")
            raise ValueError(
                "OpenRouter returned empty choices. Check your model name: "
                f"{config.OPENROUTER_MODEL}"
            )
        
        choice = choices[0]
        content = choice.get("message", {}).get("content", "").strip()
        
        if not content:
            logger.error(f"❌ Empty content in response")
            logger.error(f"Choice: {choice}")
            raise ValueError("OpenRouter returned empty response content")
        
        logger.info(f"✅ OpenRouter response: {len(content)} chars")
        return content

    def _call_mistral(self, prompt: str, max_tokens: int) -> str:
        """Call Mistral AI direct API."""
        if not config.MISTRAL_API_KEY:
            raise ValueError("MISTRAL_API_KEY not configured")
        
        headers = {
            "Authorization": f"Bearer {config.MISTRAL_API_KEY}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": config.MISTRAL_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": max_tokens,
            "temperature": config.TEMPERATURE,
        }
        
        try:
            response = requests.post(
                "https://api.mistral.ai/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=self.request_timeout,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("Invalid Mistral API key")
            elif response.status_code == 429:
                raise RuntimeError("Mistral rate limit exceeded. Please try again later.")
            else:
                raise
        
        data = response.json()
        
        if not isinstance(data, dict):
            raise ValueError("Invalid response format from Mistral")
        
        choices = data.get("choices", [])
        if not choices:
            error_msg = data.get("error", {}).get("message", "Empty response from Mistral API")
            raise ValueError(error_msg)
        
        content = choices[0].get("message", {}).get("content", "").strip()
        if not content:
            raise ValueError("Mistral returned empty response")
            
        return content

    def _call_huggingface(self, prompt: str, max_tokens: int) -> str:
        """Call HuggingFace Inference API."""
        if not config.HF_API_KEY:
            raise ValueError("HF_API_KEY not configured")
        
        headers = {"Authorization": f"Bearer {config.HF_API_KEY}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": config.TEMPERATURE,
                "do_sample": True,
                "return_full_text": False,
            },
        }
        url = f"https://api-inference.huggingface.co/models/{config.HF_MODEL}"
        
        try:
            response = requests.post(
                url, 
                headers=headers, 
                json=payload, 
                timeout=self.request_timeout * 1.5  # HF is slower
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise ValueError("Invalid HuggingFace API key")
            elif response.status_code == 429:
                raise RuntimeError("HuggingFace rate limit exceeded. Please try again later.")
            else:
                raise
        
        data = response.json()

        # Handle HF API errors
        if isinstance(data, dict) and "error" in data:
            raise ValueError(f"HuggingFace API error: {data['error']}")

        if isinstance(data, list) and data:
            content = data[0].get("generated_text", "").strip()
            if content:
                return content
        
        raise ValueError("Unexpected or empty response from HuggingFace API")


class RAGPipeline:
    """
    Full RAG pipeline with advanced semantic retrieval:
    Query → Analyze Intent → Multi-Query Generation → Semantic Retrieval → 
    Fallback Strategies → Smart Answer Formatting → Generate Answer
    """

    def __init__(self, embedding_engine: EmbeddingEngine):
        self.embedding_engine = embedding_engine
        self.llm_client = LLMClient()
        
        # Initialize advanced semantic modules
        self.query_analyzer = create_query_analyzer()
        self.semantic_retriever = create_semantic_retriever(
            embedding_engine,
            debug=config.__dict__.get('DEBUG', False)
        )
        self.answer_formatter = create_answer_formatter(
            debug=config.__dict__.get('DEBUG', False)
        )
        
        # Feature flags
        self.use_semantic_retrieval = config.ENABLE_MULTI_QUERY
        self.use_query_rewriting = config.ENABLE_QUERY_REWRITING
        
        logger.info("RAGPipeline initialized with advanced semantic retrieval")

    def query(
        self,
        question: str,
        chat_history: List[dict] = None,
        top_k: int = None,
    ) -> Tuple[str, List[TextChunk]]:
        """
        Execute the full RAG pipeline for a user question.
        
        Returns:
            - answer (str): LLM-generated answer
            - retrieved_chunks (List[TextChunk]): source chunks used
        """
        # Validate question
        if not question or not question.strip():
            return ("Please ask a question.", [])
        
        if len(question) > 1000:
            question = question[:1000]
            logger.warning("Question truncated to 1000 characters")
        
        if not self.embedding_engine.is_ready:
            return (
                "⚠️ No papers have been processed yet. "
                "Please upload and process PDFs first.",
                [],
            )

        try:
            # ── 1. Retrieve relevant chunks ───────────────────────────────────────
            logger.info(f"🔎 RAG Query: '{question[:100]}'")
            logger.info(f"📊 Index status: {self.embedding_engine.index.ntotal} vectors, {len(self.embedding_engine.chunks)} chunks")
            
            results = self.embedding_engine.search(question, top_k=top_k)
            
            logger.info(f"✅ Retrieval returned {len(results)} chunks (threshold={config.SIMILARITY_THRESHOLD})")
            if results:
                for i, (chunk, score) in enumerate(results, 1):
                    logger.info(f"   [{i}] {chunk.paper_display_name} | Score: {score:.4f} | Words: {chunk.word_count}")

            if not results:
                logger.warning(f"⚠️ No chunks matched query - try different keywords or check uploaded papers")
                # Try to give helpful feedback
                return (
                    "📋 No relevant sections found in the uploaded papers for your question.\n\n"
                    "**Tips to improve your search:**\n"
                    "• Try using different keywords related to your question\n"
                    "• Ask more specific questions about the paper content\n"
                    "• Check that you've uploaded the correct papers\n"
                    "• Try asking about methodology, results, or specific technical terms mentioned in the papers",
                    [],
                )

            retrieved_chunks = [chunk for chunk, _ in results]

            # ── 2. Build context string ───────────────────────────────────────────
            context_parts = []
            for i, (chunk, score) in enumerate(results, 1):
                context_parts.append(
                    f"[Source {i} — {chunk.paper_display_name}]\n{chunk.text}"
                )
            context = "\n\n---\n\n".join(context_parts)
            original_context_len = len(context)
            context = truncate_text(context, max_chars=10000)  # Increased from 6000 for better context
            
            logger.info(f"📝 Context: {len(context)} chars (original: {original_context_len})")

            # ── 3. Format chat history ────────────────────────────────────────────
            history_str = ""
            if chat_history:
                recent = chat_history[-4:]  # Keep last 4 turns
                for msg in recent:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_str += f"{role}: {msg['content']}\n"

            # ── 4. Build full prompt ──────────────────────────────────────────────
            prompt = RAG_PROMPT.format(
                context=context,
                chat_history=history_str or "None",
                question=question,
            )
            
            logger.info(f"💬 Prompt length: {len(prompt)} chars")

            # ── 5. Generate answer ────────────────────────────────────────────────
            logger.info(f"🤖 Calling LLM ({config.LLM_PROVIDER})...")
            answer = self.llm_client.generate(prompt)
            
            logger.info(f"✅ LLM response: {len(answer)} chars")
            
            # Validate response
            if not answer or not answer.strip():
                return ("❌ LLM returned empty response. Please try again.", retrieved_chunks)
                
            return answer, retrieved_chunks
            
        except TimeoutError as e:
            logger.error(f"⏱️ Query timeout: {e}")
            return f"❌ Request timed out: {str(e)}", []
        except ConnectionError as e:
            logger.error(f"🔌 Connection error during query: {e}")
            return f"❌ Connection failed: {str(e)}", []
        except ValueError as e:
            logger.error(f"❌ Invalid API response: {e}")
            return f"❌ Invalid response: {str(e)}", []
        except Exception as e:
            logger.error(f"❌ Unexpected error in RAG query: {e}", exc_info=True)
            return f"❌ Error: {str(e)}", []

    def generate_with_prompt(self, prompt: str, max_tokens: int = None) -> str:
        """
        Direct LLM call with a custom prompt (used by summarizer, comparator, etc.)
        """
        try:
            return self.llm_client.generate(prompt, max_tokens=max_tokens or 1500)
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise

    def query_semantic(
        self,
        question: str,
        chat_history: List[dict] = None,
        top_k: int = None,
        debug: bool = False,
    ) -> Tuple[str, List[TextChunk]]:
        """
        Advanced semantic query using multi-query retrieval, fallback logic,
        and intelligent answer formatting.
        
        This is the new intelligent RAG that never gives up on finding an answer.
        
        Args:
            question: User's query
            chat_history: Conversation history
            top_k: Number of chunks to retrieve
            debug: Enable debug logging
            
        Returns:
            Tuple of (answer, retrieved_chunks)
        """
        top_k = top_k or config.TOP_K_RETRIEVAL
        
        # Validate question
        if not question or not question.strip():
            return ("Please ask a question.", [])
        
        if len(question) > 1000:
            question = question[:1000]
            logger.warning("Question truncated to 1000 characters")
        
        if not self.embedding_engine.is_ready:
            return (
                "⚠️ No papers have been processed yet. "
                "Please upload and process PDFs first.",
                [],
            )

        try:
            logger.info(f"🧠 SEMANTIC QUERY: '{question[:100]}'")
            
            # ── 1. Analyze query intent and generate variations ──────────────────
            logger.info("📖 Analyzing query intent...")
            query_analysis = self.query_analyzer.analyze(question)
            
            if debug:
                logger.info(query_analysis.get_analysis_summary())
            
            # Rewrite query if enabled
            if self.use_query_rewriting:
                rewritten = self.query_analyzer.rewrite_query(question)
                if rewritten != question.lower():
                    logger.info(f"✏️  Query rewritten: '{rewritten}'")
                    query_analysis.query_variations.insert(0, rewritten)
            
            # ── 2. Semantic retrieval with multi-query fallback ─────────────────
            logger.info(f"🔍 Semantic retrieval ({len(query_analysis.query_variations)} queries)")
            retrieval_result = self.semantic_retriever.retrieve_semantic(
                queries=query_analysis.query_variations,
                top_k=top_k,
                strategy=config.RETRIEVAL_MERGE_STRATEGY
            )
            
            if not retrieval_result or not retrieval_result.chunks:
                logger.warning("❌ Semantic retrieval returned no chunks — attempting broad fallback")
                # Last-ditch: fall back to basic query() for any result at all
                return self.query(question, chat_history=chat_history, top_k=top_k)
            
            logger.info(f"✅ Retrieved {len(retrieval_result.chunks)} chunks (confidence: {retrieval_result.confidence:.1%})")
            if debug:
                logger.info(retrieval_result.analysis)
            
            # ── 3. Convert retrieved chunks to context ─────────────────────────
            retrieved_chunks = []
            context_parts = []
            
            for i, retrieved_chunk in enumerate(retrieval_result.chunks, 1):
                try:
                    # Try to get the full chunk from embedding engine
                    chunk = self.embedding_engine.chunks[retrieved_chunk.chunk_index]
                    retrieved_chunks.append(chunk)
                    context_parts.append(
                        f"[Source {i}]\n{chunk.text}\n(Score: {retrieved_chunk.score:.3f})"
                    )
                except (IndexError, AttributeError):
                    # Fallback to retrieved chunk content
                    context_parts.append(
                        f"[Source {i}]\n{retrieved_chunk.content}\n(Score: {retrieved_chunk.score:.3f})"
                    )
            
            context = "\n\n---\n\n".join(context_parts)
            context = truncate_text(context, max_chars=12000)  # More context for semantic
            
            logger.info(f"📝 Context: {len(context)} chars")
            
            # ── 4. Build prompt with chat history ──────────────────────────────
            history_str = ""
            if chat_history:
                recent = chat_history[-4:]
                for msg in recent:
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_str += f"{role}: {msg['content']}\n"
            
            prompt = RAG_PROMPT.format(
                context=context,
                chat_history=history_str or "None",
                question=question,
            )
            
            # ── 5. Generate LLM response ───────────────────────────────────────
            logger.info(f"🤖 Calling LLM ({config.LLM_PROVIDER})...")
            raw_answer = self.llm_client.generate(prompt)
            
            logger.info(f"✅ LLM response: {len(raw_answer)} chars")
            
            # ── 6. Format answer intelligently ────────────────────────────────
            formatted_answer = self.answer_formatter.format_answer(
                llm_response=raw_answer,
                retrieval_result=retrieval_result,
                original_query=question,
                query_analysis=query_analysis
            )
            
            final_answer = self.answer_formatter.enhance_conversational(
                formatted_answer.content,
                question
            )
            
            logger.info(f"📊 Answer formatted (confidence: {formatted_answer.confidence:.1%})")
            
            return final_answer, retrieved_chunks
            
        except TimeoutError as e:
            logger.error(f"⏱️ Query timeout: {e}")
            return f"❌ Request timed out. Please try again.", []
        except ConnectionError as e:
            logger.error(f"🔌 Connection error: {e}")
            return f"❌ Connection failed. Please check your API configuration.", []
        except ValueError as e:
            logger.error(f"❌ Invalid response: {e}")
            return f"❌ Error processing response. Please try again.", []
        except Exception as e:
            logger.error(f"❌ Unexpected error in semantic query: {e}", exc_info=True)
            return f"❌ An error occurred. Please try again.", []

