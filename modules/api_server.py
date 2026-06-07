"""
api_server.py — REST API wrapper for Smart Paper Analyst
Run this ALONGSIDE your Streamlit app so n8n can call it directly.

Usage:
    python api_server.py

Runs on: http://localhost:5001
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from modules.pdf_processor import PDFProcessor
from modules.embeddings import EmbeddingEngine
from modules.rag_pipeline import RAGPipeline
from modules.summarizer import PaperSummarizer
from modules.comparison import PaperComparator
from modules.research_gap import ResearchGapAnalyzer
from modules.semantic_search import SemanticSearchEngine
from modules.chatbot import ChatSession

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SmartPaperAPI")

app = Flask(__name__)
CORS(app)  # Allow n8n to call from any origin

# ─── Initialize shared components ─────────────────────────────────────────────
embedding_engine = EmbeddingEngine()
rag_pipeline = RAGPipeline(embedding_engine)

# Load existing FAISS index if available
try:
    embedding_engine.load_index()
    logger.info("✅ FAISS index loaded successfully")
except Exception as e:
    logger.warning(f"⚠️ No existing FAISS index: {e}")

# ─── Shared chat session ───────────────────────────────────────────────────────
chat_session = ChatSession(rag_pipeline)


# ─── ROUTES ───────────────────────────────────────────────────────────────────

@app.route("/api/status", methods=["GET"])
def status():
    """Health check endpoint."""
    paper_count = len(embedding_engine.metadata) if hasattr(embedding_engine, 'metadata') else 0
    return jsonify({
        "status": "running",
        "papers_loaded": paper_count,
        "faiss_ready": embedding_engine.index is not None,
        "version": "1.0.0"
    })


@app.route("/api/chat", methods=["POST"])
def chat():
    """
    Chat with uploaded papers using RAG.
    Body: { "question": "What is the methodology?" }
    """
    data = request.get_json()
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"error": "question field required"}), 400

    if embedding_engine.index is None:
        return jsonify({"error": "No papers loaded. Please upload PDFs first via /api/upload"}), 400

    try:
        answer = rag_pipeline.answer(question, chat_history=chat_session.get_history())
        chat_session.add(question, answer)
        return jsonify({
            "success": True,
            "action": "chat",
            "question": question,
            "answer": answer,
            "chat_history_length": len(chat_session.get_history())
        })
    except Exception as e:
        logger.error(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/upload", methods=["POST"])
def upload():
    """
    Upload and process a PDF file.
    Form-data: file = <pdf file>
    """
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded. Send PDF as multipart form-data with key 'file'"}), 400

    uploaded_file = request.files["file"]
    if not uploaded_file.filename.endswith(".pdf"):
        return jsonify({"error": "Only PDF files are supported"}), 400

    try:
        # Save temp file
        temp_path = f"/tmp/{uploaded_file.filename}"
        uploaded_file.save(temp_path)

        # Process PDF
        processor = PDFProcessor()
        paper = processor.process(temp_path)

        # Add to FAISS index
        embedding_engine.add_paper(paper)
        embedding_engine.save_index()

        return jsonify({
            "success": True,
            "action": "upload",
            "paper_name": paper.display_name,
            "pages": paper.page_count,
            "chunks_created": len(paper.chunks),
            "message": f"✅ '{paper.display_name}' processed and indexed successfully"
        })
    except Exception as e:
        logger.error(f"Upload error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/summarize", methods=["POST"])
def summarize():
    """
    Summarize a loaded paper.
    Body: { "paper_name": "paper1.pdf" }   ← optional, summarizes first paper if omitted
    """
    data = request.get_json()
    paper_name = data.get("paper_name", "").strip()

    if not hasattr(embedding_engine, 'papers') or not embedding_engine.papers:
        return jsonify({"error": "No papers loaded. Upload PDFs first via /api/upload"}), 400

    try:
        # Pick paper
        papers = list(embedding_engine.papers.values())
        if paper_name:
            paper = next((p for p in papers if paper_name.lower() in p.display_name.lower()), papers[0])
        else:
            paper = papers[0]

        summarizer = PaperSummarizer(rag_pipeline)
        summary = summarizer.summarize(paper)

        return jsonify({
            "success": True,
            "action": "summarize",
            "paper": paper.display_name,
            "summary": summary
        })
    except Exception as e:
        logger.error(f"Summarize error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/compare", methods=["POST"])
def compare():
    """
    Compare all loaded papers.
    Body: {}   ← compares all currently loaded papers
    """
    if not hasattr(embedding_engine, 'papers') or len(embedding_engine.papers) < 2:
        return jsonify({"error": "At least 2 papers required for comparison. Upload more PDFs."}), 400

    try:
        papers = list(embedding_engine.papers.values())
        comparator = PaperComparator(rag_pipeline)
        comparison = comparator.compare(papers)

        return jsonify({
            "success": True,
            "action": "compare",
            "papers_compared": [p.display_name for p in papers],
            "comparison": comparison
        })
    except Exception as e:
        logger.error(f"Compare error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/gap", methods=["POST"])
def research_gap():
    """
    Analyze research gaps in loaded papers.
    Body: { "paper_name": "paper1.pdf" }   ← optional
    """
    if not hasattr(embedding_engine, 'papers') or not embedding_engine.papers:
        return jsonify({"error": "No papers loaded. Upload PDFs first via /api/upload"}), 400

    data = request.get_json()
    paper_name = data.get("paper_name", "").strip()

    try:
        papers = list(embedding_engine.papers.values())
        if paper_name:
            paper = next((p for p in papers if paper_name.lower() in p.display_name.lower()), papers[0])
        else:
            paper = papers[0]

        analyzer = ResearchGapAnalyzer(rag_pipeline)
        gap_analysis = analyzer.analyze(paper)

        return jsonify({
            "success": True,
            "action": "gap",
            "paper": paper.display_name,
            "gap_analysis": gap_analysis
        })
    except Exception as e:
        logger.error(f"Gap analysis error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/search", methods=["POST"])
def semantic_search():
    """
    Semantic search across all papers.
    Body: { "question": "neural network architecture" }
    """
    data = request.get_json()
    query = data.get("question", data.get("query", "")).strip()

    if not query:
        return jsonify({"error": "question or query field required"}), 400

    if embedding_engine.index is None:
        return jsonify({"error": "No papers loaded"}), 400

    try:
        search_engine = SemanticSearchEngine(embedding_engine)
        results = search_engine.search(query, top_k=5)

        return jsonify({
            "success": True,
            "action": "search",
            "query": query,
            "results": results
        })
    except Exception as e:
        logger.error(f"Search error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/api/clear", methods=["POST"])
def clear():
    """Clear all loaded papers and reset FAISS index."""
    try:
        embedding_engine.reset()
        chat_session.clear()
        return jsonify({"success": True, "message": "All papers cleared and index reset"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ─── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    port = int(os.getenv("PORT", 5001))
    logger.info(f"🚀 Smart Paper API running on http://localhost:{port}")
    logger.info("📋 Endpoints: /api/status | /api/upload | /api/chat | /api/summarize | /api/compare | /api/gap | /api/search")
    app.run(host="0.0.0.0", port=port, debug=False)
