"""
app.py - Smart Academic Paper Analyst
Main Streamlit application entry point.

Architecture:
  app.py → pages → modules (PDF, RAG, Embeddings, etc.) → utils
"""

import streamlit as st
import time
import logging

# ─── Page config must be FIRST Streamlit call ──────────────────────────────
st.set_page_config(
    page_title="Smart Paper Analyst",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Imports ────────────────────────────────────────────────────────────────
from ui.themes import apply_theme
from ui.sidebar import render_sidebar
from ui.components import (
    page_header, metric_row, info_banner,
    chat_message, search_result_card,
    divider_with_label, typing_animation, paper_badges
)

from modules.pdf_processor import PDFProcessor
from modules.chunking import TextChunker
from modules.embeddings import EmbeddingEngine
from modules.rag_pipeline import RAGPipeline
from modules.summarizer import PaperSummarizer
from modules.comparison import PaperComparator
from modules.research_gap import ResearchGapAnalyzer
from modules.semantic_search import SemanticSearchEngine
from modules.chatbot import ChatSession

from utils.config import config, validate_config
from utils.helpers import format_file_size, ensure_directories
from utils.document_analyzer import analyze_document

logger = logging.getLogger("SmartPaperAnalyst")

# ─── Apply CSS Theme ────────────────────────────────────────────────────────
st.markdown(apply_theme("dark"), unsafe_allow_html=True)

# ─── Ensure directories exist ───────────────────────────────────────────────
ensure_directories("data", "vector_store", "assets", "styles")


# ─── Cached resource initialization ─────────────────────────────────────────
@st.cache_resource
def get_embedding_engine() -> EmbeddingEngine:
    """Singleton embedding engine (loads model once)."""
    engine = EmbeddingEngine()
    # Attempt to load saved index, but don't hang if corrupted
    # This is async/non-blocking - errors are logged, not raised
    try:
        success = engine.load_index()  
        if not success:
            logger.info("Starting with fresh embedding engine (no saved index)")
    except Exception as e:
        logger.error(f"Could not load saved index: {e}")
    return engine


@st.cache_resource
def get_processors():
    """Initialize all processing modules (cached for performance)."""
    engine = get_embedding_engine()
    rag = RAGPipeline(engine)
    return {
        "pdf": PDFProcessor(max_size_mb=config.MAX_FILE_SIZE_MB),
        "chunker": TextChunker(),
        "engine": engine,
        "rag": rag,
        "summarizer": PaperSummarizer(rag),
        "comparator": PaperComparator(rag),
        "gap_analyzer": ResearchGapAnalyzer(rag),
        "searcher": SemanticSearchEngine(engine),
    }


# ─── Session State Initialization ───────────────────────────────────────────
def init_session_state():
    defaults = {
        "papers": [],            # List[ProcessedPaper]
        "doc_types": {},         # {paper_name: DocumentType}
        "page": "home",
        "summaries": {},         # {paper_name: summary_text}
        "comparison_result": "",
        "gap_result": "",
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Chat session needs the RAG pipeline
    if "chat_session" not in st.session_state:
        procs = get_processors()
        st.session_state.chat_session = ChatSession(procs["rag"])


# ════════════════════════════════════════════════════════════════════════════
# PAGE RENDERERS
# ════════════════════════════════════════════════════════════════════════════

def render_home():
    """Dashboard / landing page."""
    page_header(
        "Smart Academic Paper Analyst",
        "Your AI-powered research assistant — summarize, compare, and explore papers",
        "🔬"
    )

    # ── Stats ──────────────────────────────────────────────────────────────
    engine = get_embedding_engine()
    stats = engine.get_stats()
    
    # Sync papers from engine if index is ready (handles loaded indices)
    if engine.is_ready and stats.get("total_chunks", 0) > 0:
        if not st.session_state.papers and "num_papers" in stats:
            # Index is loaded but session_state.papers is empty
            # This happens when user returns to app after index was saved
            logger.info(f"Syncing {stats.get('num_papers', 0)} papers from loaded index")
    
    papers = st.session_state.papers
    num_papers = len(papers) if papers else stats.get("num_papers", 0)

    metric_row([
        {"icon": "📄", "label": "Papers Loaded",  "value": str(num_papers)},
        {"icon": "🧩", "label": "Text Chunks",    "value": str(stats.get("total_chunks", 0))},
        {"icon": "🔍", "label": "Index Status",   "value": "Ready" if engine.is_ready else "Empty"},
        {"icon": "🤖", "label": "LLM Provider",   "value": config.LLM_PROVIDER.title()},
    ])

    st.markdown("---")

    # ── Feature Overview ───────────────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.5px;
                        color:var(--text-muted);margin-bottom:1rem">Core Features</div>
            <div style="display:grid;gap:0.6rem">
                <div style="display:flex;align-items:flex-start;gap:0.75rem">
                    <span style="font-size:1.2rem">💬</span>
                    <div><b style="color:var(--text-primary)">AI Chatbot</b>
                    <p style="color:var(--text-muted);font-size:0.83rem;margin:0.1rem 0 0">Ask questions, get accurate grounded answers</p></div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:0.75rem">
                    <span style="font-size:1.2rem">📋</span>
                    <div><b style="color:var(--text-primary)">Smart Summarization</b>
                    <p style="color:var(--text-muted);font-size:0.83rem;margin:0.1rem 0 0">Structured academic summaries in seconds</p></div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:0.75rem">
                    <span style="font-size:1.2rem">⚖️</span>
                    <div><b style="color:var(--text-primary)">Paper Comparison</b>
                    <p style="color:var(--text-muted);font-size:0.83rem;margin:0.1rem 0 0">Side-by-side AI analysis of multiple papers</p></div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:0.75rem">
                    <span style="font-size:1.2rem">🔭</span>
                    <div><b style="color:var(--text-primary)">Research Gap Finder</b>
                    <p style="color:var(--text-muted);font-size:0.83rem;margin:0.1rem 0 0">Identify unexplored areas and future directions</p></div>
                </div>
                <div style="display:flex;align-items:flex-start;gap:0.75rem">
                    <span style="font-size:1.2rem">🔍</span>
                    <div><b style="color:var(--text-primary)">Semantic Search</b>
                    <p style="color:var(--text-muted);font-size:0.83rem;margin:0.1rem 0 0">Find relevant content by meaning, not just keywords</p></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.5px;
                        color:var(--text-muted);margin-bottom:1rem">How it works</div>
            <div style="display:grid;gap:0.75rem">
                <div style="display:flex;align-items:center;gap:1rem">
                    <div style="width:32px;height:32px;border-radius:50%;
                                background:linear-gradient(135deg,#667eea,#764ba2);
                                display:flex;align-items:center;justify-content:center;
                                font-weight:700;font-size:0.85rem;flex-shrink:0">1</div>
                    <div style="color:var(--text-secondary);font-size:0.9rem">
                        <b style="color:var(--text-primary)">Upload PDFs</b> — One or multiple research papers
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:1rem">
                    <div style="width:32px;height:32px;border-radius:50%;
                                background:linear-gradient(135deg,#4facfe,#00f2fe);
                                display:flex;align-items:center;justify-content:center;
                                font-weight:700;font-size:0.85rem;flex-shrink:0">2</div>
                    <div style="color:var(--text-secondary);font-size:0.9rem">
                        <b style="color:var(--text-primary)">AI Processing</b> — Text extraction, chunking & embeddings
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:1rem">
                    <div style="width:32px;height:32px;border-radius:50%;
                                background:linear-gradient(135deg,#43e97b,#38f9d7);
                                display:flex;align-items:center;justify-content:center;
                                font-weight:700;font-size:0.85rem;flex-shrink:0">3</div>
                    <div style="color:var(--text-secondary);font-size:0.9rem">
                        <b style="color:var(--text-primary)">RAG Pipeline</b> — Semantic retrieval + LLM generation
                    </div>
                </div>
                <div style="display:flex;align-items:center;gap:1rem">
                    <div style="width:32px;height:32px;border-radius:50%;
                                background:linear-gradient(135deg,#f093fb,#f5576c);
                                display:flex;align-items:center;justify-content:center;
                                font-weight:700;font-size:0.85rem;flex-shrink:0">4</div>
                    <div style="color:var(--text-secondary);font-size:0.9rem">
                        <b style="color:var(--text-primary)">Analyze & Explore</b> — Chat, summarize, compare, search
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Quick start prompt ─────────────────────────────────────────────────
    if not st.session_state.papers:
        st.markdown("---")
        info_banner(
            "👆 Start by uploading PDF research papers via <b>Upload Papers</b> in the sidebar.",
            "info"
        )


def render_upload():
    """PDF upload and processing page."""
    page_header("Upload Research Papers", "Upload one or more PDFs to begin analysis", "📤")

    procs = get_processors()
    engine = get_embedding_engine()

    # ── Upload widget ──────────────────────────────────────────────────────
    uploaded_files = st.file_uploader(
        "Drag & drop your research paper PDFs here",
        type=["pdf"],
        accept_multiple_files=True,
        help=f"Max {config.MAX_FILE_SIZE_MB} MB per file · PDF format only",
        key="pdf_uploader",
    )

    if uploaded_files:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown(f"**{len(uploaded_files)} file(s) selected:**")
            for f in uploaded_files:
                size_str = format_file_size(f.size)
                st.markdown(f"""
                <div style="background:var(--bg-card);border:1px solid var(--border-color);
                            border-radius:8px;padding:0.6rem 1rem;margin:0.25rem 0;
                            display:flex;justify-content:space-between;align-items:center">
                    <span style="color:var(--text-secondary);font-size:0.9rem">📄 {f.name}</span>
                    <span style="color:var(--text-muted);font-size:0.8rem">{size_str}</span>
                </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown("")
            st.markdown("")
            process_btn = st.button(
                "⚡ Process Papers",
                use_container_width=True,
                type="primary",
            )

        if process_btn:
            with st.status("Processing papers...", expanded=True) as status:
                # Step 1: Extract text
                st.write("📖 Extracting text from PDFs...")
                try:
                    papers, errors = procs["pdf"].process_multiple_pdfs(uploaded_files)
                except Exception as e:
                    st.error(f"❌ PDF extraction failed: {str(e)}")
                    status.update(label="❌ Processing failed", state="error")
                    return

                # Show errors
                if errors:
                    for err in errors:
                        st.error(f"❌ {err}")

                if not papers:
                    st.error("❌ No papers were successfully processed.")
                    status.update(label="❌ Processing failed", state="error")
                    return

                st.write(f"✅ Extracted text from {len(papers)} paper(s)")

                # Analyze document types
                st.write("🔍 Analyzing document types...")
                for paper in papers:
                    analysis = analyze_document(paper.full_text)
                    st.session_state.doc_types[paper.display_name] = analysis["type"]
                    if analysis["confidence"] > 0.5:
                        st.info(f"📋 {paper.display_name}: Detected as **{analysis['type'].replace('_', ' ').title()}**")

                # Step 2: Chunk text
                st.write("🧩 Chunking text into semantic segments...")
                try:
                    chunks = procs["chunker"].chunk_multiple_papers(papers)
                except Exception as e:
                    st.error(f"❌ Chunking failed: {str(e)}")
                    status.update(label="❌ Processing failed", state="error")
                    return
                
                if not chunks:
                    st.error("❌ No chunks created from papers.")
                    status.update(label="❌ Processing failed", state="error")
                    return
                
                st.write(f"✅ Created {len(chunks)} text chunks")

                # Step 3: Build embeddings & FAISS index
                st.write("🧠 Generating embeddings and building vector index...")
                try:
                    progress = st.progress(0)
                    engine.build_index(chunks)
                    progress.progress(100)
                except Exception as e:
                    st.error(f"❌ Embedding/indexing failed: {str(e)}")
                    status.update(label="❌ Processing failed", state="error")
                    return
                
                st.write(f"✅ FAISS index built ({engine.index.ntotal} vectors)")

                # Step 4: Save index
                st.write("💾 Saving index to disk...")
                try:
                    engine.save_index()
                except Exception as e:
                    st.warning(f"⚠️ Could not save index to disk: {str(e)}")
                
                st.write("✅ Index saved")

                # Update session state
                st.session_state.papers.extend(papers)
                # Deduplicate by file hash
                seen = set()
                unique_papers = []
                for p in st.session_state.papers:
                    if p.file_hash not in seen:
                        seen.add(p.file_hash)
                        unique_papers.append(p)
                st.session_state.papers = unique_papers

                # Reset chat session with updated RAG
                st.session_state.chat_session = ChatSession(procs["rag"])

                status.update(label="✅ All papers processed successfully!", state="complete")

            st.balloons()
            st.rerun()

    # ── Currently loaded papers ────────────────────────────────────────────
    if st.session_state.papers:
        st.markdown("---")
        st.markdown("### 📚 Currently Loaded Papers")
        for i, paper in enumerate(st.session_state.papers):
            with st.expander(f"📄 {paper.display_name}  ·  {paper.num_pages} pages  ·  {paper.num_words:,} words"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Pages", paper.num_pages)
                with col2:
                    st.metric("Words", f"{paper.num_words:,}")
                with col3:
                    st.metric("File", paper.filename[:20])

                if paper.metadata.get("author", "Unknown") != "Unknown":
                    st.caption(f"👤 Author: {paper.metadata.get('author', 'Unknown')}")

                # Show first 500 chars of text
                preview = paper.full_text[:600].strip()
                st.text_area("Text Preview", value=preview + "...", height=120, disabled=True)


def render_chat():
    """AI Chatbot page."""
    page_header("AI Research Chat", "Ask questions about your uploaded papers", "💬")

    engine = get_embedding_engine()

    if not engine.is_ready:
        info_banner("Please upload and process papers before starting a chat session.", "warning")
        return

    chat_session: ChatSession = st.session_state.chat_session

    # ── Chat history display ───────────────────────────────────────────────
    if chat_session.is_empty:
        st.markdown("""
        <div style="text-align:center;padding:2rem;color:var(--text-muted)">
            <div style="font-size:3rem;margin-bottom:1rem">💬</div>
            <div style="font-size:1.1rem;color:var(--text-secondary);font-weight:500">
                Start a conversation about your papers
            </div>
            <div style="font-size:0.85rem;margin-top:0.5rem">
                Ask about methodology, findings, limitations, datasets, and more
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        chat_container = st.container()
        with chat_container:
            for msg in chat_session.history:
                chat_message(
                    role=msg.role,
                    content=msg.content,
                    timestamp=msg.timestamp,
                    sources=msg.sources if msg.role == "assistant" else [],
                )
                
                # Show retrieval scores for assistant messages (for debugging)
                if msg.role == "assistant" and hasattr(msg, '_retrieval_scores') and msg._retrieval_scores:
                    with st.expander("📊 Debug: Retrieval Scores"):
                        st.json({
                            "source": score[0],
                            "similarity": f"{score[1]:.4f}"
                        } for score in msg._retrieval_scores[:5])  # Show top 5

    # ── Suggested questions ────────────────────────────────────────────────
    if chat_session.is_empty:
        divider_with_label("Suggested Questions")
        
        # Get unique document types from loaded papers
        doc_types_set = set(st.session_state.doc_types.values()) if st.session_state.doc_types else set()
        
        # Generate suggestions based on document types
        suggestions = []
        if doc_types_set:
            from utils.document_analyzer import get_recommended_questions
            # Combine suggestions from all document types
            for doc_type in doc_types_set:
                suggestions.extend(get_recommended_questions(doc_type))
            # Remove duplicates while preserving order
            seen = set()
            suggestions = [s for s in suggestions if not (s in seen or seen.add(s))]
            suggestions = suggestions[:6]  # Show top 6
        else:
            # Default suggestions if no documents are detected
            suggestions = [
                "What is the main topic of this document?",
                "What are the key points discussed?",
                "What conclusions or findings are presented?",
                "What actions or recommendations are suggested?",
                "What is the significance of this document?",
                "What further research or steps are needed?",
            ]
        
        cols = st.columns(3)
        for i, suggestion in enumerate(suggestions):
            with cols[i % 3]:
                if st.button(suggestion, key=f"sugg_{i}", use_container_width=True):
                    st.session_state._pending_question = suggestion
                    st.rerun()

    # ── Input box ─────────────────────────────────────────────────────────
    st.markdown("---")

    col_input, col_btn = st.columns([5, 1])
    with col_input:
        user_input = st.text_input(
            "Your question",
            placeholder="Ask anything about the uploaded research papers...",
            label_visibility="collapsed",
            key="chat_input",
        )
    with col_btn:
        send_btn = st.button("Send ➤", type="primary", use_container_width=True)

    # Handle pending suggestion click
    pending = st.session_state.pop("_pending_question", None)
    question = None
    
    if send_btn and user_input and user_input.strip():
        question = user_input.strip()
    elif pending:
        question = pending

    if question:
        # Validate question
        if len(question) > 1000:
            st.warning("Question is too long (max 1000 characters). Please shorten it.")
        else:
            with st.spinner("🤔 Thinking..."):
                try:
                    answer, sources = chat_session.ask(question)
                    
                    # Show retrieval stats for debugging
                    if sources:
                        with st.expander("📊 Retrieval Info"):
                            st.success(f"✅ Retrieved {len(sources)} source(s)")
                            for source in sources:
                                st.markdown(f"  • {source}")
                    
                    st.rerun()
                except ValueError as e:
                    st.error(f"❌ Invalid input: {str(e)}")
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

    # ── Clear chat button ──────────────────────────────────────────────────
    if not chat_session.is_empty:
        if st.button("🗑️ Clear Chat History", key="clear_chat"):
            chat_session.clear()
            st.rerun()


def render_summarize():
    """Paper summarization page."""
    page_header("Paper Summarization", "Generate structured academic summaries", "📋")

    engine = get_embedding_engine()
    procs = get_processors()
    papers = st.session_state.papers

    if not papers:
        info_banner("Please upload papers first.", "warning")
        return

    # ── Paper selector ─────────────────────────────────────────────────────
    paper_names = [p.display_name for p in papers]
    selected_name = st.selectbox("Select paper to summarize", paper_names, key="sum_selector")
    selected_paper = next(p for p in papers if p.display_name == selected_name)

    col1, col2 = st.columns([3, 1])
    with col1:
        summarize_btn = st.button("🧠 Generate Summary", type="primary", key="sum_btn")
    with col2:
        clear_btn = st.button("🗑️ Clear", key="sum_clear")

    if clear_btn:
        st.session_state.summaries.pop(selected_name, None)
        st.rerun()

    # ── Generate summary ───────────────────────────────────────────────────
    if summarize_btn:
        with st.spinner(f"Generating summary for '{selected_name}'..."):
            try:
                summary = procs["summarizer"].summarize(selected_paper)
                st.session_state.summaries[selected_name] = summary
            except Exception as e:
                st.error(f"❌ Summarization failed: {str(e)}")
                return
        st.success("✅ Summary generated!")

    # ── Display summary ────────────────────────────────────────────────────
    if selected_name in st.session_state.summaries:
        summary = st.session_state.summaries[selected_name]
        st.markdown("---")
        st.markdown(f"### Summary: {selected_name}")
        st.markdown(summary)

        # Download button
        st.download_button(
            label="⬇️ Download Summary (.md)",
            data=f"# Summary: {selected_name}\n\n{summary}",
            file_name=f"summary_{selected_name.replace(' ', '_')}.md",
            mime="text/markdown",
        )


def render_compare():
    """Multi-paper comparison page."""
    page_header("Paper Comparison", "Compare multiple papers side-by-side with AI", "⚖️")

    procs = get_processors()
    papers = st.session_state.papers

    if len(papers) < 2:
        info_banner(
            "Please upload at least 2 research papers to enable comparison.",
            "warning"
        )
        return

    # ── Paper selector ─────────────────────────────────────────────────────
    paper_names = [p.display_name for p in papers]
    selected_names = st.multiselect(
        "Select papers to compare (2 or more)",
        options=paper_names,
        default=paper_names[:min(3, len(paper_names))],
        key="compare_selector",
    )

    if len(selected_names) < 2:
        st.warning("Select at least 2 papers.")
        return

    selected_papers = [p for p in papers if p.display_name in selected_names]

    col1, col2 = st.columns([3, 1])
    with col1:
        compare_btn = st.button("🤖 Generate Comparison", type="primary", key="compare_btn")
    with col2:
        clear_btn = st.button("🗑️ Clear", key="cmp_clear")

    if clear_btn:
        st.session_state.comparison_result = ""
        st.rerun()

    # ── Generate comparison ────────────────────────────────────────────────
    if compare_btn:
        with st.spinner(f"Comparing {len(selected_papers)} papers..."):
            try:
                result = procs["comparator"].compare(selected_papers)
                st.session_state.comparison_result = result
            except Exception as e:
                st.error(f"❌ Comparison failed: {str(e)}")
                return
        st.success("✅ Comparison complete!")

    # ── Display comparison ─────────────────────────────────────────────────
    if st.session_state.comparison_result:
        st.markdown("---")
        paper_badges(selected_names)
        st.markdown("")
        st.markdown(st.session_state.comparison_result)

        # Download
        st.download_button(
            label="⬇️ Download Report (.md)",
            data=f"# Paper Comparison Report\n\nPapers: {', '.join(selected_names)}\n\n{st.session_state.comparison_result}",
            file_name="paper_comparison_report.md",
            mime="text/markdown",
        )


def render_gaps():
    """Research gap analysis page."""
    page_header("Research Gap Analysis", "Identify unexplored areas and future directions", "🔭")

    procs = get_processors()
    papers = st.session_state.papers

    if not papers:
        info_banner("Please upload papers first.", "warning")
        return

    # ── Paper selector ─────────────────────────────────────────────────────
    paper_names = [p.display_name for p in papers]
    selected_names = st.multiselect(
        "Select papers to analyze",
        options=paper_names,
        default=paper_names,
        key="gap_selector",
    )
    selected_papers = [p for p in papers if p.display_name in selected_names]

    if not selected_papers:
        st.warning("Please select at least one paper.")
        return

    col1, col2 = st.columns([3, 1])
    with col1:
        gap_btn = st.button("🔭 Analyze Research Gaps", type="primary", key="gap_btn")
    with col2:
        clear_btn = st.button("🗑️ Clear", key="gap_clear")

    if clear_btn:
        st.session_state.gap_result = ""
        st.rerun()

    # ── Generate analysis ──────────────────────────────────────────────────
    if gap_btn:
        with st.spinner("Identifying research gaps..."):
            try:
                result = procs["gap_analyzer"].analyze(selected_papers)
                st.session_state.gap_result = result
            except Exception as e:
                st.error(f"❌ Analysis failed: {str(e)}")
                return
        st.success("✅ Analysis complete!")

    # ── Display result ─────────────────────────────────────────────────────
    if st.session_state.gap_result:
        st.markdown("---")
        paper_badges(selected_names)
        st.markdown("")
        st.markdown(st.session_state.gap_result)

        st.download_button(
            label="⬇️ Download Analysis (.md)",
            data=f"# Research Gap Analysis\n\nPapers: {', '.join(selected_names)}\n\n{st.session_state.gap_result}",
            file_name="research_gap_analysis.md",
            mime="text/markdown",
        )


def render_search():
    """Semantic search page."""
    page_header("Semantic Search", "Find relevant content by meaning across all papers", "🔍")

    engine = get_embedding_engine()
    procs = get_processors()

    if not engine.is_ready:
        info_banner("Please upload and process papers first.", "warning")
        return

    # ── Search input ───────────────────────────────────────────────────────
    col1, col2 = st.columns([4, 1])
    with col1:
        query = st.text_input(
            "Search query",
            placeholder="E.g., transformer attention mechanism, BERT fine-tuning, dataset preprocessing...",
            label_visibility="collapsed",
            key="search_input",
        )
    with col2:
        top_k = st.selectbox("Results", [5, 8, 10, 15], index=1, key="search_topk")

    search_btn = st.button("🔍 Search", type="primary", key="search_btn")

    # ── Run search ─────────────────────────────────────────────────────────
    if search_btn:
        if not query or not query.strip():
            st.warning("Please enter a search query.")
        else:
            search_query = query.strip()
            if len(search_query) > 500:
                st.warning("Query is too long (max 500 characters).")
            else:
                with st.spinner(f"Searching for: '{search_query}'..."):
                    try:
                        results = procs["searcher"].search(search_query, top_k=top_k)
                    except Exception as e:
                        st.error(f"❌ Search failed: {str(e)}")
                        results = []

                if results:
                    st.markdown(f"---")
                    st.markdown(f"**{len(results)} results** for: *{search_query}*")
                    st.markdown("")

                    for result in results:
                        search_result_card(
                            rank=result.rank,
                            paper_name=result.paper_name,
                            score_pct=result.score_pct,
                            preview=result.preview,
                            full_text=result.chunk.text,
                        )
                else:
                    info_banner("No relevant content found. Try a different query.", "warning")


def render_about():
    """About page with architecture and tech stack info."""
    page_header("About", "Smart Academic Paper Analyst", "ℹ️")

    st.markdown("""
    <div class="glass-card">
        <h3 style="color:var(--accent-blue);margin-top:0">🔬 Smart Academic Paper Analyst</h3>
        <p style="color:var(--text-secondary);line-height:1.7">
            A production-quality AI-powered research tool built with <b>Retrieval-Augmented Generation (RAG)</b>.
            Upload research papers and leverage state-of-the-art AI to analyze, summarize, compare,
            and extract insights in seconds.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.5px;
                        color:var(--text-muted);margin-bottom:1rem">⚙️ Tech Stack</div>
            <table style="width:100%;border-collapse:collapse;font-size:0.88rem">
                <tr><td style="padding:0.4rem 0;color:var(--text-muted);width:40%">Frontend</td>
                    <td style="color:var(--accent-blue)">Streamlit</td></tr>
                <tr><td style="padding:0.4rem 0;color:var(--text-muted)">PDF Processing</td>
                    <td style="color:var(--accent-blue)">PyMuPDF (fitz)</td></tr>
                <tr><td style="padding:0.4rem 0;color:var(--text-muted)">Embeddings</td>
                    <td style="color:var(--accent-blue)">all-MiniLM-L6-v2</td></tr>
                <tr><td style="padding:0.4rem 0;color:var(--text-muted)">Vector DB</td>
                    <td style="color:var(--accent-blue)">FAISS (IndexFlatIP)</td></tr>
                <tr><td style="padding:0.4rem 0;color:var(--text-muted)">LLM Orchestration</td>
                    <td style="color:var(--accent-blue)">LangChain</td></tr>
                <tr><td style="padding:0.4rem 0;color:var(--text-muted)">LLM Provider</td>
                    <td style="color:var(--accent-blue)">OpenRouter / Mistral / HF</td></tr>
            </table>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="glass-card">
            <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.5px;
                        color:var(--text-muted);margin-bottom:1rem">🏗️ Architecture</div>
            <div style="font-size:0.88rem;color:var(--text-secondary);line-height:1.8">
                <div>📄 <b style="color:var(--text-primary)">PDF Upload</b> → PyMuPDF extraction</div>
                <div>🧩 <b style="color:var(--text-primary)">Chunking</b> → RecursiveCharacterTextSplitter</div>
                <div>🧠 <b style="color:var(--text-primary)">Embedding</b> → Sentence-Transformers</div>
                <div>🗄️ <b style="color:var(--text-primary)">Indexing</b> → FAISS vector store</div>
                <div>🔎 <b style="color:var(--text-primary)">Retrieval</b> → Cosine similarity search</div>
                <div>🤖 <b style="color:var(--text-primary)">Generation</b> → LLM with RAG context</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("""
    <div class="glass-card" style="margin-top:1rem">
        <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.5px;
                    color:var(--text-muted);margin-bottom:0.75rem">🚀 Getting Started</div>
        <ol style="color:var(--text-secondary);font-size:0.9rem;line-height:2">
            <li>Set your API key in <code>.env</code> (e.g. <code>OPENROUTER_API_KEY=sk-...</code>)</li>
            <li>Install dependencies: <code>pip install -r requirements.txt</code></li>
            <li>Run: <code>streamlit run app.py</code></li>
            <li>Upload PDFs via <b>Upload Papers</b></li>
            <li>Start exploring with Chat, Summarize, Compare, and more!</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)


# ════════════════════════════════════════════════════════════════════════════
# MAIN ROUTER
# ════════════════════════════════════════════════════════════════════════════

def main():
    init_session_state()

    # ── Config validation warning ──────────────────────────────────────────
    is_valid, config_error = validate_config()
    if not is_valid:
        st.warning(f"⚠️ API key not configured. AI features will not work. {config_error}")

    # ── Render sidebar & get current page ──────────────────────────────────
    engine = get_embedding_engine()
    current_page = render_sidebar(engine)

    # ── Route to correct page ──────────────────────────────────────────────
    page_map = {
        "home":      render_home,
        "upload":    render_upload,
        "chat":      render_chat,
        "summarize": render_summarize,
        "compare":   render_compare,
        "gaps":      render_gaps,
        "search":    render_search,
        "about":     render_about,
    }

    renderer = page_map.get(current_page, render_home)
    renderer()


if __name__ == "__main__":
    main()
