"""Wrapper único para o modelo de embeddings — mesmo modelo usado para documentos e perguntas."""
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from config import EMBEDDING_MODEL
from src.config_helpers import get_google_api_key

load_dotenv()

_embeddings: GoogleGenerativeAIEmbeddings | None = None


def get_embeddings() -> GoogleGenerativeAIEmbeddings:
    global _embeddings
    if _embeddings is None:
        api_key = get_google_api_key()
        if not api_key:
            raise RuntimeError(
                "GOOGLE_API_KEY não definida. Copie .env.example para .env e preencha sua chave "
                "(gere gratuitamente em https://aistudio.google.com/apikey)."
            )
        _embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL, google_api_key=api_key)
    return _embeddings
