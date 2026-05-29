"""Chat page features — sidebar, sources, export."""

import html
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import streamlit as st

# (icon, button label, actual question sent to RAG)
SUGGESTED_PROMPTS: List[Tuple[str, str, str]] = [
    ("📋", "Short summary", "Give me a short summary of this document."),
    ("🔑", "Key points", "What are the key points in this document?"),
    ("💡", "Simple explanation", "Explain the main ideas in simple words."),
    ("📌", "Important details", "List the most important details I should know."),
]


def chunks_from_result(context_docs, limit: int = 3) -> List[Dict[str, Any]]:
    out = []
    for i, doc in enumerate(context_docs[:limit], start=1):
        text = doc.page_content.strip()
        out.append(
            {
                "index": i,
                "source": doc.metadata.get("source", "Document"),
                "preview": text[:400] + ("…" if len(text) > 400 else ""),
            }
        )
    return out


def _sidebar_session_card(user_name: str, doc_name: str, chunk_count: int) -> None:
    safe_user = html.escape(user_name)
    safe_doc = html.escape(doc_name)
    st.markdown(
        f"""
        <div class="sb-card sb-session">
            <p class="sb-label">Active session</p>
            <p class="sb-row"><span>👤</span> {safe_user}</p>
            <p class="sb-row sb-doc"><span>📄</span> {safe_doc}</p>
            <p class="sb-chunks"><span>{chunk_count or 0}</span> text segments indexed</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_chat_sidebar(
    user_name: str,
    doc_name: str,
    chunk_count: int,
    messages: List[dict],
    on_clear,
    on_reset,
) -> Optional[str]:
    """
    Full enhanced sidebar. Returns question text if a suggested prompt was clicked.
    """
    clicked_query: Optional[str] = None

    with st.sidebar:
        st.markdown(
            """
            <div class="sb-brand">
                <span class="sb-brand-icon">📄</span>
                <div>
                    <p class="sb-brand-title">DocuMind</p>
                    <p class="sb-brand-sub">Document Assistant</p>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        _sidebar_session_card(user_name, doc_name, chunk_count)

        st.markdown(
            """
            <div class="sb-section-head">
                <p class="sb-section-title">Suggested prompts</p>
                <p class="sb-section-hint">Works with any uploaded PDF — tap to ask</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        for icon, label, query in SUGGESTED_PROMPTS:
            if st.button(
                f"{icon}  {label}",
                key=f"prompt_{label}",
                use_container_width=True,
            ):
                clicked_query = query

        st.markdown('<div class="sb-divider"></div>', unsafe_allow_html=True)

        st.markdown('<p class="sb-actions-title">Tools</p>', unsafe_allow_html=True)

        transcript = build_transcript(messages, user_name, doc_name)
        st.download_button(
            label="📥  Export conversation",
            data=transcript,
            file_name=f"chat_{user_name.replace(' ', '_')}.txt",
            mime="text/plain",
            use_container_width=True,
            key="dl_chat",
        )

        if st.button("🗑️  Clear messages", use_container_width=True, key="btn_clear"):
            on_clear()

        if st.button("↺  New session", use_container_width=True, key="btn_reset"):
            on_reset()

    return clicked_query


def build_transcript(messages: List[dict], user_name: str, doc_name: str) -> str:
    lines = [
        "DocuMind AI — Chat Transcript",
        f"User: {user_name}",
        f"Document: {doc_name}",
        f"Exported: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "-" * 40,
        "",
    ]
    for msg in messages:
        role = "You" if msg["role"] == "user" else "DocuMind"
        lines.append(f"{role}:")
        lines.append(msg["content"])
        if msg.get("sources"):
            lines.append("[Sources used]")
            for s in msg["sources"]:
                lines.append(f"  - Segment {s['index']}: {s['source']}")
        lines.append("")
    return "\n".join(lines)


def clear_chat_keep_doc(user_name: str, doc_name: str) -> None:
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                f"Hello {user_name}!\n\n"
                f"Messages cleared. **{doc_name}** is still loaded.\n\n"
                "Ask me anything about your file."
            ),
            "sources": None,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
    ]
    st.session_state.chat_history = []


def render_copy_answer_button(text: str, key: str = "copy_answer") -> None:
    if hasattr(st, "copy_button"):
        st.copy_button("📋 Copy answer", text, use_container_width=True, key=key)
    else:
        st.download_button(
            label="📋 Save answer",
            data=text,
            file_name="last_answer.txt",
            mime="text/plain",
            use_container_width=True,
            key=key,
        )
