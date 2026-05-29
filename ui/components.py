"""Premium minimalist warm-theme chat UI components for DocuMind AI."""

import html
import re
from datetime import datetime
from typing import List, Optional

import streamlit as st

APP_NAME = "DocuMind AI"
APP_SHORT = "DocuMind"
APP_TAGLINE = "Your Document Assistant"
CHAT_TAGLINE = "Document Assistant"


def _format_bot_text(text: str) -> str:
    safe = html.escape(text)
    safe = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", safe)
    return safe.replace("\n", "<br>")


def _now_time() -> str:
    return datetime.now().strftime("%H:%M:%S")


# ---------- PAGE 1: START ----------
def render_start_page_header() -> None:
    st.markdown(
        f'<div class="page-start-inner">'
        f'<div class="start-logo">📄</div>'
        f'<h1 class="start-title">{APP_NAME}</h1>'
        f'<p class="start-subtitle">{APP_TAGLINE}</p>'
        f'<div class="start-avatar">👩‍💼</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------- PAGE 2: UPLOAD ----------
def render_upload_page_header(user_name: str) -> None:
    safe = html.escape(user_name)
    st.markdown(
        f'<div class="page-upload-inner">'
        f'<h2 class="upload-heading">Upload Document</h2>'
        f'<p class="upload-sub">Hi <strong>{safe}</strong>, please upload your PDF file</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_continue_label() -> None:
    st.markdown('<p class="upload-continue-label">Continue</p>', unsafe_allow_html=True)


# ---------- CHAT HEADER ----------
def render_chat_shell_open(doc_name: str = "") -> None:
    safe_doc = html.escape(doc_name) if doc_name else ""
    doc_html = f'<p class="nicci-doc">📄 {safe_doc}</p>' if doc_name else ""
    st.markdown(
        f'<div class="nicci-app">'
        f'<div class="nicci-header">'
        f'<div class="nicci-header-left">'
        f'<div class="nicci-avatar-lg">📄</div>'
        f'<div>'
        f'<p class="nicci-title">{APP_SHORT} <span class="online-dot"></span></p>'
        f'<p class="nicci-sub">{CHAT_TAGLINE}</p>'
        f'{doc_html}'
        f'</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_chat_subtoolbar() -> None:
    """No-op — toolbar hidden in the new design."""
    pass


def render_chat_shell_close() -> None:
    st.markdown("</div>", unsafe_allow_html=True)


# ---------- CHAT GREETING (Axiom-style) ----------
def render_greeting(user_name: str) -> None:
    """Big centered greeting matching the reference image."""
    safe = html.escape(user_name)
    # Determine time of day
    hour = datetime.now().hour
    if hour < 12:
        tod = "Good morning"
    elif hour < 17:
        tod = "Good afternoon"
    else:
        tod = "Good evening"
    st.markdown(
        f'<div class="quick-start-head">'
        f'<p class="quick-start-title">{tod}, {safe}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ---------- QUICK START CARDS (2x2 grid) ----------
def render_quick_cards(prompts: List[tuple]) -> Optional[str]:
    """
    Render a 2×2 grid of Quick Start cards.
    prompts: list of (icon, title, description, query_text)
    Returns the query text if a card was clicked, else None.
    """
    clicked_query: Optional[str] = None

    st.markdown('<p class="quick-start-label">QUICK START</p>', unsafe_allow_html=True)
    st.markdown('<div class="quick-cards-grid">', unsafe_allow_html=True)

    # Use 2 columns
    cols = st.columns(2)
    for i, (icon, title, desc, query) in enumerate(prompts):
        with cols[i % 2]:
            st.markdown('<div class="quick-card-btn">', unsafe_allow_html=True)
            if st.button(f"{icon}  {title}", key=f"qc_{i}", use_container_width=True):
                clicked_query = query
            st.markdown(
                f'<p class="quick-card-desc">{html.escape(desc)}</p>',
                unsafe_allow_html=True,
            )
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)
    return clicked_query


# ---------- CHAT BUBBLES ----------
def render_user_bubble(content: str, timestamp: str = "") -> None:
    safe = html.escape(content).replace("\n", "<br>")
    ts = html.escape(timestamp or _now_time())
    st.markdown(
        f'<div class="nicci-row nicci-row-user">'
        f'<div class="nicci-bubble nicci-bubble-user">'
        f'<div class="nicci-text">{safe}</div>'
        f'<div class="nicci-time">{ts}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def render_assistant_bubble(
    content: str,
    sources: Optional[list] = None,
    timestamp: str = "",
) -> None:
    body = _format_bot_text(content)
    ts = html.escape(timestamp or _now_time())
    sources_html = ""
    if sources:
        sources_html = (
            f'<div class="nicci-sources-hint">📎 {len(sources)} source segment(s) used</div>'
        )

    st.markdown(
        f'<div class="nicci-row nicci-row-bot">'
        f'<div class="nicci-avatar-bot">📄</div>'
        f'<div class="nicci-bubble nicci-bubble-bot">'
        f'<div class="nicci-text">{body}</div>'
        f'{sources_html}'
        f'<div class="nicci-time">{ts}</div>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )
    if sources:
        with st.expander(f"📎 View sources ({len(sources)})", expanded=False):
            for s in sources:
                st.markdown(f"**Segment {s['index']}** · `{s['source']}`")
                st.caption(s["preview"])


# ---------- OLD API STUBS (keep for backward compat) ----------
def render_quick_pills(pill_actions: List[tuple]) -> Optional[str]:
    """Deprecated — no-op. Use render_quick_cards instead."""
    return None


def render_suggested_query_bar(hint: str) -> None:
    """Deprecated — no-op."""
    pass


# Legacy stubs
def render_chat_header(doc_name: str = "") -> None:
    render_chat_shell_open(doc_name)


def render_chat_toolbar() -> None:
    pass


def render_chat_body_close() -> None:
    render_chat_shell_close()
