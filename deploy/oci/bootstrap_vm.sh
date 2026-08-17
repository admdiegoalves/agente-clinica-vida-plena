#!/usr/bin/env bash
# Roteiro de setup da instância OCI Compute (Ubuntu 22.04/24.04).
# Rodar via SSH na VM: bash bootstrap_vm.sh <url-do-repo-git>
set -euo pipefail

REPO_URL="${1:?Uso: bash bootstrap_vm.sh <url-do-repo-git>}"
APP_DIR="$HOME/agente_challenge"

sudo apt-get update -y
sudo apt-get install -y python3.12 python3.12-venv python3-pip git ufw

if [ ! -d "$APP_DIR" ]; then
  git clone "$REPO_URL" "$APP_DIR"
fi
cd "$APP_DIR"

python3.12 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

sudo ufw allow 8501/tcp
sudo ufw --force enable

echo ""
echo "Setup concluído em $APP_DIR"
echo "Próximos passos manuais:"
echo "  1. Copiar data/chroma_db já indexado via scp (evita reprocessar embeddings)"
echo "  2. Criar .env com OPENAI_API_KEY (nunca commitado)"
echo "  3. Instalar o serviço systemd: ver deploy/oci/run_app.service"
