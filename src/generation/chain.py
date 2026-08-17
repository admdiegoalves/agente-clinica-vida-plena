"""Orquestração de geração: decide entre chamar o LLM (chain LCEL) ou retornar o fallback.

A ramificação "tem contexto suficiente?" fica fora da chain LCEL, em uma função Python simples —
mais fácil de logar e depurar do que embutir a lógica de fallback dentro de um RunnableBranch.
"""
import time

from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI

from config import CHAT_MODEL, CHAT_TEMPERATURE, RETRIEVAL_TOP_K, SCORE_THRESHOLD
from src.contacts.contact_lookup import format_contact_line
from src.generation.prompts import format_context, get_prompt
from src.retrieval.retriever import retrieve

_model = None


def _get_model() -> ChatGoogleGenerativeAI:
    global _model
    if _model is None:
        _model = ChatGoogleGenerativeAI(model=CHAT_MODEL, temperature=CHAT_TEMPERATURE)
    return _model


def _build_chain():
    return get_prompt() | _get_model() | StrOutputParser()


def _fallback_answer(category: str | None) -> str:
    contact_line = format_contact_line(category)
    return (
        "Não encontrei essa informação nos documentos disponíveis na minha base de conhecimento. "
        "Recomendo confirmar diretamente com a área responsável:\n\n"
        f"{contact_line}"
    )


def answer_question(question: str, category: str | None = None,
                     top_k: int = RETRIEVAL_TOP_K, score_threshold: float = SCORE_THRESHOLD) -> dict:
    """Retorna {"answer", "sources", "has_sufficient_context", "response_time_ms"}."""
    start = time.perf_counter()

    retrieval = retrieve(question, top_k=top_k, category=category, score_threshold=score_threshold)

    if not retrieval["has_context"]:
        answer = _fallback_answer(category)
        elapsed_ms = int((time.perf_counter() - start) * 1000)
        return {
            "answer": answer,
            "sources": [],
            "has_sufficient_context": False,
            "response_time_ms": elapsed_ms,
        }

    chunks = retrieval["chunks"]
    context = format_context(chunks)
    chain = _build_chain()
    answer = chain.invoke({"context": context, "question": question})

    elapsed_ms = int((time.perf_counter() - start) * 1000)
    return {
        "answer": answer,
        "sources": chunks,
        "has_sufficient_context": True,
        "response_time_ms": elapsed_ms,
    }
