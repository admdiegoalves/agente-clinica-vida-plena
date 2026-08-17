"""Wrapper único para o modelo de embeddings — mesmo modelo usado para documentos e perguntas."""
import os

from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings

from config import EMBEDDING_MODEL

load_dotenv()

_embeddings: OpenAIEmbeddings | None = None


def get_embeddings() -> OpenAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "OPENAI_API_KEY não definida. Copie .env.example para .env e preencha sua chave."
            )
        _embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL, api_key=api_key)
    return _embeddings
