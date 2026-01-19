# Como Criar Empresa Manualmente no Admin

## 🐛 Problema Resolvido

Antes havia um bug onde:
- ❌ Empresa criada sem assinatura causava loop infinito
- ❌ Middleware quebrava ao tentar acessar `empresa.assinatura`
- ❌ Não havia opção de criar assinatura junto com a empresa

**Agora está CORRIGIDO:**
- ✅ Middleware trata empresas sem assinatura corretamente
- ✅ Pode criar assinatura junto com a empresa (Inline)
- ✅ Pode criar assinatura depois sem causar loop
- ✅ Lista de empresas mostra status da assinatura

---

## 🎯 Opção 1: Criar Empresa COM Assinatura (RECOMENDADO)

### Passo a passo:

1. **Acesse o Admin**
   - URL: `/admin/empresas/empresa/`
   - Clique em **"Adicionar Empresa"**

2. **Preencha dados da empresa:**
   - Nome
   - CNPJ
   - Email
   - Telefone
   - etc.

3. **Role para baixo até "ASSINATURA"**
   - Você verá um formulário inline para criar a assinatura
   - **Plano:** Escolha (Essencial, Profissional ou Empresarial)
   - **Status:** Escolha "Trial" para período de teste ou "Ativa" para paga
   - **Data de expiração:** Ex: Hoje + 7 dias para trial
   - **Trial ativo:** Marque se for período de teste
   - **Gateway:** Escolha "Manual" (para criação manual)

4. **Salve**
   - Empresa E assinatura criadas juntas ✅

---

## 🎯 Opção 2: Criar Empresa SEM Assinatura (depois adicionar)

### Passo 1: Criar Empresa

1. Acesse `/admin/empresas/empresa/`
2. Clique em **"Adicionar Empresa"**
3. Preencha dados da empresa
4. **NÃO preencha** o formulário de assinatura inline (deixe vazio)
5. Salve

### Passo 2: Adicionar Assinatura Depois

**Método A: Editando a Empresa (MAIS FÁCIL)**
1. Abra a empresa criada
2. Role para baixo até "ASSINATURA"
3. Preencha o formulário inline
4. Salve

**Método B: Criando Assinatura Diretamente**
1. Acesse `/admin/assinaturas/assinatura/`
2. Clique em "Adicionar Assinatura"
3. Selecione a empresa
4. Preencha os dados (veja guia rápido no topo do formulário)
5. Salve

---

## 📋 Exemplo de Dados

### Exemplo Trial (7 dias grátis)

```
EMPRESA:
  Nome: Salão Bela Vida
  CNPJ: 12.345.678/0001-99
  Email: contato@belavida.com
  Telefone: (11) 99999-9999

ASSINATURA:
  Plano: Essencial
  Status: Trial (Teste Grátis)
  Data de expiração: [DATA_HOJE + 7 DIAS]
  Trial ativo: ✓ Marcado
  Gateway: manual
```

### Exemplo Assinatura Paga

```
EMPRESA:
  Nome: Clínica Saúde Mais
  CNPJ: 98.765.432/0001-11
  Email: contato@saudemais.com
  Telefone: (21) 88888-8888

ASSINATURA:
  Plano: Profissional
  Status: Ativa
  Data de expiração: [DATA_HOJE + 30 DIAS]
  Trial ativo: ✗ Desmarcado
  Último pagamento: [DATA_HOJE]
  Próximo vencimento: [DATA_HOJE + 30 DIAS]
  Gateway: manual
```

---

## 🔍 Como Ver Status da Assinatura

Na lista de empresas (`/admin/empresas/empresa/`), você verá uma coluna **"Assinatura"** que mostra:

- ✓ **Verde:** Empresa tem assinatura ativa (trial ou paga)
- ⚠ **Laranja:** Assinatura suspensa/expirada
- ✗ **Vermelho:** Empresa sem assinatura

---

## 🛡️ Proteções Implementadas

### Middleware Corrigido

**Antes:**
```python
# ❌ Causava erro se empresa não tinha assinatura
assinatura = empresa.assinatura  # RelatedObjectDoesNotExist
```

**Depois:**
```python
# ✅ Trata corretamente
try:
    assinatura = empresa.assinatura
except Exception:
    # Empresa sem assinatura - permitir acesso
    return self.get_response(request)
```

### Três Middlewares Corrigidos:

1. **LimitesPlanoMiddleware** (`core/middleware.py:51-63`)
   - Verifica limites do plano
   - Agora: Permite acesso se empresa não tem assinatura

2. **AssinaturaExpiracaoMiddleware** (`core/middleware.py:169-177`)
   - Mostra avisos de expiração
   - Agora: Não mostra avisos se não tem assinatura

3. **UsageTrackingMiddleware** (`core/middleware.py:235-240`)
   - Adiciona headers de debug
   - Agora: Skip se não tem assinatura

---

## ⚠️ Situações Especiais

### Empresa Sem Assinatura

Uma empresa **pode existir sem assinatura** nos seguintes casos:

1. **Admin criou e ainda vai adicionar** → OK, sem problemas
2. **Empresa em processo de onboarding** → OK, vai criar depois
3. **Empresa teste/demonstração** → OK, acesso livre
4. **Assinatura foi cancelada** → Terá assinatura com status "cancelada"

**O sistema permite isso agora!** Não causará mais loop ou erro.

### Assinatura Expirada

Se uma assinatura expirar:
- Status muda automaticamente para "suspensa" ou "expirada"
- Middleware bloqueia ações (criar agendamentos, etc.)
- Admin pode renovar manualmente com action "Renovar por 30 dias"

---

## 🔧 Troubleshooting

### Erro ao criar assinatura depois

**Problema:** Loop infinito ao tentar criar assinatura

**Solução:** ✅ JÁ CORRIGIDO! Middleware agora usa try/except

### Empresa não aparece ao criar assinatura

**Problema:** OneToOneField - empresa já tem assinatura

**Solução:** Edite a empresa existente e use o inline, ou delete a assinatura antiga primeiro

### Middleware bloqueia acesso

**Problema:** Empresa sem assinatura sendo bloqueada

**Solução:** ✅ JÁ CORRIGIDO! Middleware permite acesso se não tem assinatura

---

## 📊 Fluxo Corrigido

```
Criar Empresa Manual
    ↓
[OPÇÃO 1: COM ASSINATURA]
  Preencher inline → Salvar
    ↓
  ✅ Empresa + Assinatura criadas juntas
    ↓
  Sistema funciona normalmente

[OPÇÃO 2: SEM ASSINATURA]
  Não preencher inline → Salvar
    ↓
  ✅ Empresa criada sem assinatura
    ↓
  Middleware: try/except → Permite acesso ✅
    ↓
  Admin pode:
    - Editar empresa e adicionar inline
    - Criar assinatura separadamente
    - Deixar sem assinatura (teste/demo)
    ↓
  ✅ SEM LOOP! SEM ERRO!
```

---

## 📝 Checklist

Ao criar empresa manualmente:

- [ ] Preenchi nome, CNPJ, email, telefone
- [ ] Decidi se vai ter assinatura agora ou depois
- [ ] Se COM assinatura:
  - [ ] Escolhi plano
  - [ ] Defini status (trial/ativa)
  - [ ] Configurei data de expiração
  - [ ] Marquei trial_ativo se for trial
  - [ ] Gateway = "manual"
- [ ] Salvei
- [ ] Verifiquei status na lista (coluna "Assinatura")

---

## 🆘 Suporte

- 📖 Documentação de Assinaturas: `docs/SISTEMA_ASSINATURAS.md`
- 🐛 Reportar Bug: GitHub Issues
- 💬 Contato: suporte@gestto.com.br

---

**Status:** ✅ BUG CORRIGIDO - SISTEMA ESTÁVEL
**Data:** 28/12/2025
