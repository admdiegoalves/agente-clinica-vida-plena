"""Extração de texto de PDF, por página. OCR é best-effort e desligado por padrão (ver config.py)."""
from pathlib import Path

from pypdf import PdfReader

from config import ENABLE_OCR_FALLBACK


def _ocr_page(pdf_path: Path, page_number: int) -> str:
    """Fallback best-effort via Tesseract. Retorna string vazia se as dependências não estiverem
    disponíveis (pytesseract/pdf2image/Tesseract binário), em vez de derrubar a ingestão inteira.
    """
    try:
        import pytesseract
        from pdf2image import convert_from_path

        images = convert_from_path(str(pdf_path), first_page=page_number, last_page=page_number)
        if not images:
            return ""
        return pytesseract.image_to_string(images[0], lang="por")
    except Exception:
        return ""


def load(file_path: Path) -> list[dict]:
    reader = PdfReader(str(file_path))
    units = []
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()
        if not text and ENABLE_OCR_FALLBACK:
            text = _ocr_page(file_path, i).strip()
        if not text:
            continue
        units.append({"text": text, "location": f"página {i}", "section": "N/A"})
    return units
