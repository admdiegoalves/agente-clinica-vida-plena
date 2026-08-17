"""Extração de Markdown: divide por cabeçalhos (#, ##, ###), preservando a seção como metadado."""
from pathlib import Path

from langchain_text_splitters import MarkdownHeaderTextSplitter

HEADERS_TO_SPLIT_ON = [("#", "h1"), ("##", "h2"), ("###", "h3")]


def load(file_path: Path) -> list[dict]:
    text = file_path.read_text(encoding="utf-8")
    splitter = MarkdownHeaderTextSplitter(headers_to_split_on=HEADERS_TO_SPLIT_ON, strip_headers=False)
    docs = splitter.split_text(text)

    units: list[dict] = []
    for doc in docs:
        content = doc.page_content.strip()
        if not content:
            continue
        section = " > ".join(v for v in doc.metadata.values() if v) or "N/A"
        units.append({"text": content, "location": f"seção: {section}", "section": section})

    return units
