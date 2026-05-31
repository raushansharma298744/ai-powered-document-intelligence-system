"""
RAG chain (Retrieval + Augmented Generation).

LangChain pattern:
  1. History-aware retriever — rewrites follow-up questions using chat history
  2. Retrieval chain — fetches relevant chunks from FAISS
  3. Stuff-documents chain — sends context + question to Google Gemini
"""

from typing import Any, Dict, List

from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from rag.config import LLM_MODEL, get_google_api_key, is_groq_key
from rag.vectorstore import get_retriever


def _get_llm() -> BaseChatModel:
    key = get_google_api_key()
    if is_groq_key():
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,
            groq_api_key=key,
        )
    return ChatGoogleGenerativeAI(
        model=LLM_MODEL,
        temperature=0.2,
        google_api_key=key,
    )



def build_messages_history(ui_messages: List[dict]) -> List[BaseMessage]:
    """Convert Streamlit chat history to LangChain message objects."""
    history: List[BaseMessage] = []
    for msg in ui_messages:
        if msg["role"] == "user":
            history.append(HumanMessage(content=msg["content"]))
        elif msg["role"] == "assistant":
            history.append(AIMessage(content=msg["content"]))
    return history


def build_rag_chain(vectorstore: FAISS):
    """
    Full LangChain RAG pipeline:
      Retriever (FAISS) → Context + Gemini → Grounded answer
    """
    llm = _get_llm()
    retriever = get_retriever(vectorstore)

    # Step A: Make retrieval aware of conversation (e.g. "What about its pricing?")
    contextualize_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "Given the chat history and the latest user question, "
                "rewrite it as a standalone question for document search. "
                "If it is already standalone, return it unchanged.",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        llm, retriever, contextualize_prompt
    )

    # Step B: Answer only from retrieved context (reduces hallucination)
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You are a RAG assistant. Answer ONLY using the retrieved context below. "
                "If the answer is not in the context, say: 'I could not find that in the uploaded documents.' "
                "Produce the response in STRICT JSON only — nothing else. The JSON must follow this schema:\n"
                "{{\n"
                "  \"answer\": string,            # short direct answer to the user's question\n"
                "  \"summary\": string|null,     # one-paragraph summary of relevant context (optional)\n"
                "  \"bullets\": [string],        # key points from the document (can be empty)\n"
                "  \"follow_up_questions\": [string], # useful follow-up questions (optional)\n"
                "  \"sources\": [                # optional list of used source segments\n"
                "    {{\"index\": int, \"source\": string, \"preview\": string}}\n"
                "  ]\n"
                "}}\n"
                "Be concise and factual. Never hallucinate facts outside the provided context.\n\n"
                "Context:\n{context}",
            ),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)

    return create_retrieval_chain(history_aware_retriever, question_answer_chain)


def run_rag(
    rag_chain,
    question: str,
    chat_history: List[dict],
) -> Dict[str, Any]:
    """Invoke the LangChain RAG chain with user input and prior messages."""
    return rag_chain.invoke(
        {
            "input": question,
            "chat_history": build_messages_history(chat_history),
        }
    )
