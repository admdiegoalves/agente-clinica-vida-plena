"""Templates de prompt: contexto restrito ao retrieval, citação de fonte, tom institucional."""
from langchain_core.prompts import ChatPromptTemplate

from config import CATEGORY_LABELS

SYSTEM_PROMPT = """Você é o assistente de conhecimento interno da Clínica Vida Plena, disponível a \
qualquer colaborador da empresa. Seu papel é responder perguntas usando SOMENTE as informações do \
CONTEXTO fornecido abaixo, extraído de documentos internos oficiais.

Regras obrigatórias:
- Responda sempre em português, em tom institucional e claro.
- Use apenas o CONTEXTO fornecido. Nunca use conhecimento externo ou suposições.
- Ao usar uma informação, cite a fonte correspondente inline no formato [Fonte N], referenciando \
o número do bloco de contexto de onde ela veio.
- Se o CONTEXTO não contiver informação suficiente para responder com segurança, diga isso \
explicitamente em vez de arriscar uma resposta incorreta.
- Nunca invente números, prazos, valores ou políticas que não estejam explicitamente no CONTEXTO.
- Deixe claro, quando relevante, que esta é uma resposta gerada por um agente de IA e que casos \
sensíveis devem ser confirmados com a área responsável.

CONTEXTO:
{context}"""

_prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])


def get_prompt() -> ChatPromptTemplate:
    return _prompt


def format_context(chunks: list[dict]) -> str:
    blocks = []
    for i, chunk in enumerate(chunks, start=1):
        category_label = CATEGORY_LABELS.get(chunk.get("category"), chunk.get("category", ""))
        header = (
            f"[Fonte {i}] Arquivo: {chunk.get('source_file')} | "
            f"Categoria: {category_label} | Localização: {chunk.get('location')}"
        )
        blocks.append(f"{header}\n{chunk['text']}")
    return "\n\n".join(blocks)
