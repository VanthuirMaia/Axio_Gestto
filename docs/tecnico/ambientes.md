# 🔄 Sistema de Ambientes - Desenvolvimento e Produção

## 📋 Visão Geral

Este documento descreve a estrutura profissional de separação de ambientes implementada no projeto Gestto.

O sistema permite que você trabalhe com:
- **Desenvolvimento** (local, seguro para testes)
- **Produção** (servidor, otimizado e seguro)
- **Staging** (opcional, para testes pré-produção)

---

## 🏗️ Arquitetura

### Estrutura de Arquivos

```
axio_gestto/
├── config/
│   ├── settings/
│   │   ├── __init__.py      # Detecta ambiente automaticamente
│   │   ├── base.py          # Configurações comuns
│   │   ├── dev.py           # Específico de desenvolvimento
│   │   └── prod.py          # Específico de produção
│   ├── urls.py
│   └── wsgi.py
├── .env.dev                 # Variáveis de desenvolvimento
├── .env.prod.example        # Template para produção
├── .env.prod                # Variáveis de produção (NÃO commitar!)
├── run_dev.sh               # Script para rodar em dev (Linux/Mac)
├── run_dev.bat              # Script para rodar em dev (Windows)
├── run_prod.sh              # Script para rodar em prod (Linux/Mac)
└── check_env.py             # Verifica qual ambiente está ativo
```

---

## 🔧 Como Funciona

### 1. Detecção Automática de Ambiente

O sistema usa a variável de ambiente `DJANGO_ENV` para determinar qual configuração carregar:

```python
# config/settings/__init__.py
DJANGO_ENV = os.environ.get('DJANGO_ENV', 'development')

if DJANGO_ENV == 'production':
    from .prod import *
else:
    from .dev import *
```

### 2. Configurações por Ambiente

#### `base.py` - Configurações Comuns
- Apps instalados
- Middleware
- Templates
- Autenticação
- Configurações de SaaS (Stripe, Asaas, etc)

#### `dev.py` - Desenvolvimento
```python
DEBUG = True
DATABASES = {'default': {'ENGINE': 'sqlite3', ...}}
EMAIL_BACKEND = 'console.EmailBackend'
ALLOWED_HOSTS = ['*']
CACHES = {'locmem'}  # Cache em memória
SECURE_SSL_REDIRECT = False
```

#### `prod.py` - Produção
```python
DEBUG = False
DATABASES = {'default': {'ENGINE': 'postgresql', ...}}
EMAIL_BACKEND = 'smtp.EmailBackend'
ALLOWED_HOSTS = ['seudominio.com']
CACHES = {'redis'}  # Cache Redis
SECURE_SSL_REDIRECT = True
HSTS = True
Session/CSRF Cookies Secure = True
```

---

## 🚀 Usando em Desenvolvimento

### Opção 1: Scripts Automatizados (Recomendado)

**Windows:**
```bash
run_dev.bat
```

**Linux/Mac:**
```bash
./run_dev.sh
```

O script automaticamente:
1. Define `DJANGO_ENV=development`
2. Copia `.env.dev` para `.env`
3. Ativa o ambiente virtual
4. Aplica migrações
5. Coleta arquivos estáticos
6. Inicia o servidor em `http://localhost:8000`

### Opção 2: Manual

```bash
# 1. Ativar ambiente virtual
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# 2. Definir ambiente
export DJANGO_ENV=development  # Linux/Mac
set DJANGO_ENV=development     # Windows

# 3. Copiar variáveis
cp .env.dev .env               # Linux/Mac
copy .env.dev .env             # Windows

# 4. Rodar servidor
python manage.py runserver
```

### Verificar Ambiente

```bash
python check_env.py
```

Output esperado:
```
╔════════════════════════════════════════════════════════════╗
║   🚀 AMBIENTE DE DESENVOLVIMENTO ATIVO                     ║
║   ✓ DEBUG: Ativado                                         ║
║   ✓ Database: SQLite (local)                               ║
║   ✓ Email: Console Backend                                 ║
╚════════════════════════════════════════════════════════════╝
```

---

## 🔒 Usando em Produção

### Pré-requisitos

1. **PostgreSQL instalado e configurado**
2. **Redis instalado** (para cache e Celery)
3. **Nginx configurado** (proxy reverso)
4. **Certificado SSL** válido
5. **Gunicorn instalado**: `pip install gunicorn`

### Configuração Inicial

#### 1. Criar arquivo `.env.prod`

```bash
# Copie o template
cp .env.prod.example .env.prod

# Edite com suas credenciais reais
nano .env.prod  # ou seu editor preferido
```

**Variáveis CRÍTICAS a configurar:**
```bash
DJANGO_ENV=production
SECRET_KEY=<gere-uma-chave-segura>
DEBUG=False
ALLOWED_HOSTS=seudominio.com,www.seudominio.com

# Database
DATABASE_URL=postgresql://user:password@host:5432/dbname

# Email
EMAIL_HOST=smtp-relay.brevo.com
EMAIL_HOST_USER=seu-email@seudominio.com
EMAIL_HOST_PASSWORD=<sua-senha-brevo>

# Redis
REDIS_URL=redis://localhost:6379/0

# Site
SITE_URL=https://seudominio.com
```

#### 2. Gerar SECRET_KEY Segura

```bash
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))"
```

#### 3. Iniciar em Produção

**Usando script (recomendado):**
```bash
./run_prod.sh
```

O script automaticamente:
1. Verifica se `.env.prod` existe
2. Valida SECRET_KEY e DEBUG
3. Aplica migrações
4. Coleta arquivos estáticos
5. Inicia Gunicorn com 4 workers

**Manual:**
```bash
# 1. Definir ambiente
export DJANGO_ENV=production

# 2. Copiar variáveis
cp .env.prod .env

# 3. Aplicar migrações
python manage.py migrate

# 4. Coletar estáticos
python manage.py collectstatic --noinput

# 5. Rodar com Gunicorn
gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 4 \
    --timeout 120 \
    --access-logfile logs/access.log \
    --error-logfile logs/error.log
```

---

## 📊 Diferenças entre Ambientes

| Recurso | Desenvolvimento | Produção |
|---------|----------------|----------|
| **DEBUG** | ✅ True | ❌ False |
| **Banco** | SQLite | PostgreSQL |
| **Email** | Console (fake) | SMTP (real) |
| **Cache** | Local Memory | Redis |
| **HTTPS** | ❌ Opcional | ✅ Obrigatório |
| **HSTS** | ❌ Desativado | ✅ 1 ano |
| **Cookies** | HTTP OK | HTTPS only |
| **Logs** | Console verboso | Arquivo (warnings+) |
| **Celery** | ⚠️ Opcional | ✅ Requerido |
| **Workers** | 1 (runserver) | 4+ (Gunicorn) |

---

## 🛡️ Checklist de Segurança (Produção)

Antes de fazer deploy em produção, certifique-se:

### Configuração
- [ ] `DEBUG=False` no `.env.prod`
- [ ] `SECRET_KEY` alterada e segura (50+ caracteres aleatórios)
- [ ] `ALLOWED_HOSTS` contém apenas seu domínio
- [ ] `.env.prod` NÃO está no Git (verificar `.gitignore`)

### Banco de Dados
- [ ] PostgreSQL configurado e testado
- [ ] Credenciais fortes (usuário/senha)
- [ ] Backups automáticos configurados
- [ ] `CONN_MAX_AGE` configurado (conexões persistentes)

### Email
- [ ] SMTP configurado corretamente (Brevo/Gmail/Zoho)
- [ ] Emails de teste enviados com sucesso
- [ ] `DEFAULT_FROM_EMAIL` configurado

### Servidor
- [ ] HTTPS configurado (certificado SSL válido)
- [ ] Nginx como proxy reverso
- [ ] Gunicorn ou uWSGI configurado
- [ ] Supervisor ou systemd para process management
- [ ] Firewall configurado (apenas portas necessárias)

### Cache e Filas
- [ ] Redis instalado e rodando
- [ ] Celery configurado para tarefas assíncronas
- [ ] Celery Beat para tarefas agendadas

### Monitoramento
- [ ] Logs configurados (`logs/django.log`)
- [ ] Sentry ou similar para tracking de erros
- [ ] Monitoring de uptime
- [ ] Alertas configurados

---

## 🔍 Troubleshooting

### "ModuleNotFoundError: No module named 'config.settings'"

**Causa:** Você ainda tem `config/settings.py` (antigo) conflitando com `config/settings/` (novo)

**Solução:**
```bash
# Remover o antigo
rm config/settings.py

# Ou renomeá-lo
mv config/settings.py config/settings.py.old
```

### "SECRET_KEY não foi configurada corretamente!"

**Causa:** Usando SECRET_KEY padrão do exemplo

**Solução:**
```bash
# Gere uma nova
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))"

# Cole no .env.prod
nano .env.prod
# SECRET_KEY=<cole-aqui>
```

### "DEBUG está True em produção!"

**Causa:** `.env.prod` com `DEBUG=True`

**Solução:**
```bash
# Edite .env.prod
nano .env.prod
# Mude para: DEBUG=False
```

### Banco de dados não conecta

**Causa:** Credenciais erradas ou PostgreSQL não está rodando

**Solução:**
```bash
# Verificar se PostgreSQL está rodando
sudo systemctl status postgresql

# Testar conexão manualmente
psql -h localhost -U usuario -d nome_banco

# Verificar variáveis no .env.prod
cat .env.prod | grep DB_
```

### Emails não são enviados em produção

**Causa:** SMTP mal configurado

**Solução:**
```bash
# Teste manual de email
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Teste',
    'Mensagem de teste',
    'noreply@seudominio.com',
    ['seu-email@gmail.com'],
)

# Verificar logs
tail -f logs/django.log
```

---

## 📚 Comandos Úteis

### Verificar qual ambiente está ativo
```bash
python check_env.py
```

### Rodar em modo específico temporariamente
```bash
# Desenvolvimento
DJANGO_ENV=development python manage.py runserver

# Produção (validação)
DJANGO_ENV=production python manage.py check --deploy
```

### Validar configurações de produção
```bash
DJANGO_ENV=production python manage.py check --deploy
```

### Criar superusuário
```bash
# Desenvolvimento
python manage.py createsuperuser

# Produção (via variáveis)
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@seudominio.com \
DJANGO_SUPERUSER_PASSWORD=senha123 \
python manage.py createsuperuser --noinput
```

### Migrations
```bash
# Criar
python manage.py makemigrations

# Aplicar
python manage.py migrate

# Ver SQL gerado
python manage.py sqlmigrate app_name 0001
```

---

## 🎯 Boas Práticas

### ✅ FAÇA

1. **Use `.env.dev` para desenvolvimento**
   - Valores seguros, sem credenciais reais
   - SQLite para simplicidade

2. **Use `.env.prod` para produção**
   - Credenciais reais e seguras
   - PostgreSQL para robustez

3. **Sempre verifique o ambiente**
   ```bash
   python check_env.py
   ```

4. **Use scripts automatizados**
   ```bash
   ./run_dev.sh  # Desenvolvimento
   ./run_prod.sh # Produção
   ```

5. **Commit apenas os `.example`**
   - `.env.dev` → NUNCA commitar
   - `.env.prod` → NUNCA commitar
   - `.env.prod.example` → OK commitar (sem credenciais)

### ❌ NÃO FAÇA

1. **Não commite `.env.prod`**
   - Contém credenciais sensíveis
   - Já está no `.gitignore`

2. **Não use DEBUG=True em produção**
   - Expõe informações sensíveis
   - Degrada performance

3. **Não use SQLite em produção**
   - Não escala bem
   - Problemas com concorrência
   - Use PostgreSQL

4. **Não use runserver em produção**
   - Não é otimizado
   - Use Gunicorn ou uWSGI

5. **Não ignore avisos de segurança**
   ```bash
   python manage.py check --deploy
   ```

---

## 🆘 Suporte

Se encontrar problemas:

1. **Verifique o ambiente:**
   ```bash
   python check_env.py
   ```

2. **Valide configurações:**
   ```bash
   DJANGO_ENV=production python manage.py check --deploy
   ```

3. **Verifique logs:**
   ```bash
   tail -f logs/django.log
   ```

4. **Teste individualmente:**
   - Banco: `python manage.py dbshell`
   - Email: `python manage.py sendtestemail seu@email.com`
   - Cache: `python manage.py shell` → `from django.core.cache import cache`

---

## 📝 Changelog

### v1.0.0 - 2025-12-28
- ✅ Estrutura de settings modular (base/dev/prod)
- ✅ Arquivos `.env.dev` e `.env.prod.example`
- ✅ Scripts automatizados de inicialização
- ✅ Script de verificação de ambiente
- ✅ `.gitignore` atualizado
- ✅ Documentação completa

---

**Pronto!** Agora você tem um sistema profissional de separação de ambientes. 🚀
