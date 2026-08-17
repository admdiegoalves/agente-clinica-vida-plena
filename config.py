"""Configuração central do agente: paths, modelos e parâmetros do pipeline RAG."""
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
RAW_DOCS_DIR = DATA_DIR / "raw"
CONTACTS_FILE = DATA_DIR / "contacts" / "contatos_departamentos.json"
CHROMA_DB_DIR = DATA_DIR / "chroma_db"
CHROMA_COLLECTION_NAME = "clinica_documentos"

LOGS_DIR = BASE_DIR / "logs"
EXECUTIONS_LOG_FILE = LOGS_DIR / "execucoes.jsonl"

# Vocabulário controlado de categorias (nome da subpasta em data/raw == valor do metadado "category")
CATEGORIES = [
    "rh",
    "financeiro",
    "operacional",
    "legal_compliance",
    "qualidade_biosseguranca",
    "comunicacao_interna",
    "estrategico",
]

CATEGORY_LABELS = {
    "rh": "Recursos Humanos",
    "financeiro": "Financeiro",
    "operacional": "Operacional",
    "legal_compliance": "Legal e Compliance",
    "qualidade_biosseguranca": "Qualidade e Biossegurança",
    "comunicacao_interna": "Comunicação Interna",
    "estrategico": "Estratégico",
}

# Modelos Google Gemini (via langchain-google-genai) — gerar chave gratuita em
# https://aistudio.google.com/apikey
EMBEDDING_MODEL = "models/gemini-embedding-001"
CHAT_MODEL = "gemini-3.6-flash"
CHAT_TEMPERATURE = 0

# Chunking
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

# Retrieval
RETRIEVAL_TOP_K = 6

# Calibrado empiricamente (scripts/smoke_test_query.py): com o modelo de embedding do Gemini, o
# score de cosseno roda alto mesmo para trechos irrelevantes (~0.70-0.74 no pior caso). Perguntas
# dentro do domínio tiveram melhor match >= 0.82; perguntas fora do domínio ficaram <= 0.74.
SCORE_THRESHOLD = 0.78

# OCR (best-effort, desligado por padrão — ver README para detalhes)
ENABLE_OCR_FALLBACK = False
