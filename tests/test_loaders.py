from pathlib import Path

import pytest

from config import RAW_DOCS_DIR
from src.ingestion.loaders import load_document
from src.ingestion.metadata import get_category, get_document_metadata

ALL_DOC_FILES = sorted(RAW_DOCS_DIR.rglob("*.*"))


@pytest.mark.parametrize("file_path", ALL_DOC_FILES, ids=lambda p: p.name)
def test_loader_returns_nonempty_units(file_path: Path):
    units = load_document(file_path)
    assert units, f"Nenhuma unidade extraída de {file_path.name}"
    for unit in units:
        assert unit["text"].strip()
        assert unit["location"]


@pytest.mark.parametrize("file_path", ALL_DOC_FILES, ids=lambda p: p.name)
def test_metadata_category_matches_folder(file_path: Path):
    meta = get_document_metadata(file_path)
    assert meta["category"] == file_path.parent.name
    assert meta["format"] == file_path.suffix.lstrip(".").lower()
    assert meta["title"]


def test_get_category_uses_parent_folder(tmp_path):
    fake_file = tmp_path / "rh" / "algum_arquivo.pdf"
    assert get_category(fake_file) == "rh"


def test_unsupported_extension_raises(tmp_path):
    bogus = tmp_path / "arquivo.xyz"
    bogus.write_text("conteudo")
    with pytest.raises(ValueError):
        load_document(bogus)
