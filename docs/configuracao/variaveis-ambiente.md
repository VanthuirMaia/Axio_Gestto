# 📋 Estrutura de Arquivos .env

## 🎯 Arquivos Essenciais

Após limpeza e unificação, o projeto mantém apenas **3 arquivos** relacionados a variáveis de ambiente:

```
.env.dev              # Template de desenvolvimento (NÃO commitar)
.env.prod.example     # Template de produção (OK commitar)
.env                  # Arquivo ativo (NÃO commitar, gerado automaticamente)
```

---

## 📁 Descrição dos Arquivos

### 1. `.env.dev` - Desenvolvimento

**Status:** ❌ **NÃO COMMITAR** (protegido no `.gitignore`)

**Descrição:**
- Template de variáveis para ambiente de desenvolvimento
- Valores seguros para desenvolvimento local
- SQLite, DEBUG=True, email console

**Uso:**
```bash
# Copiado automaticamente por run_dev.sh/bat
cp .env.dev .env
```

**Características:**
- `DJANGO_ENV=development`
- `DEBUG=True`
- `DB_ENGINE=sqlite3`
- `EMAIL_BACKEND=console`
- `ALLOWED_HOSTS=*` (permissivo)

---

### 2. `.env.prod.example` - Produção (Template)

**Status:** ✅ **OK COMMITAR** (template sem credenciais)

**Descrição:**
- Template documentado para configuração de produção
- Contém todas as variáveis necessárias
- Valores são placeholders (devem ser substituídos)

**Uso:**
```bash
# No servidor de produção
cp .env.prod.example .env.prod
nano .env.prod  # Preencher com credenciais reais
```

**Características:**
- `DJANGO_ENV=production`
- `DEBUG=False`
- `DB_ENGINE=postgresql`
- `EMAIL_BACKEND=smtp`
- `ALLOWED_HOSTS` configurável
- Comentários explicativos

---

### 3. `.env` - Arquivo Ativo

**Status:** ❌ **NÃO COMMITAR** (protegido no `.gitignore`)

**Descrição:**
- Arquivo ativo usado pelo Django
- Gerado automaticamente pelos scripts
- Cópia de `.env.dev` (local) ou `.env.prod` (servidor)

**Geração Automática:**
```bash
# Scripts fazem automaticamente:
run_dev.sh    → cp .env.dev .env
run_prod.sh   → cp .env.prod .env
```

**⚠️ IMPORTANTE:** Nunca edite `.env` diretamente! Edite `.env.dev` ou `.env.prod` e rode o script novamente.

---

## 🗑️ Arquivos Deletados (Redundantes)

Estes arquivos foram **removidos** do projeto:

- ❌ `.env.brevo.example` - Info já em `.env.prod.example`
- ❌ `.env.evolution.example` - Info já em `.env.prod.example`
- ❌ `.env.example` - Substituído por `.env.dev`
- ❌ `.env.production` - Renomeado para `.env.prod`
- ❌ `.env.production.example` - Renomeado para `.env.prod.example`
- ❌ `.env.deploy-rapido` - Arquivo antigo

---

## 🛡️ Proteção no .gitignore

O `.gitignore` protege:

```gitignore
# Arquivos ativos (nunca commitar)
.env
.env.local

# Ambientes específicos (nunca commitar)
.env.dev
.env.prod
.env.staging
.env.test

# Nomenclaturas antigas (manter proteção)
.env.production
.env.production.local
.env.deploy-rapido

# Variações locais (nunca commitar)
.env.*.local
.env.*.backup

# ✅ Permitido commitar (templates sem credenciais):
# - .env.dev.example
# - .env.prod.example
# - .env.example
```

---

## 🔄 Workflow Recomendado

### Desenvolvimento Local

```bash
# 1. Usar script automatizado (recomendado)
./run_dev.sh  # Copia .env.dev → .env automaticamente

# 2. Ou manualmente
cp .env.dev .env
python manage.py runserver
```

### Produção (Servidor)

```bash
# 1. Primeira vez (criar .env.prod)
cp .env.prod.example .env.prod
nano .env.prod  # Preencher credenciais reais

# 2. Usar script automatizado
./run_prod.sh  # Copia .env.prod → .env automaticamente
```

---

## 🔍 Verificação de Segurança

### Verificar se .env está protegido

```bash
git check-ignore -v .env
# Deve mostrar: .gitignore:140:.env    .env

git check-ignore -v .env.dev
# Deve mostrar: .gitignore:144:.env.dev    .env.dev

git check-ignore -v .env.prod
# Deve mostrar: .gitignore:145:.env.prod    .env.prod
```

### Verificar se algum .env foi commitado

```bash
git ls-files | grep "^\.env" | grep -v ".example"
# Não deve retornar nada!
```

---

## 📊 Comparação Antes vs Depois

### ANTES (9 arquivos - confuso)
```
.env
.env.brevo.example
.env.deploy-rapido
.env.dev
.env.evolution.example
.env.example
.env.prod.example
.env.production
.env.production.example
```

### DEPOIS (3 arquivos - limpo)
```
.env                  # Ativo (gerado automaticamente)
.env.dev              # Template dev
.env.prod.example     # Template prod
```

**Redução:** 9 → 3 arquivos (**67% menos arquivos**)

---

## ⚠️ Erros Comuns e Soluções

### Erro: "SECRET_KEY não configurada"

**Causa:** `.env` não existe ou está vazio

**Solução:**
```bash
# Desenvolvimento
cp .env.dev .env

# Produção
cp .env.prod .env
```

### Erro: "DJANGO_ENV não definido"

**Causa:** `.env` não tem `DJANGO_ENV`

**Solução:**
```bash
# Adicione ao .env
echo "DJANGO_ENV=development" >> .env
```

### Erro: Commit rejeitado por conter .env

**Causa:** Tentou commitar arquivo protegido

**Solução:**
```bash
# Remover do staging
git reset .env

# Verificar .gitignore
git check-ignore -v .env
```

---

## 📚 Documentação Relacionada

- **Configuração completa:** `docs/AMBIENTES_DEV_PROD.md`
- **Quick start:** `QUICK_START_AMBIENTES.md`
- **Email (Brevo):** `docs/CONFIGURACAO_EMAIL_BREVO.md`

---

## ✅ Checklist de Verificação

Antes de commitar, verifique:

- [ ] `.env` está no `.gitignore`
- [ ] `.env.dev` está no `.gitignore`
- [ ] `.env.prod` está no `.gitignore`
- [ ] Apenas `.env.prod.example` será commitado
- [ ] Nenhum arquivo `.env*` (sem `.example`) está sendo commitado
- [ ] Credenciais reais estão apenas em `.env.dev` (local)
- [ ] `.env.prod.example` não contém credenciais reais

Comando de verificação:
```bash
git status | grep "\.env" | grep -v ".example"
# Não deve retornar nada!
```

---

**Data:** 28/12/2025
**Status:** ✅ Estrutura limpa e organizada
**Arquivos:** 9 → 3 (redução de 67%)
