# ⚡ Quick Start - Ambientes Dev/Prod

## 🚀 Desenvolvimento (Local)

```bash
# Windows
run_dev.bat

# Linux/Mac
./run_dev.sh
```

Acesse: `http://localhost:8000`

---

## 🔒 Produção (Servidor)

### Primeira vez:

```bash
# 1. Copie o template
cp .env.prod.example .env.prod

# 2. Edite com suas credenciais
nano .env.prod

# 3. Configure variáveis críticas:
#    - SECRET_KEY (gere nova)
#    - DEBUG=False
#    - ALLOWED_HOSTS=seudominio.com
#    - DATABASE_URL ou DB_* (PostgreSQL)
#    - EMAIL_* (SMTP real)
#    - REDIS_URL

# 4. Rode
./run_prod.sh
```

### Gerar SECRET_KEY segura:

```bash
python -c "import secrets; print(''.join(secrets.choice('abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)') for i in range(50)))"
```

---

## 🔍 Verificar Ambiente

```bash
python check_env.py
```

---

## 📋 Comandos Essenciais

```bash
# Aplicar migrações
python manage.py migrate

# Coletar estáticos
python manage.py collectstatic

# Criar superusuário
python manage.py createsuperuser

# Validar produção
DJANGO_ENV=production python manage.py check --deploy
```

---

## ⚠️ IMPORTANTE

### ✅ FAÇA
- Use `.env.dev` localmente
- Use `.env.prod` no servidor
- Rode `python check_env.py` para verificar
- Use scripts `run_dev.*` e `run_prod.sh`

### ❌ NÃO FAÇA
- Commitar `.env.dev` ou `.env.prod` no Git
- Usar `DEBUG=True` em produção
- Usar SQLite em produção
- Usar `runserver` em produção (use Gunicorn)

---

## 🆘 Problemas?

```bash
# Ver ambiente ativo
python check_env.py

# Ver logs
tail -f logs/django.log

# Validar segurança
DJANGO_ENV=production python manage.py check --deploy
```

---

Documentação completa: `docs/AMBIENTES_DEV_PROD.md`
