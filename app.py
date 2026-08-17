"""Interface Streamlit do agente de conhecimento interno da Clínica Vida Plena.

Só orquestra a UI — toda a lógica de RAG vive em src/. Rodar com:
    streamlit run app.py
"""
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

from config import CATEGORIES, CATEGORY_LABELS
from src.generation.chain import answer_question
from src.logging_utils.jsonl_logger import log_execution, log_feedback

load_dotenv()

ASSETS_DIR = Path(__file__).resolve().parent / "assets"
FAVICON_PATH = ASSETS_DIR / "favicon.png"
LOGO_PATH = ASSETS_DIR / "logo.png"

st.set_page_config(
    page_title="Assistente Clínica Vida Plena",
    page_icon=str(FAVICON_PATH) if FAVICON_PATH.exists() else "🩺",
    layout="centered",
)

header_col1, header_col2 = st.columns([1, 4], vertical_alignment="center")
with header_col1:
    if FAVICON_PATH.exists():
        st.image(str(FAVICON_PATH))
with header_col2:
    st.title("Assistente de Conhecimento Interno")
    st.caption(
        "⚠️ Você está conversando com um **agente de IA**, não com uma pessoa. As respostas são "
        "geradas a partir dos documentos internos oficiais da clínica; em casos sensíveis, sempre "
        "confirme com a área responsável indicada nas fontes."
    )

with st.sidebar:
    if LOGO_PATH.exists():
        st.image(str(LOGO_PATH))
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
