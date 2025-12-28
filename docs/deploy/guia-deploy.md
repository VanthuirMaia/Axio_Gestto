# 🚀 Guia de Deploy - Gestto em Produção

Documentação completa para deploy do **Gestto** em produção no VPS Hostinger + Supabase + Brevo.

---

## 📋 Pré-requisitos

### 1️⃣ Infraestrutura Necessária

- ✅ **VPS Hostinger** (Ubuntu 20.04+)
  - IP: `72.61.56.252`
  - Usuário SSH com permissões sudo

- ✅ **Supabase (PostgreSQL Cloud)**
  - Connection String já configurada
  - Connection Pooler habilitado (porta 6543)

- ✅ **Brevo (SMTP Email)**
  - SMTP configurado: `smtp-relay.brevo.com`
  - Credenciais já obtidas

- ✅ **Domínio configurado**
  - `app.gestto.app.br` → IP do VPS
  - `gestto.app.br` → IP do VPS
  - Certificado SSL (Let's Encrypt ou Cloudflare)

---

## 🔧 Configuração Inicial do Servidor VPS

### 1. Acessar o servidor via SSH

```bash
ssh usuario@72.61.56.252
```

### 2. Atualizar sistema e instalar dependências

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget build-essential
```

### 3. Instalar Docker e Docker Compose

```bash
# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER

# Instalar Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker --version
docker-compose --version
```

### 4. Clonar o repositório

```bash
# Criar diretório para o projeto
sudo mkdir -p /var/www/gestto
sudo chown -R $USER:$USER /var/www/gestto

# Clonar repositório
cd /var/www/gestto
git clone https://github.com/SEU_USUARIO/SEU_REPO.git .
```

### 5. Criar arquivo `.env.production` no servidor

```bash
cd /var/www/gestto
nano .env.production
```

**Cole o conteúdo do `.env.production` local** (que já está configurado com Supabase, Brevo, etc.)

---

## 🔐 Configurar GitHub Secrets (para CI/CD)

Vá em: **GitHub Repository → Settings → Secrets and variables → Actions**

Adicione os seguintes secrets:

| Secret Name       | Valor                              | Descrição                          |
|-------------------|------------------------------------|------------------------------------|
| `DEPLOY_HOST`     | `72.61.56.252`                     | IP do servidor VPS                 |
| `DEPLOY_USER`     | `seu_usuario_ssh`                  | Usuário SSH do servidor            |
| `DEPLOY_SSH_KEY`  | Conteúdo da chave privada SSH      | Chave privada para autenticação    |

### Como gerar chave SSH (se não tiver)

**No seu computador local:**

```bash
ssh-keygen -t ed25519 -C "deploy@gestto"
# Salvar em: ~/.ssh/gestto_deploy
```

**Copiar chave pública para o servidor:**

```bash
ssh-copy-id -i ~/.ssh/gestto_deploy.pub usuario@72.61.56.252
```

**Adicionar chave privada no GitHub:**

```bash
cat ~/.ssh/gestto_deploy
# Copiar TODO o conteúdo e colar no GitHub Secret DEPLOY_SSH_KEY
```

---

## 🐳 Primeiro Deploy Manual

Execute no servidor VPS:

```bash
cd /var/www/gestto

# Build inicial dos containers
docker-compose -f docker-compose.prod.yml build

# Subir containers
docker-compose -f docker-compose.prod.yml up -d

# Verificar logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Comandos úteis:

```bash
# Ver status dos containers
docker-compose -f docker-compose.prod.yml ps

# Ver logs de um serviço específico
docker-compose -f docker-compose.prod.yml logs -f web

# Executar migrations manualmente
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Criar superuser manualmente
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Reiniciar todos os serviços
docker-compose -f docker-compose.prod.yml restart

# Parar todos os serviços
docker-compose -f docker-compose.prod.yml down

# Rebuild completo
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

---

## 🚀 Deploy Automático via CI/CD

Após configurar GitHub Secrets, **qualquer commit na branch `main` dispara deploy automático!**

### Como fazer deploy:

```bash
# 1. Fazer suas alterações localmente
git add .
git commit -m "feat: nova funcionalidade"

# 2. Enviar para o GitHub
git push origin main

# 3. GitHub Actions faz o resto automaticamente! 🎉
```

### Acompanhar o deploy:

1. Acesse: **GitHub → Actions**
2. Veja o workflow "Deploy to Production" rodando
3. Aguarde conclusão (verde ✅ = sucesso)

---

## 🔒 Configurar Certificado SSL (HTTPS)

### Opção 1: Cloudflare (Recomendado - Mais Fácil)

1. Adicionar domínio no Cloudflare
2. Apontar DNS para o IP do VPS
3. Habilitar SSL/TLS "Full (strict)" ou "Flexible"
4. Cloudflare gerencia automaticamente os certificados

### Opção 2: Let's Encrypt (Certbot)

```bash
# Instalar Certbot
sudo apt install -y certbot python3-certbot-nginx

# Gerar certificado
sudo certbot certonly --standalone -d app.gestto.app.br -d gestto.app.br

# Certificados serão salvos em:
# /etc/letsencrypt/live/app.gestto.app.br/fullchain.pem
# /etc/letsencrypt/live/app.gestto.app.br/privkey.pem

# Copiar para o diretório do Nginx
sudo mkdir -p /var/www/gestto/nginx/ssl
sudo cp /etc/letsencrypt/live/app.gestto.app.br/fullchain.pem /var/www/gestto/nginx/ssl/cert.pem
sudo cp /etc/letsencrypt/live/app.gestto.app.br/privkey.pem /var/www/gestto/nginx/ssl/key.pem

# Reiniciar Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

**Renovação automática:**

```bash
# Adicionar cronjob para renovar automaticamente
sudo crontab -e

# Adicionar esta linha:
0 3 * * * certbot renew --quiet && docker-compose -f /var/www/gestto/docker-compose.prod.yml restart nginx
```

---

## 🧪 Testar Aplicação

### 1. Health Check

```bash
curl https://app.gestto.app.br/health/
# Deve retornar: {"status": "ok"}
```

### 2. Acessar Admin Django

```
https://app.gestto.app.br/admin/
```

**Credenciais (definidas em `.env.production`):**
- Usuário: `admin`
- Email: `contato@gestto.app.br`
- Senha: `Admin@Gestto2025!Secure`

### 3. Testar API do Bot

```bash
curl -X POST https://app.gestto.app.br/api/bot/processar/ \
  -H "X-API-Key: SEU_N8N_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"mensagem": "Olá", "telefone": "11999999999"}'
```

---

## 📊 Monitoramento e Logs

### Ver logs em tempo real:

```bash
# Todos os serviços
docker-compose -f docker-compose.prod.yml logs -f

# Apenas Django
docker-compose -f docker-compose.prod.yml logs -f web

# Apenas Celery
docker-compose -f docker-compose.prod.yml logs -f celery

# Apenas Nginx
docker-compose -f docker-compose.prod.yml logs -f nginx
```

### Monitorar recursos do servidor:

```bash
# CPU e memória
docker stats

# Espaço em disco
df -h

# Verificar containers rodando
docker ps
```

---

## 🛠️ Troubleshooting

### Problema: Container não inicia

```bash
# Ver logs detalhados
docker-compose -f docker-compose.prod.yml logs web

# Reconstruir container
docker-compose -f docker-compose.prod.yml build --no-cache web
docker-compose -f docker-compose.prod.yml up -d
```

### Problema: Migrations não rodam

```bash
# Executar manualmente
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --fake-initial
```

### Problema: Erro 502 Bad Gateway

```bash
# Verificar se Django está respondendo
docker-compose -f docker-compose.prod.yml exec web curl http://localhost:8000/health/

# Reiniciar web + nginx
docker-compose -f docker-compose.prod.yml restart web nginx
```

### Problema: Banco de dados não conecta

```bash
# Testar conexão com Supabase
docker-compose -f docker-compose.prod.yml exec web python manage.py dbshell

# Verificar variáveis de ambiente
docker-compose -f docker-compose.prod.yml exec web env | grep DB_
```

---

## 🔄 Backup e Restore

### Backup do Supabase (PostgreSQL)

O Supabase já faz backups automáticos, mas você pode fazer backups manuais:

```bash
# Backup via pg_dump (acesse Supabase Dashboard → Database → Backups)
# Ou use a CLI do Supabase:
supabase db dump -f backup.sql
```

### Backup dos arquivos de mídia

```bash
# Criar backup dos volumes Docker
docker run --rm \
  -v gestto_media_volume:/data \
  -v $(pwd):/backup \
  alpine tar czf /backup/media-backup-$(date +%Y%m%d).tar.gz /data
```

---

## 📝 Checklist Pós-Deploy

- [ ] ✅ Aplicação acessível via HTTPS
- [ ] ✅ Health check retorna `{"status": "ok"}`
- [ ] ✅ Admin Django acessível
- [ ] ✅ Emails sendo enviados (teste de recuperação de senha)
- [ ] ✅ API do bot funcionando
- [ ] ✅ Integração n8n ativa
- [ ] ✅ Webhooks Evolution API configurados
- [ ] ✅ Celery processando tarefas
- [ ] ✅ Logs sem erros críticos
- [ ] ✅ Certificado SSL válido
- [ ] ✅ DNS apontando corretamente

---

## 🎯 Próximos Passos

1. **Configurar domínio personalizado** (se ainda não estiver)
2. **Ativar Cloudflare** para proteção DDoS e CDN
3. **Configurar monitoramento** (Sentry, UptimeRobot, etc.)
4. **Configurar backups automáticos** dos volumes Docker
5. **Adicionar testes automatizados** no CI/CD
6. **Configurar rate limiting** no Nginx

---

## 📞 Suporte

- **Documentação Django:** https://docs.djangoproject.com
- **Documentação Supabase:** https://supabase.com/docs
- **Documentação Docker:** https://docs.docker.com

---

**🎉 Deploy concluído! Sua aplicação está no ar em produção!**
