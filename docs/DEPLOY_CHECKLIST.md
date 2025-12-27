# ✅ Checklist de Deploy - Axio Gestto

## 📋 Pré-Deploy

### Servidor
- [ ] Ubuntu 20.04+ ou Debian 11+ instalado
- [ ] Docker instalado (versão 20.10+)
- [ ] Docker Compose instalado (versão 2.0+)
- [ ] Git instalado
- [ ] Usuário não-root com sudo criado
- [ ] Firewall configurado (portas 80, 443, 22)
- [ ] Domínio apontando para IP do servidor

### Serviços Externos
- [ ] Conta Evolution API criada
- [ ] Evolution API Key obtida
- [ ] Conta OpenAI criada (para n8n)
- [ ] OpenAI API Key obtida
- [ ] n8n instalado (VPS ou Cloud)
- [ ] Conta Stripe criada (opcional)
- [ ] Stripe API Keys obtidas (opcional)

### Repositório
- [ ] Código commitado no Git
- [ ] Branch main/master limpa
- [ ] Secrets não commitados
- [ ] `.env.example` atualizado

---

## 🔐 Configuração de Ambiente

### Arquivo .env
- [ ] Copiar `.env.example` para `.env`
- [ ] Gerar nova `SECRET_KEY` segura
- [ ] Definir `DEBUG=False`
- [ ] Configurar `ALLOWED_HOSTS` com domínio
- [ ] Configurar `SITE_URL` com https://seu-dominio.com

### Banco de Dados
- [ ] `DB_NAME` configurado
- [ ] `DB_USER` configurado
- [ ] `DB_PASSWORD` forte definida
- [ ] `DB_HOST=db` (Docker)
- [ ] `DB_PORT=5432`

### Email
- [ ] `EMAIL_BACKEND` configurado
- [ ] `EMAIL_HOST` configurado (smtp.gmail.com)
- [ ] `EMAIL_HOST_USER` configurado
- [ ] `EMAIL_HOST_PASSWORD` configurada (senha de app)
- [ ] `DEFAULT_FROM_EMAIL` configurado

### APIs e Integrações
- [ ] `N8N_API_KEY` gerada e configurada
- [ ] `N8N_WEBHOOK_URL` configurada (https://seu-n8n.com/webhook/bot-universal)
- [ ] `EVOLUTION_API_URL` configurada
- [ ] `EVOLUTION_API_KEY` configurada

### Pagamentos (se aplicável)
- [ ] `STRIPE_PUBLIC_KEY` configurada
- [ ] `STRIPE_SECRET_KEY` configurada
- [ ] `STRIPE_WEBHOOK_SECRET` configurada

### Superusuário
- [ ] `DJANGO_SUPERUSER_USERNAME` definido
- [ ] `DJANGO_SUPERUSER_EMAIL` definido
- [ ] `DJANGO_SUPERUSER_PASSWORD` forte definida

---

## 🐳 Deploy Docker

### Build e Inicialização
- [ ] Clonar repositório no servidor
- [ ] Criar arquivo `.env` com configurações
- [ ] Executar `docker-compose build`
- [ ] Executar `docker-compose up -d`
- [ ] Verificar containers rodando: `docker-compose ps`

### Verificação de Saúde
- [ ] PostgreSQL healthy: `docker-compose ps db`
- [ ] Redis healthy: `docker-compose ps redis`
- [ ] Web healthy: `docker-compose ps web`
- [ ] Celery rodando: `docker-compose ps celery`
- [ ] Nginx rodando: `docker-compose ps nginx`

### Logs
- [ ] Verificar logs web: `docker-compose logs web`
- [ ] Verificar logs celery: `docker-compose logs celery`
- [ ] Sem erros críticos nos logs

---

## 🔧 Configuração n8n

### Importação de Template
- [ ] Acessar n8n (VPS ou Cloud)
- [ ] Importar `TEMPLATE_Bot_Universal_VPS_Simplificado.json`
- [ ] Salvar workflow

### Configuração do Node "⚙️ Configurações + Dados"
- [ ] `config_django_url`: https://seu-dominio.com
- [ ] `config_django_key`: (mesmo da .env N8N_API_KEY)
- [ ] `config_evolution_url`: https://evolution.axiodev.cloud
- [ ] `config_evolution_key`: (mesmo da .env EVOLUTION_API_KEY)
- [ ] `config_openai_key`: sk-proj-...

### Ativação
- [ ] Workflow salvo (Ctrl+S)
- [ ] Workflow ativado (toggle verde)
- [ ] URL do webhook copiada
- [ ] Verificar em Executions se está ativo

---

## 📱 Configuração Evolution API

### Acesso
- [ ] Acessar painel Evolution API
- [ ] Login realizado
- [ ] API Key global configurada

### Primeiro Teste
- [ ] Criar empresa de teste no Gestto
- [ ] Acessar Configurações → WhatsApp
- [ ] Clicar "Criar Nova Instância"
- [ ] QR Code gerado
- [ ] Escanear QR Code
- [ ] Status: Conectado ✅

---

## 🔒 SSL/HTTPS

### Certificado Let's Encrypt
- [ ] Certbot instalado no servidor
- [ ] Domínio validado (A record configurado)
- [ ] Certificado gerado: `certbot certonly --standalone -d seu-dominio.com`
- [ ] Certificado renovação automática configurada

### Nginx
- [ ] Arquivo `nginx/default.conf` atualizado com SSL
- [ ] Certificados montados no docker-compose
- [ ] Nginx reiniciado: `docker-compose restart nginx`
- [ ] Testar HTTPS: https://seu-dominio.com
- [ ] Redirect HTTP → HTTPS funcionando

---

## 🧪 Testes de Integração

### Teste 1: Healthcheck
```bash
curl https://seu-dominio.com/health/
# Esperado: {"status": "ok"}
```
- [ ] ✅ Passou

### Teste 2: API Profissionais
```bash
curl -X GET "https://seu-dominio.com/api/n8n/profissionais/?empresa_id=1" \
  -H "apikey: SUA-N8N-API-KEY" \
  -H "empresa_id: 1"
```
- [ ] ✅ Retornou lista de profissionais

### Teste 3: API Serviços
```bash
curl -X GET "https://seu-dominio.com/api/n8n/servicos/?empresa_id=1" \
  -H "apikey: SUA-N8N-API-KEY" \
  -H "empresa_id: 1"
```
- [ ] ✅ Retornou lista de serviços

### Teste 4: Webhook n8n (Direto)
```bash
curl -X POST "https://seu-n8n.com/webhook/bot-universal" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa_id": 1,
    "instance": "teste",
    "body": {
      "data": {
        "key": {"remoteJid": "5511999999999@s.whatsapp.net"},
        "pushName": "Teste",
        "message": {"conversation": "Oi"}
      }
    }
  }'
```
- [ ] ✅ Retornou 200 OK
- [ ] ✅ Execução aparece no n8n → Executions

### Teste 5: WhatsApp End-to-End
- [ ] Enviar mensagem "Oi" para número da instância
- [ ] Bot responde com saudação da Luna
- [ ] Testar agendamento completo
- [ ] Agendamento criado no banco
- [ ] Confirmação enviada no WhatsApp

---

## 📊 Monitoramento

### Configuração Inicial
- [ ] Sentry configurado (opcional)
- [ ] Log aggregation configurado
- [ ] Uptime monitoring configurado
- [ ] Alertas configurados

### Verificações Diárias
- [ ] `docker-compose ps` - Todos containers UP
- [ ] `docker-compose logs --tail=100 web` - Sem erros
- [ ] Disk space: `df -h` - Menos de 80%
- [ ] Backups rodando automaticamente

---

## 💾 Backup

### Banco de Dados
- [ ] Script de backup PostgreSQL configurado
- [ ] Backup automático diário configurado (cron)
- [ ] Testar restore de backup
- [ ] Backups armazenados externamente (S3, etc.)

### Workflows n8n
- [ ] Backup manual de workflows exportados
- [ ] Versionar workflows no Git
- [ ] Documentar mudanças em workflows

### Arquivos
- [ ] Media files com backup
- [ ] Static files com backup
- [ ] `.env` com backup SEGURO (criptografado)

---

## 🚀 Pós-Deploy

### Documentação
- [ ] Documentar URLs de produção
- [ ] Documentar credenciais (em local seguro)
- [ ] Criar runbook de incidentes
- [ ] Treinar equipe

### Segurança
- [ ] Trocar todas as senhas padrão
- [ ] Revogar acessos desnecessários
- [ ] Configurar 2FA onde possível
- [ ] Revisar logs de acesso

### Performance
- [ ] Testar carga (opcional)
- [ ] Configurar CDN para static files (opcional)
- [ ] Otimizar queries lentas
- [ ] Configurar cache Redis

---

## ⚠️ Rollback Plan

### Em caso de problema:

1. **Reverter código:**
   ```bash
   git checkout <commit-anterior>
   docker-compose down
   docker-compose up -d --build
   ```

2. **Restaurar banco:**
   ```bash
   docker-compose exec db psql -U postgres -d gestao_negocios < backup.sql
   ```

3. **Verificar logs:**
   ```bash
   docker-compose logs --tail=500 web
   ```

4. **Notificar usuários:**
   - [ ] Email comunicando manutenção
   - [ ] Status page atualizada

---

## 📞 Contatos Importantes

- **Suporte Evolution API:** [URL/email]
- **Suporte n8n:** [URL/email]
- **Suporte Stripe:** [URL/email]
- **Equipe DevOps:** [contato]
- **Responsável técnico:** [contato]

---

## ✅ Deploy Completo

- [ ] Todos os itens acima verificados
- [ ] Testes passaram
- [ ] Monitoramento ativo
- [ ] Backup configurado
- [ ] Documentação atualizada
- [ ] Equipe treinada

**Data do Deploy:** ___/___/_______

**Responsável:** _____________________

**Status:** 🎉 **PRODUÇÃO ATIVA**

---

**Última atualização:** Dezembro 2025
