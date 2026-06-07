"""
components.py - Reusable UI components for the Smart Paper Analyst UI.
"""

import html
import streamlit as st
from typing import List, Optional


def _escape_html(text: str) -> str:
    """Safely escape HTML special characters to prevent XSS."""
    return html.escape(str(text)) if text else ""


def page_header(title: str, subtitle: str = "", icon: str = ""):
    """Render a styled page header with premium appearance."""
    st.markdown(f"""
    <div class="page-header">
        <div class="page-title">{icon} {title}</div>
        {f'<div class="page-subtitle">{subtitle}</div>' if subtitle else ''}
    </div>
    """, unsafe_allow_html=True)


def metric_row(metrics: list):
    """
    Render a row of premium metric cards.
    metrics = [{"label": str, "value": str, "icon": str}, ...]
    """
    cols = st.columns(len(metrics), gap="medium")
    for col, m in zip(cols, metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style="font-size:1.75rem;margin-bottom:0.5rem;line-height:1">{m.get('icon','')}</div>
                <div class="metric-value">{m['value']}</div>
                <div class="metric-label">{m['label']}</div>
            </div>
            """, unsafe_allow_html=True)


def glass_card(content_fn, title: str = "", icon: str = ""):
    """Render content inside a premium glass-morphism card."""
    if title:
        st.markdown(f"""
        <div class="glass-card">
            <div style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.6px;
                        color:var(--text-muted);margin-bottom:1rem;font-weight:700;display:flex;align-items:center;gap:0.5rem">
                <span style="font-size:1rem">{icon}</span>{title}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    content_fn()
    st.markdown('</div>', unsafe_allow_html=True)


def status_pill(ready: bool, count: int = 0):
    """Show a premium status indicator pill."""
    if ready:
        st.markdown(f"""
        <div class="status-pill status-ready">
            ✅ Index Ready · <strong>{count}</strong> chunks
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-pill status-empty">
            ⚠️ No papers indexed
        </div>
        """, unsafe_allow_html=True)


def paper_badges(paper_names: List[str]):
    """Render source paper badges."""
    if not paper_names:
        return
    with st.container():
        cols = st.columns(len(paper_names))
        for col, name in zip(cols, paper_names):
            with col:
                st.markdown(f"📄 **{name}**")


def chat_message(role: str, content: str, timestamp: str = "", sources: List[str] = None):
    """Render a single premium chat message bubble."""
    import html as html_mod

    if role == "user":
        col1, col2 = st.columns([1, 8])
        with col2:
            # Render user bubble with proper HTML escaping
            escaped = _escape_html(content).replace("\n", "<br>")
            ts_html = f"<div style='font-size:0.75rem;opacity:0.6;margin-top:0.4rem;text-align:right'>⏰ {timestamp}</div>" if timestamp else ""
            st.markdown(f"""
            <div class="chat-user-message" style="background:linear-gradient(135deg, #667eea, #764ba2);
                        color:white;padding:1rem 1.25rem;border-radius:18px 4px 18px 18px;
                        margin:0.75rem 0;box-shadow:0 4px 15px rgba(102,126,234,0.3);
                        font-size:0.95rem;line-height:1.7;max-width:100%;word-wrap:break-word;
                        -webkit-text-fill-color:white">
                {escaped}{ts_html}
            </div>
            """, unsafe_allow_html=True)
    else:
        # Assistant message — use st.markdown for content so markdown renders
        col1, col2 = st.columns([8, 1])
        with col1:
            st.markdown(f"""
            <div style="background:var(--bg-card);border:1px solid var(--border-color);
                        border-radius:4px 18px 18px 18px;margin:0.5rem 0 0 0;
                        padding:0.6rem 1.25rem 0.25rem;box-shadow:var(--shadow-sm)">
                <span style="font-size:0.8rem;color:var(--accent-blue);font-weight:600">🤖 Assistant</span>
            </div>
            """, unsafe_allow_html=True)

            # Render markdown content in a styled container
            with st.container():
                st.markdown(
                    f"""<div class="chat-assistant-message" style="
                        background:var(--bg-card);border:1px solid var(--border-color);
                        border-top:none;border-radius:0 0 18px 18px;
                        padding:0.75rem 1.25rem 1rem;margin-bottom:0.75rem;
                        font-size:0.95rem;color:var(--text-primary);line-height:1.7;
                        box-shadow:var(--shadow-sm)">""",
                    unsafe_allow_html=True,
                )
                st.markdown(content)

                # Source badges
                if sources:
                    st.markdown(
                        "<div style='margin-top:0.75rem;padding-top:0.5rem;"
                        "border-top:1px solid var(--border-color)'>"
                        "<span style='font-size:0.8rem;color:var(--text-muted)'>📚 Sources: </span>"
                        + " &nbsp;".join(
                            f"<span style='font-size:0.78rem;color:var(--accent-blue);"
                            f"background:rgba(99,179,237,0.1);padding:0.1rem 0.5rem;"
                            f"border-radius:4px'>📄 {_escape_html(s)}</span>"
                            for s in sources[:3]
                        )
                        + "</div>",
                        unsafe_allow_html=True,
                    )

                ts_html = (
                    f"<div style='font-size:0.75rem;color:var(--text-muted);margin-top:0.3rem'>⏰ {timestamp}</div>"
                    if timestamp
                    else ""
                )
                if ts_html:
                    st.markdown(ts_html, unsafe_allow_html=True)

                st.markdown("</div>", unsafe_allow_html=True)



def search_result_card(rank: int, paper_name: str, score_pct: str, preview: str, full_text: str):
    """Render a premium semantic search result."""
    with st.expander(f"#{rank} · {paper_name}  ·  🎯 {score_pct}", expanded=(rank == 1)):
        st.markdown(f"""
        <div style="background:var(--bg-card);border:1px solid var(--border-color);
                    border-radius:10px;padding:1.25rem">
            <div style="display:flex;justify-content:space-between;margin-bottom:1rem;flex-wrap:wrap;gap:0.75rem">
                <span style="color:var(--accent-blue);font-weight:700;display:flex;align-items:center;gap:0.5rem">
                    📄 {_escape_html(paper_name)}
                </span>
                <span style="color:var(--accent-green);font-weight:700;display:flex;align-items:center;gap:0.5rem">
                    🎯 {_escape_html(score_pct)}
                </span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown(full_text)  # Safe markdown
        
        st.markdown("</div>", unsafe_allow_html=True)


def divider_with_label(label: str):
    """Horizontal divider with centered label."""
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:1.25rem;margin:1.75rem 0">
        <div style="flex:1;height:1px;background:var(--border-color)"></div>
        <div style="font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;
                    letter-spacing:0.6px;white-space:nowrap;font-weight:700">{label}</div>
        <div style="flex:1;height:1px;background:var(--border-color)"></div>
    </div>
    """, unsafe_allow_html=True)


def info_banner(message: str, type_: str = "info"):
    """Render a premium styled information banner."""
    colors = {
        "info":    ("rgba(99,179,237,0.12)",  "rgba(99,179,237,0.4)",   "var(--accent-blue-light)",  "ℹ️"),
        "success": ("rgba(104,211,145,0.12)", "rgba(104,211,145,0.4)", "var(--accent-green-light)", "✅"),
        "warning": ("rgba(246,173,85,0.12)",  "rgba(246,173,85,0.4)",   "var(--accent-orange)",      "⚠️"),
        "error":   ("rgba(252,129,129,0.12)", "rgba(252,129,129,0.4)",  "var(--accent-red)",         "❌"),
    }
    bg, border, color, icon = colors.get(type_, colors["info"])
    st.markdown(f"""
    <div style="background:{bg};border:1px solid {border};border-radius:10px;
                padding:1rem 1.25rem;color:{color};font-size:0.9rem;margin:0.75rem 0;
                font-weight:500;display:flex;align-items:flex-start;gap:0.75rem;line-height:1.6">
        <span style="font-size:1.1rem;flex-shrink:0;margin-top:0.1rem">{icon}</span>
        <span>{message}</span>
    </div>
    """, unsafe_allow_html=True)


def typing_animation():
    """Animated premium 'thinking' indicator."""
    st.markdown("""
    <div style="display:flex;align-items:center;gap:0.75rem;padding:0.75rem 0;color:var(--text-muted)">
        <div class="chat-ai-bubble" style="padding:0.8rem 1.25rem;width:fit-content">
            <span style="display:inline-flex;gap:6px;align-items:center">
                <span style="animation:bounce 1.2s infinite 0s;font-size:1.25rem">·</span>
                <span style="animation:bounce 1.2s infinite 0.2s;font-size:1.25rem">·</span>
                <span style="animation:bounce 1.2s infinite 0.4s;font-size:1.25rem">·</span>
            </span>
        </div>
    </div>
    <style>
    @keyframes bounce {
        0%, 60%, 100% { transform: translateY(0); opacity: 0.5; }
        30% { transform: translateY(-8px); opacity: 1; }
    }
    </style>
    """, unsafe_allow_html=True)


def logo_header():
    """Render the app logo/brand in the sidebar with premium styling."""
    st.markdown("""
    <div style="padding:1.25rem 0.75rem 1.75rem;border-bottom:1px solid var(--border-color);margin-bottom:1.5rem">
        <div style="display:flex;align-items:center;gap:0.9rem">
            <div style="
                width:44px;height:44px;
                background:linear-gradient(135deg,#667eea,#764ba2);
                border-radius:12px;
                display:flex;align-items:center;justify-content:center;
                font-size:1.4rem;flex-shrink:0;box-shadow:0 4px 15px rgba(102,126,234,0.3)
            ">🔬</div>
            <div>
                <div style="font-weight:800;font-size:0.95rem;color:var(--text-primary);
                            letter-spacing:-0.3px;line-height:1.1">Smart Paper</div>
                <div style="font-size:0.65rem;color:var(--text-muted);text-transform:uppercase;
                            letter-spacing:0.6px;font-weight:700;margin-top:0.15rem">Analyst</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
