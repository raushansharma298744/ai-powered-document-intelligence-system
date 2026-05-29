"""Premium minimalist peach & cream theme for DocuMind AI."""

APP_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Outfit', 'Roboto', 'Segoe UI', sans-serif;
    color: #2d2621;
}

#MainMenu, footer, header { visibility: hidden; }

/* Center app container */
.block-container {
    max-width: 800px !important;
    padding: 1.5rem !important;
    margin: 0 auto;
}

.stApp {
    background: linear-gradient(135deg, #fdf6f0 0%, #f5eae0 100%) !important;
}

section.main > div {
    padding: 0 !important;
}

/* Completely hide sidebar */
section[data-testid="stSidebar"] {
    display: none !important;
}
[data-testid="collapsedControl"] {
    display: none !important;
}

/* ========== PAGE 1: START ========== */
.page-start-inner {
    text-align: center;
    padding: 3rem 1.5rem;
    max-width: 480px;
    margin: 4vh auto 0;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-radius: 24px;
    box-shadow: 0 12px 40px rgba(218, 192, 172, 0.15);
}
.start-logo {
    font-size: 3.5rem;
    margin-bottom: 1rem;
    filter: drop-shadow(0 4px 10px rgba(224, 122, 95, 0.15));
}
.start-title {
    font-size: 1.80rem;
    margin: 0 0 0.5rem 0;
    color: #2d2621;
}
.start-subtitle {
    color: #7a6f68;
    font-size: 0.95rem;
    margin-bottom: 2rem;
}
.start-avatar {
    font-size: 5rem;
    margin: 1.5rem 0;
    filter: drop-shadow(0 8px 16px rgba(0,0,0,0.06));
}

/* Clean modern inputs */
[data-testid="stTextInput"] input {
    background: #ffffff !important;
    border: 1px solid #e6dcd5 !important;
    border-radius: 14px !important;
    padding: 0.9rem 1.25rem !important;
    font-size: 1.05rem !important;
    color: #2d2621 !important;
    text-align: center;
    box-shadow: 0 4px 12px rgba(224, 122, 95, 0.05) !important;
    transition: all 0.2s ease;
}
[data-testid="stTextInput"] input:focus {
    border-color: #e07a5f !important;
    box-shadow: 0 0 0 2px rgba(224, 122, 95, 0.15) !important;
}

/* Warm action buttons */
.btn-start button, .btn-continue button {
    background: #e07a5f !important;
    color: #ffffff !important;
    font-weight: 600 !important;
    font-size: 1.05rem !important;
    border: none !important;
    border-radius: 14px !important;
    padding: 0.85rem 2rem !important;
    width: 100% !important;
    margin-top: 1rem !important;
    box-shadow: 0 6px 18px rgba(224, 122, 95, 0.25) !important;
    transition: all 0.2s ease;
}
.btn-start button:hover, .btn-continue button:hover {
    background: #d06a4f !important;
    box-shadow: 0 8px 22px rgba(224, 122, 95, 0.35) !important;
}

/* ========== PAGE 2: UPLOAD ========== */
.page-upload-inner {
    text-align: center;
    padding: 2.5rem 1.5rem 1rem;
    max-width: 480px;
    margin: 4vh auto 0;
    background: rgba(255, 255, 255, 0.6);
    backdrop-filter: blur(12px);
    border: 1px solid rgba(255, 255, 255, 0.7);
    border-radius: 24px;
    box-shadow: 0 12px 40px rgba(218, 192, 172, 0.15);
}
.upload-heading {
    font-size: 1.6rem;
    margin: 0 0 0.5rem;
    color: #2d2621;
}
.upload-sub {
    color: #7a6f68;
    font-size: 0.95rem;
    margin-bottom: 1.5rem;
}
.upload-box-wrap {
    background: #ffffff;
    border-radius: 16px;
    padding: 1.5rem;
    border: 1px solid #eedcd0;
    box-shadow: 0 8px 24px rgba(224, 122, 95, 0.04);
}
.upload-continue-label {
    color: #7a6f68;
    font-size: 0.95rem;
    font-weight: 500;
    margin: 1.5rem 0 0.5rem;
}
[data-testid="stFileUploader"] {
    background: #fdfbf7 !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploader"] section {
    border: 2px dashed #dacfc7 !important;
    border-radius: 12px !important;
}

/* ========== CHAT LAYOUT ========== */
.online-dot {
    display: inline-block;
    width: 8px;
    height: 8px;
    background: #4caf50;
    border-radius: 50%;
    margin-left: 4px;
    vertical-align: middle;
    box-shadow: 0 0 6px #4caf50;
}

.nicci-app {
    width: 100%;
    background: transparent;
}

.nicci-header {
    background: rgba(255, 255, 255, 0.65);
    backdrop-filter: blur(14px);
    border: 1px solid rgba(255, 255, 255, 0.7);
    padding: 1rem 1.5rem;
    border-radius: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 4px 20px rgba(218, 192, 172, 0.08);
    margin-bottom: 1.5rem;
}
.nicci-header-left {
    display: flex;
    align-items: center;
    gap: 0.85rem;
}
.nicci-avatar-lg {
    width: 46px;
    height: 46px;
    background: linear-gradient(135deg, #fdf6f0, #f5eae0);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.5rem;
    border: 1px solid #eedcd0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}
.nicci-title {
    margin: 0;
    color: #2d2621;
    font-weight: 700;
    font-size: 1.15rem;
}
.nicci-sub {
    margin: 0;
    color: #7a6f68;
    font-size: 0.78rem;
}
.nicci-doc {
    margin: 0.15rem 0 0 !important;
    font-size: 0.75rem !important;
    color: #e07a5f !important;
    font-weight: 500;
}

/* Inline action buttons (replacing sidebar) */
.stDownloadButton > button,
[data-testid="stBaseButton-secondary"] {
    background: #ffffff !important;
    color: #7a6f68 !important;
    border: 1px solid #e6dcd5 !important;
    border-radius: 10px !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 0.4rem 0.65rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
}
.stDownloadButton > button:hover,
[data-testid="stBaseButton-secondary"]:hover {
    border-color: #e07a5f !important;
    color: #e07a5f !important;
    background: #fdf6f0 !important;
}

.nicci-chat-body {
    padding: 0 0 7rem 0;
    min-height: 50vh;
}

/* ========== CHAT BUBBLES ========== */
.nicci-row {
    display: flex;
    align-items: flex-end;
    margin-bottom: 1.25rem;
    gap: 0.75rem;
    width: 100%;
}
.nicci-row-user {
    justify-content: flex-end;
}
.nicci-row-bot {
    justify-content: flex-start;
}

/* User bubble: warm beige */
.nicci-bubble-user {
    background: #f7ede2;
    color: #2d2621;
    border: 1px solid #eddcd0;
    border-radius: 18px 18px 4px 18px;
    max-width: 75%;
    padding: 0.85rem 1.15rem;
    box-shadow: 0 4px 12px rgba(224, 122, 95, 0.05);
}

/* Bot bubble: pure white card */
.nicci-bubble-bot {
    background: #ffffff;
    color: #2d2621;
    border: 1px solid #eedcd0;
    border-radius: 18px 18px 18px 4px;
    max-width: 75%;
    padding: 0.95rem 1.25rem;
    box-shadow: 0 6px 18px rgba(218, 192, 172, 0.12);
}

.nicci-avatar-bot {
    width: 36px;
    height: 36px;
    background: linear-gradient(135deg, #fdf6f0, #f5eae0);
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1.1rem;
    flex-shrink: 0;
    border: 1px solid #eedcd0;
    margin-bottom: 2px;
}

.nicci-text {
    font-size: 0.95rem;
    line-height: 1.55;
    word-break: break-word;
}
.nicci-text strong {
    color: #e07a5f;
}

.nicci-time {
    font-size: 0.7rem;
    margin-top: 0.45rem;
    color: #a3978e;
    text-align: right;
}

.nicci-sources-hint {
    font-size: 0.75rem;
    margin-top: 0.45rem;
    color: #e07a5f;
    font-weight: 500;
}

/* Expander */
[data-testid="stExpander"] {
    background: #ffffff !important;
    border: 1px solid #eedcd0 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 12px rgba(0,0,0,0.02) !important;
    margin-top: 0.5rem !important;
}

/* ========== GREETING ========== */
.quick-start-head {
    text-align: center;
    margin: 2rem 0 0.5rem;
}
.quick-start-title {
    font-size: 2rem;
    font-weight: 600;
    color: #2d2621;
    margin: 0;
    line-height: 1.3;
}

/* ========== QUICK START CARDS ========== */
.quick-start-label {
    text-align: center;
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #a3978e;
    font-weight: 600;
    margin: 1.5rem 0 0.75rem;
}

.quick-cards-grid {
    margin: 0.5rem 0 2rem;
}

.quick-card-btn {
    margin-bottom: 0.75rem;
}
.quick-card-btn button {
    background: #ffffff !important;
    border: 1px solid #e6dcd5 !important;
    border-radius: 16px !important;
    padding: 1rem 1.15rem !important;
    text-align: left !important;
    width: 100% !important;
    box-shadow: 0 4px 14px rgba(218, 192, 172, 0.08) !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    font-weight: 600 !important;
    color: #2d2621 !important;
    font-size: 0.9rem !important;
}
.quick-card-btn button:hover {
    border-color: #e07a5f !important;
    box-shadow: 0 8px 24px rgba(224, 122, 95, 0.15) !important;
    transform: translateY(-2px) !important;
}

.quick-card-desc {
    font-size: 0.76rem !important;
    color: #7a6f68 !important;
    margin: -0.5rem 0 0.25rem 0 !important;
    padding: 0 0.25rem;
    line-height: 1.4 !important;
}

/* ========== FLOATING CHAT INPUT ========== */
[data-testid="stChatInput"] {
    position: fixed !important;
    bottom: 1.5rem !important;
    left: 50% !important;
    transform: translateX(-50%) !important;
    width: calc(100% - 3rem) !important;
    max-width: 720px !important;
    background: #ffffff !important;
    padding: 0.4rem 0.5rem !important;
    border: 1px solid #eedcd0 !important;
    border-radius: 28px !important;
    z-index: 1000 !important;
    box-shadow: 0 8px 32px rgba(218, 192, 172, 0.22) !important;
}

[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    padding: 0.6rem 1rem !important;
    font-size: 0.98rem !important;
    color: #2d2621 !important;
    resize: none !important;
}
[data-testid="stChatInput"] textarea:focus {
    box-shadow: none !important;
}

[data-testid="stChatInput"] button {
    background: #e07a5f !important;
    color: #ffffff !important;
    border-radius: 50% !important;
    width: 38px !important;
    height: 38px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 2px !important;
    box-shadow: 0 2px 8px rgba(224, 122, 95, 0.2) !important;
    transition: all 0.2s ease !important;
}
[data-testid="stChatInput"] button:hover {
    background: #d06a4f !important;
}

/* Back button */
.stButton > button[kind="secondary"] {
    background: transparent !important;
    color: #7a6f68 !important;
    border: 1px solid #dacfc7 !important;
    border-radius: 10px !important;
}
</style>
"""


def inject_styles(page_bg: str = "#fdf6f0", show_sidebar: bool = False) -> None:
    import streamlit as st
    st.markdown(APP_CSS, unsafe_allow_html=True)
