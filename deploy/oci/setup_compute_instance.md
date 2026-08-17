# Deploy na OCI (Always Free)

Este guia cobre os dois serviços OCI usados neste projeto:

1. **Object Storage** — repositório dos documentos originais (`data/raw/`).
2. **Compute (Always Free)** — execução completa da aplicação (Streamlit + RAG + Chroma) para
   gerar a evidência (foto/vídeo) de execução em nuvem exigida pelo desafio.

## 0. Pré-requisito: criar a conta OCI

Crie uma conta em [cloud.oracle.com](https://cloud.oracle.com) usando o tier **Always Free**
(cartão de crédito é solicitado para verificação, mas os recursos Always Free não geram cobrança).
Anote a **região** escolhida — recursos Always Free têm disponibilidade por região, então se um
recurso (ex: Ampere A1) estiver indisponível, tente outra região próxima.

## 1. Gerar chave de API (necessária para o script de upload)

No Console OCI: **perfil (canto superior direito) → User Settings → Tokens and Keys → Add API Key**.

Localmente:
```bash
mkdir -p ~/.oci
openssl genrsa -out ~/.oci/oci_api_key.pem 2048
openssl rsa -pubout -in ~/.oci/oci_api_key.pem -out ~/.oci/oci_api_key_public.pem
```
Cole o conteúdo de `oci_api_key_public.pem` no Console. Ele vai gerar um **fingerprint** — anote-o
junto com o **tenancy OCID**, **user OCID** e **region**, todos exibidos no Console.

Crie `~/.oci/config`:
```ini
[DEFAULT]
user=ocid1.user.oc1..xxxxx
fingerprint=xx:xx:xx:...
tenancy=ocid1.tenancy.oc1..xxxxx
region=sa-saopaulo-1
key_file=~/.oci/oci_api_key.pem
```

## 2. Criar o bucket de Object Storage

Console: **Storage → Buckets → Create Bucket** (nome sugerido: `clinica-vida-plena-documentos`).
Anote o **namespace** do tenancy (aparece no topo da página de Buckets) e o **compartment OCID**.

Preencha no `.env` do projeto:
```
OCI_NAMESPACE=<namespace do tenancy>
OCI_BUCKET_NAME=clinica-vida-plena-documentos
OCI_COMPARTMENT_ID=<compartment OCID>
```

Rode o upload:
```bash
python scripts/upload_to_oci_object_storage.py
```

## 3. Criar a instância Compute (Always Free)

Console: **Compute → Instances → Create Instance**.

- **Imagem**: Ubuntu 22.04 (ou 24.04) Minimal.
- **Shape**: prefira **VM.Standard.A1.Flex** (Ampere ARM, Always Free com até 4 OCPU / 24 GB RAM)
  em vez do `VM.Standard.E2.1.Micro` (só 1 GB RAM — apertado para Streamlit + Chroma + cliente
  OpenAI rodando juntos). Se a capacidade Ampere A1 estiver esgotada na região, tente novamente
  mais tarde ou troque de região.
- **Chave SSH**: gere um par local (`ssh-keygen -t ed25519`) e cole a chave pública na criação.
- Anote o **IP público** da instância ao final da criação.

## 4. Abrir a porta 8501 (Streamlit)

**Nos dois lugares — esquecer um deles é a causa mais comum de "a porta não responde":**

1. **Security List / NSG da VCN** (Console: Networking → Virtual Cloud Networks → sua VCN →
   Security Lists → Add Ingress Rule): permitir TCP na porta `8501`, origem `0.0.0.0/0` (ou seu
   IP, para restringir).
2. **Firewall do próprio SO**, via SSH na instância:
   ```bash
   sudo ufw allow 8501/tcp
   sudo ufw reload
   ```

## 5. Publicar o código e subir a aplicação

Antes deste passo, publique o repositório local num remoto Git (ex: GitHub), já que a instância
vai clonar de lá.

Via SSH na instância (`ssh ubuntu@<IP_PUBLICO>`), use `deploy/oci/bootstrap_vm.sh` como roteiro
(instala Python, clona o repo, cria o venv e instala as dependências).

Copie o índice já gerado localmente em vez de reindexar na VM (evita reprocessar embeddings e
gastar créditos da API de novo):
```bash
scp -r data/chroma_db ubuntu@<IP_PUBLICO>:~/agente_challenge/data/
```

Crie o `.env` diretamente na VM (nunca via `scp` do seu `.env` local, para não deixar rastro em
histórico de shell/scp logs desnecessariamente — copie o conteúdo manualmente por SSH):
```bash
nano ~/agente_challenge/.env   # cole OPENAI_API_KEY=...
```

Suba a aplicação com `systemd` (ver `deploy/oci/run_app.service`), que mantém o processo vivo
mesmo após fechar a sessão SSH:
```bash
sudo cp deploy/oci/run_app.service /etc/systemd/system/agente-clinica.service
sudo systemctl daemon-reload
sudo systemctl enable --now agente-clinica.service
sudo systemctl status agente-clinica.service
```

## 6. Capturar a evidência de execução em nuvem

Acesse `http://<IP_PUBLICO>:8501` de um navegador **fora** da VM e faça algumas perguntas de
teste. Capture print(s) ou um vídeo curto mostrando a URL pública, a conversa e as fontes citadas
— essa é a evidência exigida pelo desafio de que o agente rodou de fato em nuvem.

## 7. Depois de capturar a evidência: restrinja ou derrube a instância

A VM fica exposta publicamente **sem autenticação** enquanto estiver de pé, e cada pergunta
consome a API paga da OpenAI (o Always Free cobre a VM, não a API). Depois de capturar a
evidência:

- Restrinja a Security List a apenas o seu IP, **ou**
- Pare/termine a instância (Console: Compute → Instances → Stop/Terminate).
