# Guia de Deploy - Axio Gestto na VPS Hostinger (Ubuntu)

## Pré-requisitos
- VPS Ubuntu na Hostinger
- Acesso SSH (root ou sudo)
- Domínio apontando para o IP da VPS
- Conta n8n.io (cloud) ou n8n instalado

---

## PASSO 1: Preparar VPS

### 1.1. Conectar via SSH
```bash
ssh root@SEU_IP_VPS
# ou
ssh seu_usuario@SEU_IP_VPS
```

### 1.2. Atualizar sistema
```bash
sudo apt update && sudo apt upgrade -y
```

### 1.3. Instalar Docker
```bash
# Instalar dependências
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common

# Adicionar chave GPG do Docker
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg

# Adicionar repositório Docker
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io

# Verificar instalação
docker --version
```

### 1.4. Instalar Docker Compose
```bash
# Baixar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permissão de execução
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker-compose --version
```

### 1.5. Adicionar usuário ao grupo Docker (opcional)
```bash
sudo usermod -aG docker $USER
# Logout e login novamente para aplicar
```

---

## PASSO 2: Transferir código para VPS

### 2.1. Opção A - Via Git (RECOMENDADO)
```bash
# No VPS
cd /home
git clone https://github.com/SEU_USUARIO/axio_gestto.git
cd axio_gestto
```

### 2.2. Opção B - Via SCP (upload manual)
```bash
# No seu computador local (Windows PowerShell/CMD)
# Compactar projeto
tar -czf axio_gestto.tar.gz D:\Axio\axio_gestto

# Enviar para VPS
scp axio_gestto.tar.gz root@SEU_IP_VPS:/home/

# No VPS
cd /home
tar -xzf axio_gestto.tar.gz
cd axio_gestto
```

---

## PASSO 3: Configurar variáveis de ambiente

### 3.1. Criar arquivo .env
```bash
cd /home/axio_gestto
nano .env
```

### 3.2. Copiar e ajustar (IMPORTANTE: gerar valores novos)
```env
# DJANGO CORE
SECRET_KEY=GERAR_NOVO_TOKEN_AQUI_50_CARACTERES
DEBUG=False
ALLOWED_HOSTS=seu-dominio.com,www.seu-dominio.com,SEU_IP_VPS

# DATABASE
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gestao_negocios
DB_USER=postgres
DB_PASSWORD=SENHA_FORTE_POSTGRES_AQUI
DB_HOST=db
DB_PORT=5432

# EMAIL (SMTP - exemplo Gmail)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=senha-app-gmail
DEFAULT_FROM_EMAIL=noreply@seu-dominio.com

# REDIS & CELERY
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# N8N INTEGRATION (IMPORTANTE PARA BOT WHATSAPP)
N8N_API_KEY=GERAR_NOVO_TOKEN_32_CARACTERES

# CORS (se tiver frontend separado)
CORS_ALLOWED_ORIGINS=https://seu-dominio.com

# SUPERUSER (primeiro deploy)
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@seu-dominio.com
DJANGO_SUPERUSER_PASSWORD=SENHA_ADMIN_FORTE
```

**Salvar:** `Ctrl+O`, `Enter`, `Ctrl+X`

### 3.3. Gerar tokens seguros
```bash
# Gerar SECRET_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(50))"

# Gerar N8N_API_KEY
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Copiar e colar no .env
```

---

## PASSO 4: Configurar SSL/HTTPS

### 4.1. Opção A - Certificado Let's Encrypt (GRÁTIS, RECOMENDADO)

```bash
# Instalar Certbot
sudo apt install -y certbot

# Gerar certificado (método standalone - ANTES de subir Docker)
sudo certbot certonly --standalone -d seu-dominio.com -d www.seu-dominio.com --email seu-email@gmail.com --agree-tos --non-interactive

# Certificados gerados em:
# /etc/letsencrypt/live/seu-dominio.com/fullchain.pem
# /etc/letsencrypt/live/seu-dominio.com/privkey.pem

# Copiar para pasta do projeto
sudo mkdir -p /home/axio_gestto/nginx/certs
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /home/axio_gestto/nginx/certs/cert.pem
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem /home/axio_gestto/nginx/certs/key.pem
sudo chmod 644 /home/axio_gestto/nginx/certs/*
```

**Renovação automática:**
```bash
# Adicionar ao crontab (renova a cada 60 dias)
sudo crontab -e

# Adicionar linha:
0 0 1 */2 * certbot renew --quiet && cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem /home/axio_gestto/nginx/certs/cert.pem && cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem /home/axio_gestto/nginx/certs/key.pem && docker-compose -f /home/axio_gestto/docker-compose.yml restart nginx
```

### 4.2. Opção B - Certificado self-signed (APENAS TESTE)
```bash
mkdir -p /home/axio_gestto/nginx/certs
cd /home/axio_gestto/nginx/certs
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -subj "/C=BR/ST=State/L=City/O=Organization/CN=seu-dominio.com"
```

---

## PASSO 5: Ajustar docker-compose.yml (se necessário)

### 5.1. Editar arquivo
```bash
cd /home/axio_gestto
nano docker-compose.yml
```

### 5.2. Verificar mapeamento de certificados SSL
```yaml
services:
  nginx:
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./nginx/certs:/etc/nginx/certs:ro  # ← Verificar se existe
      - static_volume:/app/staticfiles:ro
      - media_volume:/app/media:ro
    ports:
      - "80:80"
      - "443:443"
```

---

## PASSO 6: Subir containers

### 6.1. Build e iniciar
```bash
cd /home/axio_gestto

# Build das imagens
docker-compose build

# Subir containers em background
docker-compose up -d

# Verificar status
docker-compose ps
```

**Saída esperada:**
```
NAME                  STATUS
axio_gestto-nginx     Up (healthy)
axio_gestto-web       Up (healthy)
axio_gestto-celery    Up
axio_gestto-db        Up (healthy)
axio_gestto-redis     Up (healthy)
```

### 6.2. Verificar logs (se algo falhar)
```bash
# Ver todos os logs
docker-compose logs

# Ver log específico
docker-compose logs web
docker-compose logs nginx
docker-compose logs db
```

### 6.3. Aplicar migrações (se não aplicou automaticamente)
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### 6.4. Criar superuser (se não criou automaticamente)
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## PASSO 7: Testar acesso

### 7.1. Verificar saúde do sistema
```bash
curl http://SEU_IP_VPS/health/
# Deve retornar: {"status": "ok"}
```

### 7.2. Acessar admin Django
```
https://seu-dominio.com/admin/
# Login: admin (conforme .env)
```

### 7.3. Acessar dashboard
```
https://seu-dominio.com/
# Redireciona para /accounts/login/
```

---

## PASSO 8: Configurar n8n para integração

### 8.1. Se usar n8n.io (cloud)

1. Acessar https://n8n.io
2. Importar workflows de `/n8n-workflows/*.json`
3. Editar cada workflow e ajustar:

**HTTP Request Nodes para APIs Django:**
```
URL Base: https://seu-dominio.com

Endpoint de comando:
POST https://seu-dominio.com/api/bot/processar/

Headers:
- X-API-Key: [valor do N8N_API_KEY do .env]
- X-Empresa-ID: 1
- Content-Type: application/json

Body (exemplo):
{
  "telefone": "5587999887766",
  "mensagem_original": "Quero agendar amanhã às 14h",
  "intencao": "agendar",
  "dados": {
    "servico": "corte",
    "data": "2025-12-26",
    "hora": "14:00"
  }
}
```

**Endpoints de consulta (GET):**
```
GET https://seu-dominio.com/api/n8n/servicos/
GET https://seu-dominio.com/api/n8n/profissionais/
GET https://seu-dominio.com/api/n8n/horarios-funcionamento/?dia_semana=0
GET https://seu-dominio.com/api/n8n/datas-especiais/?data_inicio=2025-12-01

Headers (em todos):
- X-API-Key: [valor do N8N_API_KEY]
```

### 8.2. Se usar n8n self-hosted (mesmo servidor)

**Instalar n8n via Docker (porta diferente):**
```bash
# Criar diretório para n8n
mkdir -p /home/n8n_data

# Rodar n8n (porta 5678)
docker run -d --restart unless-stopped \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=SUA_SENHA \
  -v /home/n8n_data:/home/node/.n8n \
  n8nio/n8n

# Acessar em: http://SEU_IP_VPS:5678
```

**IMPORTANTE:** Se n8n estiver no mesmo servidor, use URLs internas:
```
http://web:8000/api/bot/processar/
http://web:8000/api/n8n/servicos/
```

---

## PASSO 9: Firewall e segurança (IMPORTANTE)

### 9.1. Configurar UFW (firewall Ubuntu)
```bash
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 5678/tcp    # n8n (se self-hosted)
sudo ufw enable
sudo ufw status
```

### 9.2. Trocar senha root e configurar fail2ban
```bash
# Trocar senha root
sudo passwd root

# Instalar fail2ban (proteção contra brute force)
sudo apt install -y fail2ban
sudo systemctl enable fail2ban
sudo systemctl start fail2ban
```

---

## PASSO 10: Comandos úteis para manutenção

### 10.1. Parar/Reiniciar containers
```bash
cd /home/axio_gestto

# Parar todos
docker-compose down

# Reiniciar
docker-compose restart

# Reiniciar apenas um serviço
docker-compose restart web
docker-compose restart nginx
```

### 10.2. Ver logs em tempo real
```bash
docker-compose logs -f web
docker-compose logs -f celery
```

### 10.3. Backup do banco de dados
```bash
# Fazer backup
docker-compose exec db pg_dump -U postgres gestao_negocios > backup_$(date +%Y%m%d).sql

# Restaurar backup
docker-compose exec -T db psql -U postgres gestao_negocios < backup_20251225.sql
```

### 10.4. Atualizar código (quando fizer mudanças)
```bash
cd /home/axio_gestto
git pull origin main  # Se usar Git
docker-compose down
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### 10.5. Acessar shell Django dentro do container
```bash
docker-compose exec web python manage.py shell
```

---

## PASSO 11: Configuração inicial no Django Admin

1. Acesse `https://seu-dominio.com/admin/`
2. Login com credenciais do SUPERUSER
3. Configurar:
   - **Empresas** → Criar sua primeira empresa
   - **Profissionais** → Adicionar profissionais
   - **Serviços** → Adicionar serviços (corte, barba, etc)
   - **Horários de Funcionamento** → Configurar seg-dom
   - **Datas Especiais** → Adicionar feriados

---

## TROUBLESHOOTING

### Erro: "502 Bad Gateway"
```bash
# Verificar se web está rodando
docker-compose ps web

# Ver logs
docker-compose logs web

# Reiniciar
docker-compose restart web
```

### Erro: "Database connection failed"
```bash
# Verificar variáveis .env
cat .env | grep DB_

# Verificar se PostgreSQL está rodando
docker-compose ps db

# Ver logs do DB
docker-compose logs db
```

### Erro: "SSL certificate problem"
```bash
# Verificar se certificados existem
ls -la /home/axio_gestto/nginx/certs/

# Regenerar certificados
sudo certbot renew --force-renewal
```

### n8n não consegue se conectar
```bash
# Testar conectividade
curl -H "X-API-Key: SEU_TOKEN" https://seu-dominio.com/api/n8n/servicos/

# Verificar rate limiting nos logs
docker-compose logs nginx | grep "limiting"
```

---

## CHECKLIST FINAL

- [ ] VPS atualizada
- [ ] Docker e Docker Compose instalados
- [ ] Código transferido para /home/axio_gestto
- [ ] Arquivo .env configurado com valores seguros
- [ ] Certificado SSL configurado (Let's Encrypt)
- [ ] docker-compose up -d executado com sucesso
- [ ] Todos os containers em status "Up (healthy)"
- [ ] Admin Django acessível em /admin/
- [ ] Empresa, serviços e profissionais cadastrados
- [ ] n8n configurado com N8N_API_KEY correto
- [ ] Workflows importados e testados
- [ ] Firewall UFW habilitado
- [ ] Backup automático configurado

---

## Contatos e Suporte

- **Documentação Django:** https://docs.djangoproject.com/
- **Docker Compose:** https://docs.docker.com/compose/
- **n8n Docs:** https://docs.n8n.io/
- **Let's Encrypt:** https://letsencrypt.org/

---

**Desenvolvido por:** Axio Gestto Team
**Última atualização:** 2025-12-25
