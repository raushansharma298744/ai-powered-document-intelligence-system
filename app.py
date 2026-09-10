"""
DocuMind AI — Premium minimalist warm-theme chat UI
Page 1: Name → Page 2: Upload → Page 3: Chat (Axiom-style design)
"""

import shutil
from datetime import datetime

import streamlit as st
from dotenv import load_dotenv
import json

from rag import (
    build_rag_chain,
    create_indexes,
    load_pdfs,
    run_rag,
    split_into_chunks,
)
from rag.config import VECTORSTORE_DIR
from rag.errors import format_user_error
from ui import (
    SUGGESTED_PROMPTS,
    build_transcript,
    chunks_from_result,
    clear_chat_keep_doc,
    inject_styles,
    render_assistant_bubble,
    render_chat_shell_close,
    render_chat_shell_open,
    render_continue_label,
    render_greeting,
    render_quick_cards,
    render_start_page_header,
    render_upload_page_header,
    render_user_bubble,
)

load_dotenv()

# Check for presence of an API key early so we can show a helpful UI message
from rag.config import get_google_api_key

try:
    _ = get_google_api_key()
    HAS_API_KEY = True
except Exception:
    HAS_API_KEY = False

# Quick Start cards: (icon, title, description, query_text)
QUICK_START = [
    ("📋", "Short summary", "Get a concise summary of your document.", "Give me a short summary of this document."),
    ("🔑", "Key points", "Extract the most important takeaways.", "What are the key points in this document?"),
    ("💡", "Simple explanation", "Understand complex ideas easily.", "Explain the main ideas in simple words."),
    ("📌", "Important details", "Identify critical facts and data.", "List the most important details I should know."),
]

st.set_page_config(
    page_title="DocuMind AI",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def init_session():
    defaults = {
        "page": 0,
        "user_name": "",
        "doc_name": "",
        "chunk_count": 0,
        "chat_messages": [],
        "chat_history": [],
        "vectorstore": None,
        "rag_chain": None,
        "pending_question": None,
        "suggest_hint": SUGGESTED_PROMPTS[0][2]
        if SUGGESTED_PROMPTS and len(SUGGESTED_PROMPTS[0]) > 2
        else "Give me a short summary of this document.",
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def reset_all():
    if VECTORSTORE_DIR.parent.exists():
        shutil.rmtree(VECTORSTORE_DIR.parent, ignore_errors=True)
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()


def process_document(uploaded_file):
    docs = load_pdfs([uploaded_file])
    chunks = split_into_chunks(docs)
    vectorstore, bm25store = create_indexes(chunks)
    st.session_state.vectorstore = vectorstore
    st.session_state.bm25store = bm25store
    st.session_state.rag_chain = build_rag_chain(st.session_state.vectorstore)
    st.session_state.doc_name = uploaded_file.name
    st.session_state.chunk_count = len(chunks)


def set_greeting():
    name = st.session_state.user_name
    doc = st.session_state.doc_name
    st.session_state.chat_messages = [
        {
            "role": "assistant",
            "content": (
                f"Hello {name}!\n\n"
                f"I have read your document (**{doc}**). "
                "Ask me anything — summaries, facts, or explanations."
            ),
            "sources": None,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
    ]
    st.session_state.chat_history = []
    st.session_state.suggest_hint = "Give me a short summary of this document."


def show_chat_messages():
    for msg in st.session_state.chat_messages:
        ts = msg.get("time", "")
        if msg["role"] == "user":
            render_user_bubble(msg["content"], ts)
        else:
            render_assistant_bubble(msg["content"], msg.get("sources"), ts)


def add_chat(role: str, content: str, sources=None):
    st.session_state.chat_messages.append(
        {
            "role": role,
            "content": content,
            "sources": sources,
            "time": datetime.now().strftime("%H:%M:%S"),
        }
    )


def answer_question(question: str):
    history = st.session_state.chat_history
    result = run_rag(st.session_state.rag_chain, question, history)
    raw = result.get("answer", "Sorry, I could not find an answer in your document.")
    # Try to parse structured JSON output from the LLM (if present)
    content = None
    sources = None
    try:
        parsed = json.loads(raw)
        parts = []
        if parsed.get("summary"):
            parts.append(f"Summary:\n{parsed['summary']}")
        if parsed.get("bullets"):
            bullets = "\n".join(f"- {b}" for b in parsed.get("bullets", []))
            parts.append(f"Key points:\n{bullets}")
        if parsed.get("answer"):
            parts.append(f"Answer:\n{parsed['answer']}")
        if parsed.get("follow_up_questions"):
            fu = "\n".join(f"- {q}" for q in parsed.get("follow_up_questions", []))
            parts.append(f"Suggested follow-up questions:\n{fu}")
        content = "\n\n".join(parts) if parts else parsed.get("answer", raw)
        sources = parsed.get("sources") or chunks_from_result(result.get("context", []))
    except Exception:
        # Not JSON — fall back to the raw answer string
        content = raw
        sources = chunks_from_result(result.get("context", []))

    add_chat("assistant", content, sources=sources)
    st.session_state.chat_history = history + [
        {"role": "user", "content": question},
        {"role": "assistant", "content": content},
    ]
    st.session_state.suggest_hint = question


def handle_user_message(question: str):
    add_chat("user", question)
    try:
        answer_question(question)
    except Exception as e:
        add_chat("assistant", f"Something went wrong: {format_user_error(e)}", sources=None)


init_session()
page = st.session_state.page
inject_styles()

# ===================== PAGE 1: NAME =====================
if page == 0:
    render_start_page_header()
    name = st.text_input("name", placeholder="Your name", label_visibility="collapsed")
    st.markdown('<div class="btn-start">', unsafe_allow_html=True)
    if st.button("Start", use_container_width=True):
        cleaned = (name or "").strip()
        if not cleaned:
            st.warning("Please enter your name.")
        else:
            st.session_state.user_name = cleaned
            st.session_state.page = 1
            st.rerun()
    st.markdown("</div>", unsafe_allow_html=True)

# ===================== PAGE 2: UPLOAD =====================
elif page == 1:
    render_upload_page_header(st.session_state.user_name)
    st.markdown('<div class="upload-box-wrap">', unsafe_allow_html=True)
    uploaded = st.file_uploader("pdf", type=["pdf"], label_visibility="collapsed")
    if uploaded:
        st.caption(f"📄 {uploaded.name}")
    st.markdown("</div>", unsafe_allow_html=True)
    render_continue_label()
    st.markdown('<div class="btn-continue">', unsafe_allow_html=True)
    if st.button("Continue", use_container_width=True):
        if not uploaded:
            st.warning("Please upload a PDF first.")
        else:
            if not HAS_API_KEY:
                st.error(
                    "Invalid or missing API key. Check GROK_API_KEY or GOOGLE_API_KEY in your .env file."
                )
            else:
                with st.spinner("Loading document..."):
                    try:
                        process_document(uploaded)
                        set_greeting()
                        st.session_state.page = 2
                        st.rerun()
                    except Exception as e:
                        # Show both a user-friendly hint and the raw exception for debugging
                        st.error(
                            "Document processing failed. See details below. Common causes: invalid API key, missing sentence-transformers, or network issues."
                        )
                        st.exception(e)
                        st.info(
                            "Try: `pip install -r requirements.txt`, verify `.env` keys, then restart the app."
                        )
    st.markdown("</div>", unsafe_allow_html=True)
    if st.button("← Back"):
        st.session_state.page = 0
        st.rerun()

# ===================== PAGE 3: CHAT =====================
elif page == 2:

    # --- Header bar ---
    render_chat_shell_open(st.session_state.doc_name)

    # --- Inline action buttons (replaces sidebar tools) ---
    act_cols = st.columns([1, 1, 1, 4])
    with act_cols[0]:
        transcript = build_transcript(
            st.session_state.chat_messages,
            st.session_state.user_name,
            st.session_state.doc_name,
        )
        st.download_button(
            label="📥 Export",
            data=transcript,
            file_name=f"chat_{st.session_state.user_name.replace(' ', '_')}.txt",
            mime="text/plain",
            key="dl_chat",
        )
    with act_cols[1]:
        if st.button("🗑️ Clear", key="btn_clear_inline"):
            clear_chat_keep_doc(st.session_state.user_name, st.session_state.doc_name)
            st.rerun()
    with act_cols[2]:
        if st.button("↺ Reset", key="btn_reset_inline"):
            reset_all()

    # --- Big greeting if only the initial message is shown ---
    if len(st.session_state.chat_messages) <= 1:
        render_greeting(st.session_state.user_name)

    # --- Chat messages ---
    show_chat_messages()

    # --- Quick Start cards (show only at the beginning) ---
    card_q = None
    if len(st.session_state.chat_messages) <= 1:
        card_q = render_quick_cards(QUICK_START)

    render_chat_shell_close()

    # --- Handle card clicks ---
    if card_q:
        st.session_state.pending_question = card_q

    if st.session_state.pending_question:
        pq = st.session_state.pending_question
        st.session_state.pending_question = None
        handle_user_message(pq)
        st.rerun()

    # --- Floating chat input ---
    if question := st.chat_input("How can I help you today?"):
        handle_user_message(question)
        st.rerun()
