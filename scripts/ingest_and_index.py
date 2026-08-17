"""Pipeline de ingestão fim a fim: data/raw -> loaders -> chunking -> embeddings -> Chroma.

Idempotente: chunk_id determinístico faz upsert, então rodar de novo sobre arquivos inalterados
não duplica vetores. Rodar com o ambiente do projeto ativado:
    python scripts/ingest_and_index.py
"""
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config import RAW_DOCS_DIR  # noqa: E402
from src.ingestion.loaders import load_document  # noqa: E402
from src.indexing.vector_store import collection_count, upsert_chunks  # noqa: E402
from src.processing.chunking import build_chunks  # noqa: E402


def main():
    files = sorted(RAW_DOCS_DIR.rglob("*.*"))
    print(f"Encontrados {len(files)} documentos em {RAW_DOCS_DIR}\n")

    chunks_per_category = Counter()
    total_chunks = 0

    for file_path in files:
        units = load_document(file_path)
        chunks = build_chunks(file_path, units)
        upsert_chunks(chunks)

        category = file_path.parent.name
        chunks_per_category[category] += len(chunks)
        total_chunks += len(chunks)
        print(f"[OK] {file_path.relative_to(RAW_DOCS_DIR)} -> {len(chunks)} chunks indexados")

    print(f"\nTotal de chunks processados: {total_chunks}")
    print("Chunks por categoria:")
    for category, count in sorted(chunks_per_category.items()):
        print(f"  {category}: {count}")

    print(f"\nTotal de vetores na collection Chroma: {collection_count()}")


if __name__ == "__main__":
    main()
