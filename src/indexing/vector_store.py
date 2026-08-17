"""Conexão com o ChromaDB persistente local e upsert de chunks indexados."""
from langchain_chroma import Chroma

from config import CHROMA_COLLECTION_NAME, CHROMA_DB_DIR
from src.indexing.embeddings import get_embeddings

_vector_store: Chroma | None = None


def get_vector_store() -> Chroma:
    global _vector_store
    if _vector_store is None:
        _vector_store = Chroma(
            collection_name=CHROMA_COLLECTION_NAME,
            embedding_function=get_embeddings(),
            persist_directory=str(CHROMA_DB_DIR),
            # Default do Chroma é "l2" (distância). Usamos cosseno para o score de similaridade
            # (0-1, maior=melhor) ter interpretação direta no threshold de retrieval.
            collection_metadata={"hnsw:space": "cosine"},
        )
    return _vector_store


def upsert_chunks(chunks: list[dict]) -> int:
    """Insere/atualiza chunks no Chroma. chunk_id determinístico faz upsert em vez de duplicar."""
    if not chunks:
        return 0

    store = get_vector_store()
    ids = [c["chunk_id"] for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [{k: v for k, v in c.items() if k not in ("text", "chunk_id")} for c in chunks]

    store.add_texts(texts=texts, metadatas=metadatas, ids=ids)
    return len(chunks)


def collection_count() -> int:
    return get_vector_store()._collection.count()
