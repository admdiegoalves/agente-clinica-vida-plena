"""Interface Streamlit do agente de conhecimento interno da Clínica Vida Plena.

Só orquestra a UI — toda a lógica de RAG vive em src/. Rodar com:
    streamlit run app.py
"""
import base64
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from config import CATEGORIES, CATEGORY_LABELS, RAW_DOCS_DIR
from src.generation.chain import answer_question
from src.ingestion.loaders import load_document
from src.indexing.vector_store import collection_count, upsert_chunks
from src.logging_utils.jsonl_logger import log_execution, log_feedback
from src.processing.chunking import build_chunks

load_dotenv()

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
FAVICON_PATH = ASSETS_DIR / "favicon.png"
LOGO_PATH = ASSETS_DIR / "logo.png"
ROBOT_IMAGE_PATH = ASSETS_DIR / "imagem_robo.png"

st.set_page_config(
    page_title="Assistente Clínica Vida Plena",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🩺",
    layout="centered",
)


@st.cache_resource(show_spinner="Preparando a base de conhecimento pela primeira vez...")
def ensure_indexed():
    """Indexa data/raw/ no Chroma se a collection estiver vazia — cobre o primeiro boot em
    ambientes onde data/chroma_db/ não é versionado (ex: Streamlit Community Cloud)."""
    if collection_count() > 0:
        return
    for file_path in sorted(RAW_DOCS_DIR.rglob("*.*")):
        units = load_document(file_path)
        chunks = build_chunks(file_path, units)
        upsert_chunks(chunks)


ensure_indexed()

if ROBOT_IMAGE_PATH.exists():
    robot_b64 = base64.b64encode(ROBOT_IMAGE_PATH.read_bytes()).decode()
    st.markdown(
        f'<div style="text-align: center;">'
        f'<img src="data:image/png;base64,{robot_b64}" width="140" />'
        f"</div>",
        unsafe_allow_html=True,
    )

st.markdown(
    """
    <style>
    #MainMenu, [data-testid="stMainMenu"], [data-testid="stToolbar"], [data-testid="stDecoration"] {
        visibility: hidden;
        display: none;
    }
    .app-title {
        text-align: center;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        font-size: 2rem;
    }
    @media (max-width: 480px) {
        .app-title {
            white-space: normal;
            font-size: 1.5rem;
            line-height: 1.25;
        }
    }
    </style>
    <h1 class="app-title">Assistente de Conhecimento Interno</h1>
    """,
    unsafe_allow_html=True,
)
st.caption(
    "⚠️ Você está conversando com um **agente de IA**, não com uma pessoa. As respostas são "
    "geradas a partir dos documentos internos oficiais da clínica; em casos sensíveis, sempre "
    "confirme com a área responsável indicada nas fontes.",
)

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH), width=140)
    st.header("Filtros")
    category_options = ["Todas as categorias"] + [CATEGORY_LABELS[c] for c in CATEGORIES]
    label_to_slug = {CATEGORY_LABELS[c]: c for c in CATEGORIES}
    selected_label = st.selectbox("Categoria de documentos", category_options)
    selected_category = label_to_slug.get(selected_label)  # None quando "Todas as categorias"

    st.divider()
    if st.button("🗑️ Limpar conversa"):
        st.session_state.messages = []
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "logged_feedback" not in st.session_state:
    st.session_state.logged_feedback = {}

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

        if msg["role"] == "assistant" and msg.get("sources"):
            with st.expander("📄 Fontes consultadas"):
                for s in msg["sources"]:
                    category_label = CATEGORY_LABELS.get(s.get("category"), s.get("category", ""))
                    st.markdown(
                        f"- **{s['source_file']}** ({category_label}) — {s['location']} "
                        f"— relevância {s['score']:.2f}"
                    )

        if msg["role"] == "assistant" and msg.get("execution_id"):
            execution_id = msg["execution_id"]
            selected = st.feedback("thumbs", key=f"fb_{execution_id}")
            if selected is not None and st.session_state.logged_feedback.get(execution_id) != selected:
                log_feedback(execution_id, 1 if selected == 1 else -1)
                st.session_state.logged_feedback[execution_id] = selected

question = st.chat_input("Digite sua pergunta sobre políticas, procedimentos ou documentos internos...")

if question:
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Consultando a base de conhecimento..."):
            result = answer_question(question, category=selected_category)
            execution_id = log_execution(
                question=question,
                category_filter=selected_category,
                retrieved_chunks=result["sources"],
                has_sufficient_context=result["has_sufficient_context"],
                answer=result["answer"],
                response_time_ms=result["response_time_ms"],
            )
        st.markdown(result["answer"])
        if result["sources"]:
            with st.expander("📄 Fontes consultadas"):
                for s in result["sources"]:
                    category_label = CATEGORY_LABELS.get(s.get("category"), s.get("category", ""))
                    st.markdown(
                        f"- **{s['source_file']}** ({category_label}) — {s['location']} "
                        f"— relevância {s['score']:.2f}"
                    )

    st.session_state.messages.append({
        "role": "assistant",
        "content": result["answer"],
        "sources": result["sources"],
        "execution_id": execution_id,
    })
    st.rerun()
