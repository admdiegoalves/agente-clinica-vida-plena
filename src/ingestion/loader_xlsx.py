"""Extração de planilhas Excel: cada aba é lida linha a linha, com cabeçalho repetido por bloco."""
from pathlib import Path

import pandas as pd

ROWS_PER_CHUNK = 15


def load(file_path: Path) -> list[dict]:
    sheets = pd.read_excel(str(file_path), sheet_name=None, engine="openpyxl", dtype=str)
    units: list[dict] = []

    for sheet_name, df in sheets.items():
        df = df.fillna("")
        if df.empty:
            continue
        header = list(df.columns)
        rows = df.values.tolist()

        for start in range(0, len(rows), ROWS_PER_CHUNK):
            block = rows[start : start + ROWS_PER_CHUNK]
            lines = [" | ".join(str(h) for h in header)]
            for row in block:
                lines.append(" | ".join(f"{h}: {v}" for h, v in zip(header, row)))
            end = start + len(block)
            units.append({
                "text": "\n".join(lines),
                "location": f"planilha '{sheet_name}', linhas {start + 1}-{end}",
                "section": sheet_name,
            })

    return units
