"""Extração de CSV: linhas agrupadas em blocos, com cabeçalho repetido em cada bloco."""
from pathlib import Path

import pandas as pd

ROWS_PER_CHUNK = 15


def load(file_path: Path) -> list[dict]:
    df = pd.read_csv(str(file_path), encoding="utf-8", dtype=str).fillna("")
    if df.empty:
        return []

    header = list(df.columns)
    rows = df.values.tolist()
    units: list[dict] = []

    for start in range(0, len(rows), ROWS_PER_CHUNK):
        block = rows[start : start + ROWS_PER_CHUNK]
        lines = [" | ".join(str(h) for h in header)]
        for row in block:
            lines.append(" | ".join(f"{h}: {v}" for h, v in zip(header, row)))
        end = start + len(block)
        units.append({
            "text": "\n".join(lines),
            "location": f"linhas {start + 1}-{end}",
            "section": "N/A",
        })

    return units
