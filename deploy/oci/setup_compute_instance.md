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

Se o tenancy ainda não tiver nenhuma VCN (comum em conta nova), é preciso criar a rede primeiro:
VCN → Internet Gateway (attached) → Route Table (rota `0.0.0.0/0` → IGW) → Security List (ingress
TCP 22 e 8501 liberados) → Subnet pública associada a essa route table/security list. Tudo isso
pode ser feito pelo assistente "Create VCN with Internet Connectivity" no Console, ou via
`oci.core.VirtualNetworkClient` do SDK.

Console: **Compute → Instances → Create Instance**.

- **Imagem**: Ubuntu 22.04 (ou 24.04) Minimal.
- **Shape**: prefira **VM.Standard.A1.Flex** (Ampere ARM, Always Free com até 4 OCPU / 24 GB RAM,
  conforme o limite liberado para o tenancy — contas novas às vezes começam com um limite menor,
  ex. 2 OCPU/12 GB; confira em Limits, Quotas and Usage antes de lançar).
  **Atenção**: é comum o lançamento falhar com `Out of host capacity` — a capacidade Ampere
  gratuita é disputada e esgota rápido em regiões populares. Se isso acontecer, tente novamente
  em outro momento **ou** caia para o `VM.Standard.E2.1.Micro` (x86, sempre disponível, sem
  disputa de capacidade). Com só 1 GB de RAM, adicione um swapfile antes de instalar dependências:
  ```bash
  sudo fallocate -l 2G /swapfile && sudo chmod 600 /swapfile
  sudo mkswap /swapfile && sudo swapon /swapfile
  echo "/swapfile none swap sw 0 0" | sudo tee -a /etc/fstab
  ```
  Isso é suficiente para Streamlit + Chroma + cliente Gemini rodando juntos numa base pequena
  (dezenas de chunks); para uma base bem maior, prefira o A1.
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

> **Pegadinha conhecida das imagens Ubuntu da Oracle:** mesmo com o Security List e o `ufw`
> liberados, a porta pode continuar inacessível de fora. As imagens Ubuntu fornecidas pela Oracle
> vêm com um conjunto de regras `iptables` pré-instalado (`/etc/iptables/rules.v4`) que **antecede**
> as chains do `ufw` na tabela `INPUT` e só libera explicitamente a porta 22, rejeitando todo o
> resto antes mesmo do `ufw` ser avaliado. Sintoma: SSH funciona, a aplicação não — mesmo com
> `ufw status` mostrando a porta liberada. Diagnóstico e correção:
> ```bash
> sudo iptables -L INPUT -n --line-numbers   # procure uma regra REJECT antes das chains ufw-*
> sudo iptables -I INPUT 5 -p tcp -m state --state NEW -m tcp --dport 8501 -j ACCEPT
> sudo netfilter-persistent save            # persiste a regra para sobreviver a reboot
> ```
> (ajuste o número `5` para a posição imediatamente antes da regra `REJECT` no seu `iptables -L INPUT --line-numbers`).

## 5. Publicar o código e subir a aplicação

Duas formas de levar o código até a instância:

**a) Via Git** (recomendado se o repositório já está num remoto como GitHub): via SSH na
instância (`ssh ubuntu@<IP_PUBLICO>`), use `deploy/oci/bootstrap_vm.sh` como roteiro (instala
Python, clona o repo, cria o venv e instala as dependências).

**b) Via tar + scp** (mais simples se ainda não há remoto Git configurado): empacote o projeto
localmente excluindo o que não deve ir (venv, caches, git), envie e extraia na VM:
```bash
tar --exclude='.venv' --exclude='__pycache__' --exclude='.git' --exclude='.pytest_cache' \
    -czf /tmp/agente_challenge.tar.gz .
scp /tmp/agente_challenge.tar.gz ubuntu@<IP_PUBLICO>:~/agente_challenge.tar.gz
ssh ubuntu@<IP_PUBLICO> 'mkdir -p ~/agente_challenge && tar -xzf ~/agente_challenge.tar.gz -C ~/agente_challenge && rm ~/agente_challenge.tar.gz'
```
Isso já leva `data/chroma_db` (índice já gerado localmente) junto — evita reindexar na VM e
gastar cota da API do Gemini de novo. Depois, na VM: `python3 -m venv .venv && .venv/bin/pip
install -r requirements.txt`.

Crie o `.env` diretamente na VM (nunca via `scp` do seu `.env` local, para não deixar rastro em
histórico de shell/scp logs desnecessariamente — copie o conteúdo manualmente por SSH):
```bash
nano ~/agente_challenge/.env   # cole GOOGLE_API_KEY=...
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
consome a cota da API do Gemini (o Always Free da OCI cobre a VM, não a API do Gemini — o free
tier do Gemini tem limite de requisições por minuto/dia). Depois de capturar a evidência:

- Restrinja a Security List a apenas o seu IP, **ou**
- Pare/termine a instância (Console: Compute → Instances → Stop/Terminate).
