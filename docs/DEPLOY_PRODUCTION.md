# 🚀 Guia de Deploy em Produção - Axio Gestto

## 📋 Índice

1. [Pré-requisitos](#pré-requisitos)
2. [Preparação do Servidor](#preparação-do-servidor)
3. [Configuração do Ambiente](#configuração-do-ambiente)
4. [Deploy com Docker](#deploy-com-docker)
5. [Configuração da Integração n8n](#configuração-da-integração-n8n)
6. [Configuração da Evolution API](#configuração-da-evolution-api)
7. [Configuração de Pagamentos](#configuração-de-pagamentos)
8. [SSL/HTTPS](#sslhttps)
9. [Monitoramento e Logs](#monitoramento-e-logs)
10. [Backup e Recuperação](#backup-e-recuperação)
11. [Troubleshooting](#troubleshooting)

---

## 🎯 Pré-requisitos

### **Infraestrutura Necessária:**

- ✅ Servidor Ubuntu 20.04+ (mínimo: 2 CPU, 4GB RAM, 40GB SSD)
- ✅ Domínio configurado (ex: `axiogestto.com`)
- ✅ Acesso SSH ao servidor
- ✅ n8n instalado e rodando (VPS ou Cloud)
- ✅ Evolution API configurada

### **Serviços Externos:**

- ✅ Conta OpenAI com créditos (para IA do bot)
- ✅ Conta Stripe ou Asaas (para pagamentos)
- ✅ SMTP configurado (Gmail, SendGrid, etc)

---

## 🖥️ Preparação do Servidor

### **1. Conectar ao Servidor**

```bash
ssh root@seu-servidor.com
```

### **2. Atualizar Sistema**

```bash
apt update && apt upgrade -y
```

### **3. Instalar Dependências Básicas**

```bash
apt install -y git curl wget build-essential
```

### **4. Clonar Repositório**

```bash
cd /opt
git clone https://github.com/seu-usuario/axio_gestto.git
cd axio_gestto
```

---

## ⚙️ Configuração do Ambiente

### **1. Criar Arquivo .env**

```bash
cp .env.example .env
nano .env
```

### **2. Configurar Variáveis Obrigatórias**

```bash
# ============================================
# DJANGO CORE
# ============================================
SECRET_KEY=<gerar-chave-segura-50-caracteres>
DEBUG=False
ALLOWED_HOSTS=axiogestto.com,www.axiogestto.com,seu-ip-servidor

# ============================================
# DATABASE
# ============================================
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gestao_negocios
DB_USER=postgres
DB_PASSWORD=<senha-postgres-forte>
DB_HOST=db
DB_PORT=5432

# ============================================
# N8N INTEGRATION (NOVO!)
# ============================================
N8N_API_KEY=<gerar-token-32-caracteres>
N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/bot-universal

# ============================================
# EVOLUTION API (NOVO!)
# ============================================
EVOLUTION_API_URL=https://evolution.axiodev.cloud
EVOLUTION_API_KEY=<sua-evolution-api-key-global>

# ============================================
# SITE URL
# ============================================
SITE_URL=https://axiogestto.com

# ============================================
# EMAIL
# ============================================
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=noreply@axiogestto.com
EMAIL_HOST_PASSWORD=<senha-app-gmail>
DEFAULT_FROM_EMAIL=noreply@axiogestto.com

# ============================================
# PAGAMENTOS
# ============================================
# Stripe (Internacional)
STRIPE_PUBLIC_KEY=pk_live_...
STRIPE_SECRET_KEY=sk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Asaas (Brasil) - RECOMENDADO
ASAAS_API_KEY=<sua-asaas-api-key>
ASAAS_SANDBOX=False

# ============================================
# SUPERUSER
# ============================================
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@axiogestto.com
DJANGO_SUPERUSER_PASSWORD=<senha-admin-forte>

# ============================================
# REDIS
# ============================================
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# ============================================
# CORS
# ============================================
CORS_ALLOWED_ORIGINS=https://axiogestto.com,https://www.axiogestto.com
```

### **3. Gerar Tokens Seguros**

```bash
# Gerar SECRET_KEY
python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))"

# Gerar N8N_API_KEY
python3 -c "import secrets; print('N8N_API_KEY=' + secrets.token_urlsafe(32))"
```

**⚠️ IMPORTANTE:** Salve esses tokens em um lugar seguro!

---

## 🐳 Deploy com Docker

### **1. Executar Script de Deploy**

```bash
sudo bash deploy.sh
```

O script vai:
- ✅ Instalar Docker e Docker Compose
- ✅ Verificar arquivo .env
- ✅ Gerar certificados SSL (self-signed para teste)
- ✅ Construir imagens Docker
- ✅ Iniciar containers
- ✅ Executar migrações
- ✅ Criar superuser

### **2. Verificar Containers**

```bash
docker-compose ps
```

**Resultado Esperado:**
```
NAME              COMMAND                  SERVICE    STATUS
gestao_web        "sh -c 'python manag…"   web        Up (healthy)
gestao_db         "docker-entrypoint.s…"   db         Up (healthy)
gestao_redis      "docker-entrypoint.s…"   redis      Up (healthy)
gestao_celery     "celery -A config wo…"   celery     Up
gestao_nginx      "/docker-entrypoint.…"   nginx      Up
```

### **3. Testar Health Check**

```bash
curl http://localhost/health/
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected"
}
```

---

## 🤖 Configuração da Integração n8n

### **1. Importar Template no n8n**

1. Acesse seu n8n: `https://seu-n8n.com`
2. Clique em "Import from File"
3. Selecione: `n8n-workflows/TEMPLATE_Bot_Universal_VPS_Simplificado.json`
4. Clique em "Import"

### **2. Configurar Workflow**

1. Abra o workflow importado
2. Clique no node **"⚙️ Configurações + Dados"**
3. Edite os valores:

```javascript
config_django_url: "https://axiogestto.com"
config_django_key: "<N8N_API_KEY do .env>"
config_evolution_url: "https://evolution.axiodev.cloud"
config_evolution_key: "<EVOLUTION_API_KEY do .env>"
config_openai_key: "sk-proj-<sua-openai-key>"
```

4. **Salve** (Ctrl+S)
5. **Ative** o workflow (toggle superior direito)

### **3. Copiar URL do Webhook**

1. Clique no node **"Webhook - Recebe Mensagem"**
2. Copie a "Production URL"
3. Exemplo: `https://seu-n8n.com/webhook/bot-universal`

### **4. Atualizar .env do Django**

```bash
nano /opt/axio_gestto/.env
```

Certifique-se que `N8N_WEBHOOK_URL` está correto:
```
N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/bot-universal
```

### **5. Reiniciar Containers**

```bash
cd /opt/axio_gestto
docker-compose restart web celery
```

---

## 📱 Configuração da Evolution API

### **1. Verificar Evolution API**

```bash
curl https://evolution.axiodev.cloud/
```

Deve retornar status 200.

### **2. Obter API Key Global**

1. Acesse painel da Evolution API
2. Vá em: Settings → API Key
3. Copie a API Key Global
4. Cole no `.env`:
   ```
   EVOLUTION_API_KEY=SUA-API-KEY-AQUI
   ```

### **3. Testar Conexão**

No servidor Django:

```bash
docker-compose exec web python manage.py shell
```

Execute:

```python
from empresas.services.evolution_api import EvolutionAPIService
from empresas.models import ConfiguracaoWhatsApp, Empresa

# Pegar primeira empresa
empresa = Empresa.objects.first()
config, _ = ConfiguracaoWhatsApp.objects.get_or_create(empresa=empresa)

# Testar conexão
service = EvolutionAPIService(config)
result = service._request('GET', 'instance/fetchInstances')
print("Sucesso!" if result['success'] else f"Erro: {result.get('error')}")
```

**Resposta esperada:** `Sucesso!`

---

## 💳 Configuração de Pagamentos

### **Opção A: Stripe (Internacional)**

1. Acesse: https://dashboard.stripe.com/apikeys
2. Copie as chaves:
   - Publishable key → `STRIPE_PUBLIC_KEY`
   - Secret key → `STRIPE_SECRET_KEY`
3. Configure webhook:
   - URL: `https://axiogestto.com/api/stripe/webhook/`
   - Eventos: `checkout.session.completed`, `customer.subscription.updated`
4. Copie o webhook secret → `STRIPE_WEBHOOK_SECRET`

### **Opção B: Asaas (Brasil) - RECOMENDADO**

1. Acesse: https://www.asaas.com/api/v3/myAccount
2. Copie a API Key → `ASAAS_API_KEY`
3. Configure:
   ```
   ASAAS_SANDBOX=False  # Para produção
   ```

---

## 🔒 SSL/HTTPS

### **Opção A: Let's Encrypt (Recomendado)**

```bash
# Instalar Certbot
apt install -y certbot python3-certbot-nginx

# Parar Nginx temporariamente
docker-compose stop nginx

# Gerar certificados
certbot certonly --standalone -d axiogestto.com -d www.axiogestto.com

# Copiar certificados para projeto
mkdir -p /opt/axio_gestto/nginx/certs
cp /etc/letsencrypt/live/axiogestto.com/fullchain.pem /opt/axio_gestto/nginx/certs/cert.pem
cp /etc/letsencrypt/live/axiogestto.com/privkey.pem /opt/axio_gestto/nginx/certs/key.pem

# Reiniciar Nginx
cd /opt/axio_gestto
docker-compose up -d nginx
```

### **Opção B: Cloudflare (Mais Simples)**

1. Adicione domínio no Cloudflare
2. Configure DNS:
   - Tipo `A` → Nome: `@` → IP do servidor
   - Tipo `A` → Nome: `www` → IP do servidor
3. Ative SSL/TLS → Full (strict)
4. Cloudflare cuida do SSL automaticamente ✅

---

## 📊 Monitoramento e Logs

### **Ver Logs em Tempo Real**

```bash
# Todos os containers
docker-compose logs -f

# Apenas Django
docker-compose logs -f web

# Apenas Celery
docker-compose logs -f celery

# Apenas Nginx
docker-compose logs -f nginx
```

### **Verificar Status**

```bash
docker-compose ps
```

### **Monitorar Recursos**

```bash
docker stats
```

### **Configurar Monitoramento (Opcional)**

Recomendado: Sentry, New Relic ou DataDog

```bash
# Adicionar no .env
SENTRY_DSN=https://...@sentry.io/...
```

---

## 💾 Backup e Recuperação

### **1. Backup Automático do Banco**

Crie script de backup:

```bash
nano /opt/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/postgres"
mkdir -p $BACKUP_DIR

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_FILE="$BACKUP_DIR/backup_$TIMESTAMP.sql"

docker-compose exec -T db pg_dump -U postgres gestao_negocios > $BACKUP_FILE

# Manter apenas últimos 7 dias
find $BACKUP_DIR -type f -name "*.sql" -mtime +7 -delete

echo "Backup criado: $BACKUP_FILE"
```

```bash
chmod +x /opt/backup_db.sh
```

### **2. Agendar Backup Diário**

```bash
crontab -e
```

Adicione:
```
0 2 * * * /opt/backup_db.sh >> /var/log/backup_db.log 2>&1
```

### **3. Backup de Mídia e Estáticos**

```bash
#!/bin/bash
BACKUP_DIR="/opt/backups/media"
mkdir -p $BACKUP_DIR

TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

tar -czf "$BACKUP_DIR/media_$TIMESTAMP.tar.gz" /opt/axio_gestto/media/
find $BACKUP_DIR -type f -name "*.tar.gz" -mtime +30 -delete
```

### **4. Restaurar Backup**

```bash
# Restaurar banco
docker-compose exec -T db psql -U postgres gestao_negocios < backup_YYYYMMDD.sql

# Restaurar mídia
cd /opt/axio_gestto
tar -xzf /opt/backups/media/media_YYYYMMDD.tar.gz
```

---

## 🧪 Testes Pós-Deploy

### **1. Testar APIs Django**

```bash
# Health check
curl https://axiogestto.com/health/

# API n8n - Profissionais
curl -X GET "https://axiogestto.com/api/n8n/profissionais/?empresa_id=1" \
  -H "apikey: <N8N_API_KEY>"

# API n8n - Serviços
curl -X GET "https://axiogestto.com/api/n8n/servicos/?empresa_id=1" \
  -H "apikey: <N8N_API_KEY>"
```

### **2. Testar Webhook Intermediário**

```bash
curl -X POST "https://axiogestto.com/api/webhooks/whatsapp-n8n/1/teste123/" \
  -H "Content-Type: application/json" \
  -d '{
    "instance": "teste",
    "data": {
      "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
      "pushName": "Teste",
      "message": {"conversation": "teste"}
    }
  }'
```

### **3. Testar Integração Completa**

Ver: `docs/QUICK_START_N8N.md` ou executar:

```bash
python scripts/testar_integracao_n8n.py
```

---

## ⚠️ Troubleshooting

### **Problema: Containers não iniciam**

```bash
# Ver logs
docker-compose logs web

# Verificar portas
netstat -tulpn | grep :80
netstat -tulpn | grep :443

# Verificar .env
cat .env | grep -v "^#"
```

### **Problema: "502 Bad Gateway"**

```bash
# Verificar se Django está UP
docker-compose exec web curl http://localhost:8000/health/

# Reiniciar containers
docker-compose restart web nginx
```

### **Problema: Banco não conecta**

```bash
# Verificar se PostgreSQL está rodando
docker-compose exec db pg_isready -U postgres

# Testar conexão manualmente
docker-compose exec db psql -U postgres -d gestao_negocios
```

### **Problema: n8n não recebe webhooks**

```bash
# Verificar N8N_WEBHOOK_URL
docker-compose exec web python manage.py shell
>>> from django.conf import settings
>>> print(settings.N8N_WEBHOOK_URL)

# Testar n8n diretamente
curl https://seu-n8n.com/webhook/bot-universal
```

---

## 📋 Checklist Final de Deploy

### **Antes do Deploy:**
- [ ] `.env` configurado com valores de produção
- [ ] Tokens seguros gerados
- [ ] Domínio apontando para o servidor
- [ ] n8n instalado e configurado
- [ ] Evolution API configurada
- [ ] OpenAI API Key com créditos

### **Durante o Deploy:**
- [ ] Script `deploy.sh` executado com sucesso
- [ ] Todos os containers UP e healthy
- [ ] Migrações aplicadas
- [ ] Superuser criado
- [ ] Arquivos estáticos coletados

### **Após o Deploy:**
- [ ] Health check retorna 200
- [ ] Admin Django acessível
- [ ] APIs n8n retornam dados
- [ ] Webhook intermediário funciona
- [ ] Template n8n importado e ativo
- [ ] SSL/HTTPS funcionando
- [ ] Backup automático configurado

### **Testes:**
- [ ] Criar empresa de teste
- [ ] Criar profissional e serviço
- [ ] Criar instância WhatsApp
- [ ] Enviar mensagem de teste
- [ ] Bot responde corretamente
- [ ] Agendamento é criado

---

## 🎉 Deploy Concluído!

Se todos os itens do checklist estão ✅, seu sistema está em produção!

### **Próximos Passos:**

1. Configure monitoramento (Sentry, New Relic)
2. Configure backup automático em nuvem
3. Documente acessos e credenciais
4. Treine equipe no sistema
5. Monitore logs diariamente

### **Suporte:**

- Documentação: `docs/`
- Testes: `docs/TESTE_INTEGRACAO_N8N.md`
- Quick Start: `docs/QUICK_START_N8N.md`

---

**Última atualização:** Dezembro 2025
**Versão:** 2.0.0 (com integração n8n)
