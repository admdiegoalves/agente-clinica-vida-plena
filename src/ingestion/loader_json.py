"""Extração de JSON: um chunk por unidade lógica (item de uma lista), sem splitter genérico.

Assume o formato {"documento": "...", "itens": [ {chave: valor, ...}, ... ]}, usado pelos FAQs
estruturados deste projeto. Para JSON sem essa forma, cai em um fallback que serializa o objeto
inteiro como um único chunk legível.
"""
import json
from pathlib import Path


def _item_to_text(item: dict) -> str:
    return "\n".join(f"{key.capitalize()}: {value}" for key, value in item.items())


def load(file_path: Path) -> list[dict]:
    with open(file_path, encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, dict) and isinstance(data.get("itens"), list):
        units = []
        for i, item in enumerate(data["itens"], start=1):
            if not isinstance(item, dict):
                continue
            units.append({
                "text": _item_to_text(item),
                "location": f"item {i}",
                "section": data.get("documento", "N/A"),
            })
        return units

    # Fallback genérico: serializa o objeto inteiro como texto legível em um único chunk.
    text = json.dumps(data, ensure_ascii=False, indent=2)
    return [{"text": text, "location": "documento completo", "section": "N/A"}]
