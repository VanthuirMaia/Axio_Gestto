# Quick Start - Deploy Gestto em 15 minutos

## ✅ Checklist de Deploy

### 📋 Pré-requisitos
- [ ] VPS Ubuntu na Hostinger com acesso SSH
- [ ] Domínio apontando para IP da VPS (ou usar IP diretamente)
- [ ] Conta Gmail com senha de app (para envio de emails)

---

## 🚀 Opção 1: Deploy Automatizado (Recomendado)

### 1. Conectar na VPS
```bash
ssh root@SEU_IP_VPS
```

### 2. Baixar código
```bash
cd /home
git clone SEU_REPOSITORIO_GIT axio_gestto
# OU fazer upload via SCP
```

### 3. Executar script de deploy
```bash
cd /home/axio_gestto
chmod +x deploy.sh
sudo bash deploy.sh
```

### 4. Editar .env quando solicitado
```bash
nano .env
```

**Valores obrigatórios para trocar:**
- `SECRET_KEY` - Gerar com: `python3 -c "import secrets; print(secrets.token_urlsafe(50))"`
- `N8N_API_KEY` - Gerar com: `python3 -c "import secrets; print(secrets.token_urlsafe(32))"`
- `ALLOWED_HOSTS` - Colocar seu domínio ou IP
- `DB_PASSWORD` - Senha forte para PostgreSQL
- `EMAIL_HOST_USER` - Seu email Gmail
- `EMAIL_HOST_PASSWORD` - Senha de app do Gmail
- `DJANGO_SUPERUSER_PASSWORD` - Senha do admin

### 5. Continuar deploy
O script automaticamente:
- ✅ Instala Docker e Docker Compose
- ✅ Gera certificados SSL (self-signed para teste)
- ✅ Faz build das imagens
- ✅ Sobe containers
- ✅ Aplica migrações
- ✅ Cria superuser

### 6. Testar
```bash
curl http://SEU_IP/health/
# Deve retornar: {"status": "ok"}
```

---

## 🛠️ Opção 2: Deploy Manual (Passo a Passo)

### Passo 1: Preparar servidor
```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

### Passo 2: Transferir código
```bash
cd /home
# Via Git
git clone SEU_REPO axio_gestto

# OU via SCP (do seu PC)
scp -r D:\Axio\axio_gestto root@SEU_IP:/home/
```

### Passo 3: Configurar .env
```bash
cd /home/axio_gestto
cp .env.example .env
nano .env
```

### Passo 4: SSL (Let's Encrypt)
```bash
# Instalar Certbot
sudo apt install -y certbot

# Gerar certificado
sudo certbot certonly --standalone -d seu-dominio.com --email seu@email.com --agree-tos

# Copiar certificados
sudo mkdir -p nginx/certs
sudo cp /etc/letsencrypt/live/seu-dominio.com/fullchain.pem nginx/certs/cert.pem
sudo cp /etc/letsencrypt/live/seu-dominio.com/privkey.pem nginx/certs/key.pem
```

### Passo 5: Subir containers
```bash
docker-compose build
docker-compose up -d
docker-compose ps  # Verificar status
```

### Passo 6: Migrações e setup
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
docker-compose exec web python manage.py createsuperuser
```

---

## 🔐 Configurar Gmail para SMTP

1. Acessar https://myaccount.google.com/security
2. Ativar **verificação em duas etapas**
3. Gerar **senha de app**:
   - Ir em "Senhas de app"
   - Selecionar "E-mail" e "Outro (nome personalizado)"
   - Digitar "Gestto"
   - Copiar senha de 16 caracteres gerada
4. Colocar no `.env`:
   ```
   EMAIL_HOST_USER=seu-email@gmail.com
   EMAIL_HOST_PASSWORD=senha_16_caracteres_aqui
   ```

---

## 🤖 Configurar n8n

### Opção A: n8n Cloud (n8n.io)

1. Criar conta gratuita em https://n8n.io
2. Criar novo workflow
3. Importar workflows de `/n8n-workflows/`
4. Criar credencial "Gestto API":
   - Tipo: Header Auth
   - Header Name: `X-API-Key`
   - Header Value: [copiar N8N_API_KEY do .env]
5. Atualizar URLs em todos os HTTP Request nodes:
   - `https://seu-dominio.com/api/bot/processar/`
   - `https://seu-dominio.com/api/n8n/servicos/`
   - etc.

### Opção B: n8n Self-Hosted (mesma VPS)

```bash
mkdir -p /home/n8n_data

docker run -d --restart unless-stopped \
  --name n8n \
  -p 5678:5678 \
  -e N8N_BASIC_AUTH_ACTIVE=true \
  -e N8N_BASIC_AUTH_USER=admin \
  -e N8N_BASIC_AUTH_PASSWORD=sua_senha \
  -v /home/n8n_data:/home/node/.n8n \
  n8nio/n8n

# Acessar: http://SEU_IP:5678
```

**IMPORTANTE:** Abrir porta no firewall:
```bash
sudo ufw allow 5678/tcp
```

---

## 📱 Configurar WhatsApp (Evolution API)

### 1. Instalar Evolution API (mesma VPS)

```bash
# Clonar repositório
git clone https://github.com/EvolutionAPI/evolution-api.git /home/evolution-api
cd /home/evolution-api

# Configurar .env
cp .env.example .env
nano .env

# Valores importantes:
# AUTHENTICATION_API_KEY=gerar_token_aqui
# SERVER_URL=http://SEU_IP:8080

# Subir com Docker
docker-compose up -d
```

### 2. Conectar WhatsApp

1. Acessar `http://SEU_IP:8080/manager`
2. Criar nova instância
3. Escanear QR Code com WhatsApp
4. Configurar webhook para n8n:
   - URL: `https://seu-n8n.com/webhook/whatsapp`

---

## 🎯 Configuração Inicial Django Admin

1. Acessar `https://seu-dominio.com/admin/`
2. Login: admin (conforme .env)
3. Configurar sistema:

### ✅ Criar Empresa
- Nome: Sua empresa
- CNPJ, telefone, email
- Logo (opcional)

### ✅ Adicionar Serviços
Exemplos:
- Corte Masculino - R$ 45 - 30min
- Barba - R$ 30 - 20min
- Corte + Barba - R$ 70 - 50min

### ✅ Adicionar Profissionais
- Nome
- Email, telefone
- Selecionar serviços que executa
- Escolher cor para calendário

### ✅ Horários de Funcionamento
- Segunda a Sexta: 09:00 - 19:00
- Sábado: 09:00 - 17:00
- Domingo: Fechado

### ✅ Datas Especiais (Feriados)
- 25/12 - Natal - Fechado
- 01/01 - Ano Novo - Fechado

---

## 🧪 Testar Integração Completa

### 1. Testar APIs manualmente
```bash
# Health check
curl http://SEU_IP/health/

# Listar serviços (substitua TOKEN)
curl -H "X-API-Key: SEU_TOKEN" https://seu-dominio.com/api/n8n/servicos/

# Testar agendamento
curl -X POST https://seu-dominio.com/api/bot/processar/ \
  -H "X-API-Key: SEU_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "5587999887766",
    "mensagem_original": "Teste",
    "intencao": "agendar",
    "dados": {
      "servico": "corte",
      "data": "2025-12-26",
      "hora": "14:00"
    }
  }'
```

### 2. Testar n8n
- Executar workflow manualmente
- Verificar se APIs respondem
- Checar logs

### 3. Testar WhatsApp
- Enviar mensagem: "Quero agendar corte amanhã às 14h"
- Verificar resposta do bot
- Conferir agendamento no admin Django

---

## 📊 Monitoramento

### Ver logs em tempo real
```bash
# Todos os containers
docker-compose logs -f

# Apenas Django
docker-compose logs -f web

# Apenas Celery (tarefas agendadas)
docker-compose logs -f celery
```

### Status dos containers
```bash
docker-compose ps
```

### Estatísticas de uso
```bash
docker stats
```

---

## 🔧 Comandos Úteis

### Reiniciar aplicação
```bash
docker-compose restart web
```

### Reiniciar tudo
```bash
docker-compose restart
```

### Parar tudo
```bash
docker-compose down
```

### Atualizar código (após git pull)
```bash
docker-compose down
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py collectstatic --noinput
```

### Backup do banco
```bash
docker-compose exec db pg_dump -U postgres gestao_negocios > backup.sql
```

### Restaurar backup
```bash
docker-compose exec -T db psql -U postgres gestao_negocios < backup.sql
```

---

## 🆘 Problemas Comuns

### "502 Bad Gateway"
```bash
docker-compose logs web
docker-compose restart web
```

### "Connection refused" ao banco
```bash
docker-compose logs db
# Verificar .env: DB_HOST=db (não localhost!)
```

### n8n não conecta
```bash
# Verificar API Key
cat .env | grep N8N_API_KEY
# Comparar com credencial no n8n (devem ser iguais)
```

### Celery não processa tarefas
```bash
docker-compose logs celery
docker-compose restart celery
```

---

## 📚 Documentação Completa

- **Deploy completo**: `DEPLOY_GUIDE.md`
- **Integração n8n**: `N8N_INTEGRATION.md`
- **Código**: Explorar `/config/`, `/agendamentos/`, etc.

---

## 🎉 Checklist Final

- [ ] Sistema acessível em https://seu-dominio.com/
- [ ] Admin Django funcionando (/admin/)
- [ ] Empresa, serviços e profissionais cadastrados
- [ ] APIs respondendo (testar com curl)
- [ ] n8n conectado e workflows importados
- [ ] WhatsApp conectado via Evolution API
- [ ] Teste completo: enviar mensagem e criar agendamento
- [ ] Logs sem erros críticos
- [ ] Backup automático configurado (cron)
- [ ] Firewall configurado (UFW)
- [ ] SSL válido (Let's Encrypt ou similar)

---

**Pronto! Sistema em produção! 🚀**

Tempo estimado: 15-30 minutos (deploy automatizado) ou 1-2 horas (manual)

---

**Suporte:** Consulte os arquivos de documentação para detalhes técnicos.
