"""User-friendly messages for Google API / RAG failures."""


def format_user_error(exc: BaseException) -> str:
    msg = str(exc)
    lower = msg.lower()
    if "quota" in lower or "resource_exhausted" in lower or "429" in msg:
        return (
            "API daily limit reached (Groq or Google). "
            "Wait a few minutes, try again tomorrow, or use a different API key in `.env`. "
            "(Groq free tier has very strict token/minute limits)."
        )
    if "unexpected model name format" in lower:
        return (
            "Invalid embedding model name. Use `models/gemini-embedding-001` in `rag/config.py`."
        )
    if "api key" in lower or "api_key" in lower:
        return "Invalid or missing API key. Check `GROK_API_KEY` or `GOOGLE_API_KEY` in your `.env` file."
    return msg
