"""Chunking: divide as unidades extraídas por um loader em chunks finais com metadados.

Cada chunk carrega apenas tipos primitivos em seus metadados (str/int), como exigido pelo Chroma,
e um chunk_id determinístico (`"{source_file}::{chunk_index}"`) que permite reingestão idempotente:
rodar o pipeline de novo sobre o mesmo arquivo faz upsert em vez de duplicar vetores.
"""
from pathlib import Path

from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import CHUNK_OVERLAP, CHUNK_SIZE
from src.ingestion.metadata import get_document_metadata
from src.processing.cleaning import clean_text

_splitter = RecursiveCharacterTextSplitter(
    chunk_size=CHUNK_SIZE,
    chunk_overlap=CHUNK_OVERLAP,
    separators=["\n\n", "\n", ". ", " ", ""],
)


def build_chunks(file_path: Path, units: list[dict]) -> list[dict]:
    doc_meta = get_document_metadata(file_path)
    chunks: list[dict] = []
    chunk_index = 0

    for unit in units:
        text = clean_text(unit["text"])
        if not text:
            continue

        sub_texts = _splitter.split_text(text) if len(text) > CHUNK_SIZE else [text]

        for i, sub_text in enumerate(sub_texts):
            location = unit["location"]
            if len(sub_texts) > 1:
                location = f"{location} (parte {i + 1}/{len(sub_texts)})"

            chunks.append({
                **doc_meta,
                "location": location,
                "section": unit["section"],
                "chunk_index": chunk_index,
                "chunk_id": f"{doc_meta['source_file']}::{chunk_index}",
                "text": sub_text,
            })
            chunk_index += 1

    return chunks
