import json

import config
from src.logging_utils import jsonl_logger


def test_log_execution_and_feedback_appends_jsonl_lines(tmp_path, monkeypatch):
    log_file = tmp_path / "execucoes.jsonl"
    monkeypatch.setattr(config, "EXECUTIONS_LOG_FILE", log_file)
    monkeypatch.setattr(jsonl_logger, "EXECUTIONS_LOG_FILE", log_file)

    execution_id = jsonl_logger.log_execution(
        question="Quantos dias de férias eu tenho?",
        category_filter="rh",
        retrieved_chunks=[{"source_file": "a.pdf", "location": "página 1", "score": 0.8}],
        has_sufficient_context=True,
        answer="Resposta de teste [Fonte 1]",
        response_time_ms=123,
    )
    jsonl_logger.log_feedback(execution_id, 1)

    lines = log_file.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 2

    execution_record = json.loads(lines[0])
    assert execution_record["execution_id"] == execution_id
    assert execution_record["category_filter"] == "rh"
    assert execution_record["has_sufficient_context"] is True

    feedback_record = json.loads(lines[1])
    assert feedback_record["event"] == "feedback"
    assert feedback_record["execution_id"] == execution_id
    assert feedback_record["feedback"] == 1
