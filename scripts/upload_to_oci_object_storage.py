"""Faz upload dos documentos originais (data/raw/) para um bucket OCI Object Storage.

Pré-requisitos (ver deploy/oci/setup_compute_instance.md para o passo a passo completo):
  1. Conta OCI (Always Free serve) com um bucket já criado no compartment desejado.
  2. Par de chaves de API cadastrado no Console (Usuário > Tokens e chaves de autenticação),
     com o arquivo ~/.oci/config apontando para a chave privada (perfil DEFAULT).
  3. .env preenchido com OCI_NAMESPACE, OCI_BUCKET_NAME e OCI_COMPARTMENT_ID.

O runtime do agente usa o índice Chroma local para responder perguntas — o Object Storage aqui
é o repositório do arquivo original (backup/auditoria), não uma dependência do caminho quente de
retrieval, para manter a aplicação simples e sem chamadas de rede extras por pergunta.

Uso:
    python scripts/upload_to_oci_object_storage.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import oci  # noqa: E402
from dotenv import load_dotenv  # noqa: E402

from config import RAW_DOCS_DIR  # noqa: E402

load_dotenv()


def main():
    bucket_name = os.getenv("OCI_BUCKET_NAME")
    namespace_env = os.getenv("OCI_NAMESPACE")
    if not bucket_name:
        raise SystemExit("OCI_BUCKET_NAME não definido no .env")

    oci_config = oci.config.from_file()  # lê ~/.oci/config, perfil DEFAULT
    client = oci.object_storage.ObjectStorageClient(oci_config)
    namespace = namespace_env or client.get_namespace().data

    files = sorted(RAW_DOCS_DIR.rglob("*.*"))
    print(f"Enviando {len(files)} arquivos para o bucket '{bucket_name}' (namespace {namespace})\n")

    for file_path in files:
        category = file_path.parent.name
        object_name = f"{category}/{file_path.name}"
        with open(file_path, "rb") as f:
            client.put_object(namespace, bucket_name, object_name, f)
        print(f"[OK] {object_name}")

    print("\nUpload concluído.")


if __name__ == "__main__":
    main()
