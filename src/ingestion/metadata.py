"""Metadados de documento (título, autor/área, data) e derivação de categoria por pasta.

Numa empresa real esses metadados viriam de um sistema de gestão documental (SharePoint,
Google Drive etc.). Como os documentos aqui são gerados sinteticamente para o desafio, mantemos
um pequeno registro estático por nome de arquivo.
"""
from pathlib import Path

DOCUMENT_REGISTRY: dict[str, dict[str, str]] = {
    "manual_colaborador.pdf": {
        "title": "Manual do Colaborador",
        "author": "Recursos Humanos",
        "doc_date": "2025-08-01",
    },
    "politica_ferias_banco_horas.docx": {
        "title": "Política de Férias e Banco de Horas",
        "author": "Recursos Humanos",
        "doc_date": "2025-09-15",
    },
    "tabela_beneficios_por_cargo.xlsx": {
        "title": "Tabela de Benefícios por Cargo",
        "author": "Recursos Humanos",
        "doc_date": "2025-11-01",
    },
    "politica_reembolso_despesas.pdf": {
        "title": "Política de Reembolso de Despesas",
        "author": "Financeiro e Contábil",
        "doc_date": "2025-06-10",
    },
    "centros_de_custo.csv": {
        "title": "Centros de Custo",
        "author": "Financeiro e Contábil",
        "doc_date": "2026-01-05",
    },
    "procedimento_pagamento_fornecedores.docx": {
        "title": "Procedimento de Pagamento a Fornecedores",
        "author": "Financeiro e Contábil",
        "doc_date": "2025-07-22",
    },
    "manual_atendimento_paciente.pdf": {
        "title": "Manual de Atendimento ao Paciente",
        "author": "Coordenação de Operações e Atendimento",
        "doc_date": "2025-05-12",
    },
    "protocolo_agendamento_cancelamento.docx": {
        "title": "Protocolo de Agendamento e Cancelamento de Consultas",
        "author": "Coordenação de Operações e Atendimento",
        "doc_date": "2025-10-03",
    },
    "treinamento_fluxo_atendimento_recepcao.pptx": {
        "title": "Treinamento: Fluxo de Atendimento na Recepção",
        "author": "Coordenação de Operações e Atendimento",
        "doc_date": "2025-04-18",
    },
    "politica_privacidade_lgpd.pdf": {
        "title": "Política de Privacidade e Proteção de Dados (LGPD)",
        "author": "Jurídico e Compliance",
        "doc_date": "2025-03-20",
    },
    "termo_consentimento_dados_paciente.docx": {
        "title": "Termo de Consentimento para Tratamento de Dados do Paciente",
        "author": "Jurídico e Compliance",
        "doc_date": "2025-03-20",
    },
    "faq_compliance_lgpd.json": {
        "title": "FAQ de Compliance e LGPD",
        "author": "Jurídico e Compliance",
        "doc_date": "2025-12-01",
    },
    "protocolo_biosseguranca_controle_infeccao.pdf": {
        "title": "Protocolo de Biossegurança e Controle de Infecção",
        "author": "Qualidade e Biossegurança",
        "doc_date": "2025-02-14",
    },
    "checklist_esterilizacao_autoclave.xlsx": {
        "title": "Checklist de Esterilização de Autoclave",
        "author": "Qualidade e Biossegurança",
        "doc_date": "2025-02-14",
    },
    "comunicado_home_office.html": {
        "title": "Comunicado Interno: Nova Política de Home Office Administrativo",
        "author": "Comunicação Interna",
        "doc_date": "2026-02-03",
    },
    "newsletter_mensal.md": {
        "title": "Newsletter Mensal — Edição de Janeiro/2026",
        "author": "Comunicação Interna",
        "doc_date": "2026-01-30",
    },
    "missao_visao_valores.md": {
        "title": "Missão, Visão e Valores",
        "author": "Diretoria Executiva",
        "doc_date": "2025-01-10",
    },
    "planejamento_estrategico_2026.pptx": {
        "title": "Planejamento Estratégico 2026",
        "author": "Diretoria Executiva",
        "doc_date": "2026-01-15",
    },
}

_DEFAULT_METADATA = {"title": "", "author": "Não informado", "doc_date": "Não informado"}


def get_category(file_path: Path) -> str:
    """Categoria = nome da subpasta imediatamente abaixo de data/raw/."""
    return file_path.parent.name


def get_document_metadata(file_path: Path) -> dict[str, str]:
    entry = DOCUMENT_REGISTRY.get(file_path.name, _DEFAULT_METADATA)
    title = entry["title"] or file_path.stem.replace("_", " ").title()
    return {
        "source_file": file_path.name,
        "category": get_category(file_path),
        "format": file_path.suffix.lstrip(".").lower(),
        "title": title,
        "author": entry["author"],
        "doc_date": entry["doc_date"],
    }
