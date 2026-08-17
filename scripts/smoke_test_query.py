"""Testa retrieval + geração via CLI, sem subir o Streamlit. Também calibra o SCORE_THRESHOLD.

Requer GOOGLE_API_KEY em .env e a base já indexada (rodar scripts/ingest_and_index.py antes).
Uso:
    python scripts/smoke_test_query.py
    python scripts/smoke_test_query.py "Quantos dias de férias posso tirar de uma vez?"
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.generation.chain import answer_question  # noqa: E402
from src.logging_utils.jsonl_logger import log_execution  # noqa: E402

DEFAULT_QUESTIONS = [
    # Perguntas dentro do domínio (esperado: resposta com fonte)
    "Quantos dias de antecedência preciso para solicitar férias?",
    "Posso cancelar uma consulta sem custo? Até quando?",
    "Por quanto tempo a clínica guarda o prontuário do paciente?",
    "Qual o limite diário de reembolso de alimentação em viagem?",
    # Pergunta fora do domínio (esperado: fallback)
    "Qual é a capital da França?",
]


def run_question(question: str):
    print(f"\n{'=' * 80}\nPERGUNTA: {question}\n{'=' * 80}")
    result = answer_question(question)
    print(f"\nRESPOSTA:\n{result['answer']}")
    print(f"\nContexto suficiente: {result['has_sufficient_context']}")
    print(f"Tempo de resposta: {result['response_time_ms']} ms")
    if result["sources"]:
        print("\nFontes consultadas:")
        for s in result["sources"]:
            print(f"  - {s['source_file']} | {s['location']} | score={s['score']}")

    execution_id = log_execution(
        question=question,
        category_filter=None,
        retrieved_chunks=result["sources"],
        has_sufficient_context=result["has_sufficient_context"],
        answer=result["answer"],
        response_time_ms=result["response_time_ms"],
    )
    print(f"\nexecution_id: {execution_id}")


def main():
    if len(sys.argv) > 1:
        run_question(" ".join(sys.argv[1:]))
    else:
        for question in DEFAULT_QUESTIONS:
            run_question(question)


if __name__ == "__main__":
    main()
