"""Log de execução append-only em JSONL: uma linha por pergunta, uma linha por evento de feedback."""
import json
import uuid
from datetime import datetime, timezone

from config import CHAT_MODEL, EXECUTIONS_LOG_FILE


def _append_line(record: dict) -> None:
    EXECUTIONS_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(EXECUTIONS_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def log_execution(question: str, category_filter: str | None, retrieved_chunks: list[dict],
                   has_sufficient_context: bool, answer: str, response_time_ms: int) -> str:
    execution_id = str(uuid.uuid4())
    record = {
        "execution_id": execution_id,
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
        "question": question,
        "category_filter": category_filter,
        "retrieved_chunks": [
            {"source_file": c.get("source_file"), "location": c.get("location"), "score": c.get("score")}
            for c in retrieved_chunks
        ],
        "has_sufficient_context": has_sufficient_context,
        "answer": answer,
        "response_time_ms": response_time_ms,
        "model": CHAT_MODEL,
    }
    _append_line(record)
    return execution_id


def log_feedback(execution_id: str, feedback: int) -> None:
    record = {
        "event": "feedback",
        "execution_id": execution_id,
        "feedback": feedback,
        "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
    }
    _append_line(record)
