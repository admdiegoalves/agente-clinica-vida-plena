"""Resolução da GOOGLE_API_KEY em qualquer ambiente: .env local (scripts/CLI) ou
st.secrets (Streamlit Community Cloud, onde não existe arquivo .env)."""
import os


def get_google_api_key() -> str | None:
    key = os.getenv("GOOGLE_API_KEY")
    if key:
        return key

    try:
        import streamlit as st
        key = st.secrets.get("GOOGLE_API_KEY")
    except Exception:
        key = None

    if key:
        os.environ["GOOGLE_API_KEY"] = key
    return key
