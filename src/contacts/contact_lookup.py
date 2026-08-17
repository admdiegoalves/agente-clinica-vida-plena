"""Lookup determinístico de contatos por categoria, usado no fallback de "não encontrei resposta".

Não é indexado no Chroma de propósito: o fallback precisa de 100% de precisão ao apontar o
colaborador para a área certa, o que um retrieval semântico não garante.
"""
import json

from config import CATEGORY_LABELS, CONTACTS_FILE

_contacts: dict | None = None


def _load_contacts() -> dict:
    global _contacts
    if _contacts is None:
        with open(CONTACTS_FILE, encoding="utf-8") as f:
            _contacts = json.load(f)
    return _contacts


def get_contact(category: str | None) -> dict:
    contacts = _load_contacts()
    entry = contacts.get(category) if category else None
    if entry is None:
        entry = contacts["geral"]
    return entry


def format_contact_line(category: str | None) -> str:
    contact = get_contact(category)
    label = CATEGORY_LABELS.get(category, contact["area"]) if category else contact["area"]
    return f"{label}: {contact['responsavel']} — {contact['email']} (ramal {contact['ramal']})"
