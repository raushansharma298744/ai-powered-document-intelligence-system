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
            model="qwen/qwen3.8-27b",
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
                "You are a document intelligence assistant.\n\n"
                "Answer the user's question using ONLY the supplied document context. "
                "Do not use external knowledge when the requested information is not supported by the provided documents. "
                "If sufficient evidence does not exist in the retrieved context, respond that the uploaded documents do not provide enough information.\n"
                "Keep the answer concise but complete. Use citations supplied by the backend to support factual claims.\n\n"
                "IMPORTANT: You MUST respond in a valid JSON format with the following structure:\n"
                "{{\n"
                "  \"answer\": \"Your detailed answer here\",\n"
                "  \"sources\": [\n"
                "    {{\"doc\": \"filename\", \"page\": page_number_integer}}\n"
                "  ],\n"
                "  \"evaluation_metrics\": {{\n"
                "    \"confidence\": \"e.g., 91%\",\n"
                "    \"relevancy\": \"e.g., High / Medium / Low\",\n"
                "    \"clarity\": \"e.g., Clear\"\n"
                "  }}\n"
                "}}\n"
                "Do not include any other text outside the JSON block.\n\n"
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
