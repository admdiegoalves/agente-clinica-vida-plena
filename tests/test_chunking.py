from config import RAW_DOCS_DIR
from src.ingestion.loaders import load_document
from src.processing.chunking import build_chunks
from src.processing.cleaning import clean_text

PRIMITIVE_METADATA_KEYS = (
    "source_file", "category", "format", "title", "author",
    "doc_date", "location", "section", "chunk_index", "chunk_id",
)


def test_clean_text_collapses_whitespace_and_blank_lines():
    dirty = "Título  com   espaços\n\n\n\nParágrafo   seguinte.  \n"
    cleaned = clean_text(dirty)
    assert "   " not in cleaned
    assert "\n\n\n" not in cleaned
    assert cleaned == cleaned.strip()


def test_build_chunks_all_metadata_is_primitive_and_nonempty():
    sample_file = RAW_DOCS_DIR / "rh" / "manual_colaborador.pdf"
    units = load_document(sample_file)
    chunks = build_chunks(sample_file, units)

    assert chunks
    for chunk in chunks:
        for key in PRIMITIVE_METADATA_KEYS:
            assert key in chunk
            value = chunk[key]
            assert isinstance(value, (str, int))
            if key != "section":  # seção pode ser "N/A", mas nunca vazia/None
                assert value != ""
        assert chunk["text"].strip()


def test_chunk_ids_are_unique_and_deterministic_per_file():
    sample_file = RAW_DOCS_DIR / "rh" / "manual_colaborador.pdf"
    units = load_document(sample_file)

    chunks_a = build_chunks(sample_file, units)
    chunks_b = build_chunks(sample_file, units)

    ids_a = [c["chunk_id"] for c in chunks_a]
    assert len(ids_a) == len(set(ids_a))
    assert ids_a == [c["chunk_id"] for c in chunks_b]


def test_long_unit_is_split_into_multiple_chunks():
    long_text = "Frase de teste sobre política interna. " * 60  # bem acima do CHUNK_SIZE
    units = [{"text": long_text, "location": "página 1", "section": "N/A"}]
    sample_file = RAW_DOCS_DIR / "rh" / "manual_colaborador.pdf"

    chunks = build_chunks(sample_file, units)

    assert len(chunks) > 1
    assert all("parte" in c["location"] for c in chunks)
