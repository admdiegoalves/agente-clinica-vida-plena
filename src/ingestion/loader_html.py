"""Extração de HTML: remove marcação técnica e agrupa conteúdo por seção (h1-h3)."""
from pathlib import Path

from bs4 import BeautifulSoup

HEADING_TAGS = {"h1", "h2", "h3"}
NOISE_TAGS = ["script", "style", "nav", "footer", "header"]


def load(file_path: Path) -> list[dict]:
    html = file_path.read_text(encoding="utf-8")
    soup = BeautifulSoup(html, "lxml")

    for tag in soup.find_all(NOISE_TAGS):
        tag.decompose()

    body = soup.body or soup
    units: list[dict] = []
    current_section = "N/A"
    buffer: list[str] = []

    def flush():
        text = "\n".join(buffer).strip()
        if text:
            units.append({"text": text, "location": f"seção: {current_section}", "section": current_section})
        buffer.clear()

    for element in body.find_all(True, recursive=True):
        if element.name in HEADING_TAGS:
            flush()
            current_section = element.get_text(strip=True)
        elif element.name in ("p", "li"):
            text = element.get_text(strip=True)
            if text:
                buffer.append(text)
    flush()

    return units
