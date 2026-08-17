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

# Modelos OpenAI
EMBEDDING_MODEL = "text-embedding-3-small"
CHAT_MODEL = "gpt-4o-mini"
CHAT_TEMPERATURE = 0

# Chunking
CHUNK_SIZE = 900
CHUNK_OVERLAP = 150

# Retrieval
RETRIEVAL_TOP_K = 6
SCORE_THRESHOLD = 0.35  # calibrado empiricamente na fase de retrieval (ver scripts/smoke_test_query.py)

# OCR (best-effort, desligado por padrão — ver README para detalhes)
ENABLE_OCR_FALLBACK = False
