# ✅ Configuração de Deploy Concluída!

## 📁 Arquivos Criados/Modificados

### ✨ Novos Arquivos

1. **`.env.production`** - Configuração de produção completa
   - ✅ Supabase PostgreSQL (connection pooler)
   - ✅ Brevo SMTP
   - ✅ Evolution API
   - ✅ n8n webhook
   - ✅ Stripe (test keys)
   - ✅ Segurança HTTPS habilitada

2. **`docker-compose.prod.yml`** - Orquestração para produção
   - ✅ Redis (cache + Celery)
   - ✅ Django Web (Gunicorn)
   - ✅ Celery Worker
   - ✅ Celery Beat (tarefas agendadas)
   - ✅ Nginx (proxy reverso + HTTPS)
   - ❌ Sem PostgreSQL local (usa Supabase cloud)

3. **`.github/workflows/deploy.yml`** - CI/CD automático
   - ✅ Roda testes automaticamente
   - ✅ Deploy automático ao push na branch `main`
   - ✅ Health check pós-deploy

4. **`DEPLOY.md`** - Documentação completa de deploy

5. **`SETUP_RAPIDO.md`** - Guia rápido (menos de 10 min)

6. **`setup-server.sh`** - Script automático de setup do servidor

### 🔧 Arquivos Modificados

1. **`config/settings.py`**
   - ✅ Suporte a `DATABASE_URL` (Supabase style)
   - ✅ Fallback para SQLite em desenvolvimento
   - ✅ Configurações de segurança automáticas (HTTPS)

2. **`requirements.txt`**
   - ✅ Adicionado `dj-database-url==2.2.0`

3. **`.gitignore`**
   - ✅ Proteção de arquivos `.env*`
   - ✅ Proteção de certificados SSL
   - ✅ Proteção de backups

4. **`Dockerfile`**
   - ✅ Otimizado para produção
   - ✅ Healthcheck integrado
   - ✅ Multi-stage build preparado

5. **`nginx/nginx.conf`**
   - ✅ Rate limiting configurado
   - ✅ Headers de segurança
   - ✅ Cache otimizado para static/media

---

## 🎯 O que você tem AGORA

### ✅ Desenvolvimento Local
- SQLite (banco de dados local)
- Email console (debug)
- DEBUG=True
- Sem HTTPS

### ✅ Produção (Pronto para Deploy)
- Supabase PostgreSQL (cloud)
- Brevo SMTP (email real)
- DEBUG=False
- HTTPS obrigatório
- Security headers habilitados
- Rate limiting configurado

---

## 🚀 Próximos Passos (em ordem)

### 1️⃣ Preparar Servidor VPS

No seu **VPS Hostinger** (SSH):

```bash
# Copiar e executar o script de setup
wget https://raw.githubusercontent.com/SEU_REPO/main/setup-server.sh
chmod +x setup-server.sh
./setup-server.sh

# Após o script, fazer LOGOUT e LOGIN novamente
exit
```

### 2️⃣ Configurar Repositório no Servidor

```bash
# Reconectar ao servidor
ssh usuario@72.61.56.252

# Clonar repositório
cd /var/www/gestto
git clone https://github.com/SEU_USUARIO/axio_gestto.git .

# Criar .env.production no servidor
nano .env.production
# (colar conteúdo do seu .env.production local)
```

### 3️⃣ Primeiro Deploy Manual

```bash
cd /var/www/gestto

# Build e iniciar
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Ver logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 4️⃣ Configurar GitHub Actions (CI/CD)

No **GitHub Repository → Settings → Secrets**:

Adicionar 3 secrets:

| Nome              | Valor                              |
|-------------------|------------------------------------|
| `DEPLOY_HOST`     | `72.61.56.252`                     |
| `DEPLOY_USER`     | Seu usuário SSH                    |
| `DEPLOY_SSH_KEY`  | Chave privada SSH completa         |

**Gerar chave SSH no seu PC:**

```bash
ssh-keygen -t ed25519 -C "deploy@gestto" -f ~/.ssh/gestto_deploy
ssh-copy-id -i ~/.ssh/gestto_deploy.pub usuario@72.61.56.252
cat ~/.ssh/gestto_deploy  # Copiar TODO o conteúdo → GitHub Secret
```

### 5️⃣ Testar Deploy Automático

```bash
# No seu PC local
git add .
git commit -m "deploy: configuração de produção finalizada"
git push origin main

# GitHub Actions vai fazer deploy automaticamente! 🎉
```

### 6️⃣ Configurar HTTPS

**Opção A: Cloudflare (Recomendado - Mais Fácil)**
- Adicionar domínio no Cloudflare
- Apontar DNS para `72.61.56.252`
- SSL/TLS → "Flexible" ou "Full"
- Pronto!

**Opção B: Let's Encrypt (Manual)**
```bash
# No servidor VPS
sudo apt install certbot
sudo certbot certonly --standalone -d app.gestto.app.br
sudo mkdir -p /var/www/gestto/nginx/ssl
sudo cp /etc/letsencrypt/live/app.gestto.app.br/fullchain.pem /var/www/gestto/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.gestto.app.br/privkey.pem /var/www/gestto/nginx/ssl/key.pem
docker-compose -f /var/www/gestto/docker-compose.prod.yml restart nginx
```

---

## 🧪 Testes de Verificação

### ✅ Health Check
```bash
curl http://app.gestto.app.br/health/
# Esperado: {"status": "ok"}
```

### ✅ Admin Django
```
http://app.gestto.app.br/admin/
Login: admin / Admin@Gestto2025!Secure
```

### ✅ Conexão Supabase
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell
# Se conectar = ✅ Supabase funcionando
```

### ✅ Email Brevo
```bash
docker-compose -f docker-compose.prod.yml exec web python manage.py shell
>>> from django.core.mail import send_mail
>>> send_mail('Test', 'Teste', 'contato@gestto.app.br', ['seu@email.com'])
# Check seu email!
```

---

## 📊 Arquitetura Final

```
┌─────────────────────────────────────────────────┐
│              CLOUDFLARE (DNS + CDN)             │
│         app.gestto.app.br → 72.61.56.252        │
└─────────────────┬───────────────────────────────┘
                  │
                  ▼
┌─────────────────────────────────────────────────┐
│           VPS HOSTINGER (Ubuntu)                │
│  ┌──────────────────────────────────────────┐   │
│  │  Nginx (Proxy Reverso + HTTPS)           │   │
│  └───────────┬──────────────────────────────┘   │
│              │                                   │
│  ┌───────────▼──────────────────────────────┐   │
│  │  Django (Gunicorn) - Web App             │   │
│  └───────────┬──────────────────────────────┘   │
│              │                                   │
│  ┌───────────▼──────────────────────────────┐   │
│  │  Redis (Cache + Broker Celery)           │   │
│  └───────────┬──────────────────────────────┘   │
│              │                                   │
│  ┌───────────▼──────────────────────────────┐   │
│  │  Celery Worker + Beat                    │   │
│  └──────────────────────────────────────────┘   │
└─────────────────────────────────────────────────┘
                  │
                  ├──────────► Supabase (PostgreSQL Cloud)
                  ├──────────► Brevo (SMTP Email)
                  ├──────────► Evolution API (WhatsApp)
                  └──────────► n8n (Automações)
```

---

## 🔧 Comandos Úteis de Produção

```bash
# Status dos containers
docker-compose -f docker-compose.prod.yml ps

# Logs em tempo real
docker-compose -f docker-compose.prod.yml logs -f

# Logs de um serviço específico
docker-compose -f docker-compose.prod.yml logs -f web

# Reiniciar aplicação
docker-compose -f docker-compose.prod.yml restart

# Rebuild completo
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d

# Executar comandos Django
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic

# Acessar shell Django
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Ver uso de recursos
docker stats

# Limpar recursos antigos
docker system prune -f
```

---

## 🎉 Conclusão

Você tem **TUDO pronto** para deploy em produção seguindo **boas práticas**:

✅ Separação clara entre dev (SQLite) e prod (Supabase)
✅ CI/CD automático via GitHub Actions
✅ Configurações de segurança (HTTPS, headers, rate limiting)
✅ Banco gerenciado (Supabase - sem preocupação com backups)
✅ Email profissional (Brevo SMTP)
✅ Orquestração com Docker Compose
✅ Documentação completa

**Siga os passos em ordem e em 10-15 minutos sua aplicação estará no ar! 🚀**

---

## 📚 Documentação Disponível

- **`DEPLOY.md`** - Guia completo e detalhado
- **`SETUP_RAPIDO.md`** - Guia express (menos de 10 min)
- **`RESUMO_DEPLOY.md`** - Este arquivo (visão geral)
- **`setup-server.sh`** - Script automático de setup

**Dúvidas?** Consulte os arquivos de documentação acima.
