"""Limpeza leve de texto extraído: normaliza espaços e remove linhas vazias em excesso.

Os loaders já descartam a marcação técnica de cada formato (tags HTML, sintaxe Markdown/JSON,
etc.), então esta etapa foca em ruído residual comum de extração: espaços duplicados, linhas em
branco repetidas e espaços nas bordas.
"""
import re

_MULTI_SPACE = re.compile(r"[ \t]+")
_MULTI_BLANK_LINE = re.compile(r"\n{3,}")


def clean_text(text: str) -> str:
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    lines = [_MULTI_SPACE.sub(" ", line).strip() for line in text.split("\n")]
    text = "\n".join(lines)
    text = _MULTI_BLANK_LINE.sub("\n\n", text)
    return text.strip()
