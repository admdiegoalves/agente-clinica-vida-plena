"""Testes de integração da camada de retrieval — exigem OPENAI_API_KEY e a base já indexada
(rodar scripts/ingest_and_index.py antes). São pulados automaticamente sem a chave configurada.
"""
import os

import pytest
from dotenv import load_dotenv

load_dotenv()

pytestmark = pytest.mark.skipif(
    not os.getenv("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY não configurada — testes de retrieval exigem chamadas reais à API",
)


def test_in_domain_question_returns_context():
    from src.retrieval.retriever import retrieve

    result = retrieve("Quantos dias de antecedência preciso para solicitar férias?")
    assert result["has_context"] is True
    assert result["chunks"]
    assert result["chunks"][0]["score"] >= 0


def test_out_of_domain_question_has_no_context():
    from src.retrieval.retriever import retrieve

    result = retrieve("Qual é a capital da França?", score_threshold=0.6)
    assert result["has_context"] is False


def test_category_filter_restricts_results():
    from src.retrieval.retriever import retrieve

    result = retrieve("política interna", top_k=10, category="rh", score_threshold=0.0)
    assert all(c["category"] == "rh" for c in result["chunks"])
