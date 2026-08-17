"""Wrapper único para o modelo de embeddings — mesmo modelo usado para documentos e perguntas."""
from dotenv import load_dotenv
from google.auth.api_key import Credentials as ApiKeyCredentials
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
        # Credenciais construídas explicitamente em vez de passar google_api_key=... —
        # em algumas plataformas (ex: Streamlit Community Cloud, hospedada em GCP), a lib
        # cai silenciosamente para Application Default Credentials em vez de usar a API key,
        # pegando um token de identidade da infraestrutura em vez da chave do Gemini.
        _embeddings = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL, credentials=ApiKeyCredentials(api_key), transport="rest",
        )
    return _embeddings
