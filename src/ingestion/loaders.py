"""Dispatch de ingestão: escolhe o loader correto pela extensão do arquivo."""
from pathlib import Path

from src.ingestion import (
    loader_csv,
    loader_docx,
    loader_html,
    loader_json,
    loader_md,
    loader_pdf,
    loader_pptx,
    loader_xlsx,
)

_LOADERS = {
    ".pdf": loader_pdf.load,
    ".docx": loader_docx.load,
    ".xlsx": loader_xlsx.load,
    ".pptx": loader_pptx.load,
    ".md": loader_md.load,
    ".csv": loader_csv.load,
    ".json": loader_json.load,
    ".html": loader_html.load,
}


def load_document(file_path: Path) -> list[dict]:
    """Retorna uma lista de unidades extraídas: [{"text", "location", "section"}, ...].

    Levanta ValueError para extensões não suportadas — falha alta e cedo em vez de ingerir
    silenciosamente um arquivo de formato desconhecido.
    """
    loader = _LOADERS.get(file_path.suffix.lower())
    if loader is None:
        raise ValueError(f"Formato não suportado: {file_path.suffix} ({file_path.name})")
    return loader(file_path)
