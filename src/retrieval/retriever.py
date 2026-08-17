"""Camada de recuperação: busca semântica no Chroma, filtro opcional por categoria e threshold."""
from config import RETRIEVAL_TOP_K, SCORE_THRESHOLD
from src.indexing.vector_store import get_vector_store


def retrieve(query: str, top_k: int = RETRIEVAL_TOP_K, category: str | None = None,
             score_threshold: float = SCORE_THRESHOLD) -> dict:
    """Retorna {"has_context": bool, "chunks": [{"text", **metadados, "score"}, ...]}.

    `has_context=False` quando nenhum chunk recuperado atinge o score_threshold — usado pela
    camada de geração para acionar o fallback sem chamar o LLM.
    """
    store = get_vector_store()
    where = {"category": category} if category else None

    results = store.similarity_search_with_relevance_scores(query, k=top_k, filter=where)

    chunks = []
    for doc, score in results:
        if score < score_threshold:
            continue
        chunks.append({"text": doc.page_content, **doc.metadata, "score": round(score, 4)})

    return {"has_context": len(chunks) > 0, "chunks": chunks}
