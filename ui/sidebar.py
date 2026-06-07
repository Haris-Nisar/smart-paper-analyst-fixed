"""
sidebar.py - Sidebar navigation and global state display.
"""

import html
import streamlit as st
from ui.components import logo_header, status_pill
from utils.config import config


PAGES = [
    ("🏠", "Home",               "home"),
    ("📤", "Upload Papers",      "upload"),
    ("💬", "AI Chat",            "chat"),
    ("📋", "Summarization",      "summarize"),
    ("⚖️", "Paper Comparison",  "compare"),
    ("🔭", "Research Gaps",      "gaps"),
    ("🔍", "Semantic Search",    "search"),
    ("ℹ️",  "About",             "about"),
]


def render_sidebar(embedding_engine) -> str:
    """
    Render sidebar navigation.
    Returns the currently selected page key.
    """
    with st.sidebar:
        logo_header()

        # ── Status indicator ───────────────────────────────────
        st.markdown("**System Status**")
        status_pill(
            ready=embedding_engine.is_ready,
            count=len(embedding_engine.chunks) if embedding_engine.is_ready else 0,
        )
        st.markdown("")

        # ── Navigation (Premium Style) ─────────────────────────────────────────
        st.markdown("""
        <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.6px;
                    color:var(--text-muted);margin-bottom:0.75rem;font-weight:700;padding:0 0.25rem">
        📍 Navigation
        </div>
        """, unsafe_allow_html=True)

        # Initialize selected page (avoid infinite reruns)
        if "page" not in st.session_state:
            st.session_state.page = "home"

        previous_page = st.session_state.page

        for icon, label, key in PAGES:
            is_active = st.session_state.page == key
            btn_type = "primary" if is_active else "secondary"

            if st.button(
                f"{icon}  {label}",
                key=f"nav_{key}",
                use_container_width=True,
                type=btn_type,
            ):
                st.session_state.page = key
                # Only rerun if page actually changed
                if previous_page != key:
                    st.rerun()

        # ── Papers loaded (Premium Style) ──────────────────────────────────────
        if "papers" in st.session_state and st.session_state.papers:
            st.markdown("---")
            st.markdown("""
            <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.6px;
                        color:var(--text-muted);margin-bottom:0.75rem;font-weight:700;padding:0 0.25rem">
            📚 Loaded Papers
            </div>
            """, unsafe_allow_html=True)

            for paper in st.session_state.papers:
                safe_name = html.escape(paper.display_name[:32])
                st.markdown(f"""
                <div style="background:var(--bg-card-hover);border:1px solid var(--border-color);
                            border-radius:10px;padding:0.65rem 0.85rem;margin:0.35rem 0;
                            font-size:0.8rem;color:var(--text-secondary);
                            transition:all 0.2s ease;cursor:pointer"
                     onmouseover="this.style.borderColor='var(--border-accent)';this.style.background='var(--bg-card-active)'"
                     onmouseout="this.style.borderColor='var(--border-color)';this.style.background='var(--bg-card-hover)'">
                    📄 <strong>{safe_name}{'…' if len(paper.display_name) > 32 else ''}</strong>
                    <div style="font-size:0.7rem;color:var(--text-muted);margin-top:0.25rem;font-weight:500">
                    {paper.num_pages}p · {paper.num_words:,}w
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if st.button("🗑️ Clear All Papers", key="clear_papers", use_container_width=True):
                st.session_state.papers = []
                embedding_engine.clear_index()
                if "chat_session" in st.session_state:
                    st.session_state.chat_session.clear()
                st.rerun()

        # ── Footer (Premium Style) ────────────────────────────────────────────
        st.markdown("---")
        st.markdown(f"""
        <div style="text-align:center;font-size:0.7rem;color:var(--text-muted);line-height:1.8">
            <strong>v{config.APP_VERSION}</strong><br>
            Smart Paper Analyst<br>
            <span style="color:var(--accent-blue);font-weight:600;display:inline-block;margin-top:0.35rem">
            ✨ Powered by RAG + AI
            </span>
        </div>
        """, unsafe_allow_html=True)

    return st.session_state.get("page", "home")
