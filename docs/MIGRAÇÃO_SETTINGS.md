# 🔄 Migração do Sistema de Settings

## ⚠️ ATENÇÃO: Leia Antes de Continuar

Este documento descreve como migrar do antigo `config/settings.py` para a nova estrutura modular `config/settings/`.

---

## 📊 Antes vs Depois

### ANTES (Antigo)
```
config/
├── settings.py          # ← Arquivo único com tudo
├── urls.py
└── wsgi.py
```

### DEPOIS (Novo)
```
config/
├── settings/
│   ├── __init__.py      # Detecta ambiente
│   ├── base.py          # Comum a todos
│   ├── dev.py           # Desenvolvimento
│   └── prod.py          # Produção
├── urls.py
└── wsgi.py
```

---

## ✅ Passo a Passo da Migração

### 1. Verificar se a migração já foi feita

```bash
# Se este comando funcionar, a migração JÁ FOI FEITA
ls config/settings/
```

Se você vê `base.py`, `dev.py`, `prod.py` → **Migração já concluída!**

### 2. Backup do arquivo antigo (se existir)

```bash
# Se ainda existe config/settings.py
mv config/settings.py config/settings.py.backup
```

### 3. Verificar se o sistema está funcionando

```bash
# Teste em desenvolvimento
python check_env.py
```

Output esperado:
```
🌍 Ambiente: DEVELOPMENT
✓ DEBUG: True
✓ Database: SQLite
```

---

## 🔧 Resolvendo Conflitos

### Erro: "ModuleNotFoundError: No module named 'config.settings'"

**Causa:** Arquivo antigo conflitando com nova estrutura

**Solução:**
```bash
# 1. Verificar se existe config/settings.py
ls -la config/settings.py

# 2. Se existir, renomeie ou remova
mv config/settings.py config/settings.py.old

# 3. Teste novamente
python check_env.py
```

### Erro: "AttributeError: module 'config.settings' has no attribute '...'"

**Causa:** Import cache do Python

**Solução:**
```bash
# Limpe o cache
find . -type d -name __pycache__ -exec rm -rf {} +
find . -name "*.pyc" -delete

# Ou manualmente
rm -rf config/__pycache__
rm -rf config/settings/__pycache__

# Teste novamente
python manage.py runserver
```

---

## 🎯 Personalizando as Configurações

Se você tinha configurações customizadas no antigo `settings.py`:

### 1. Localize a configuração

Abra o backup:
```bash
cat config/settings.py.backup | grep "SUA_CONFIG"
```

### 2. Decida onde adicionar

- **Comum a todos os ambientes?** → `config/settings/base.py`
- **Apenas em desenvolvimento?** → `config/settings/dev.py`
- **Apenas em produção?** → `config/settings/prod.py`

### 3. Adicione a configuração

Exemplo:
```python
# config/settings/base.py
MINHA_CONFIG_CUSTOM = config('MINHA_CONFIG', default='valor_padrao')
```

---

## 📋 Checklist Pós-Migração

- [ ] Arquivo `config/settings/base.py` existe
- [ ] Arquivo `config/settings/dev.py` existe
- [ ] Arquivo `config/settings/prod.py` existe
- [ ] Arquivo `config/settings/__init__.py` existe
- [ ] Arquivo antigo `config/settings.py` foi removido/renomeado
- [ ] Teste `python check_env.py` funciona
- [ ] Teste `python manage.py runserver` funciona
- [ ] Migrações aplicam sem erros: `python manage.py migrate`
- [ ] Admin acessível: `http://localhost:8000/admin/`

---

## 🆘 Problemas?

### Não consigo rodar o servidor

```bash
# 1. Verifique o ambiente
python check_env.py

# 2. Verifique se há conflitos
ls -la config/settings.py
ls -la config/settings/

# 3. Limpe o cache
find . -type d -name __pycache__ -exec rm -rf {} +

# 4. Tente novamente
python manage.py runserver
```

### Minhas configurações customizadas sumiram

Elas estão no backup:
```bash
# Ver o backup
cat config/settings.py.backup

# Encontrar configuração específica
grep "MINHA_CONFIG" config/settings.py.backup
```

Copie para o arquivo apropriado em `config/settings/`.

---

## ✅ Sucesso!

Se tudo funcionou:

1. **Delete o backup** (opcional):
   ```bash
   rm config/settings.py.backup
   ```

2. **Commite as mudanças**:
   ```bash
   git add config/settings/
   git commit -m "refactor: migrar para settings modular (dev/prod)"
   ```

3. **Continue desenvolvendo normalmente!**
   ```bash
   ./run_dev.sh
   ```

---

**Documentação completa:** `docs/AMBIENTES_DEV_PROD.md`
**Quick Start:** `QUICK_START_AMBIENTES.md`
