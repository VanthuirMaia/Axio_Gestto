# 🎯 ONDE MEXER - Guia Visual

## 🟢 MEXE AQUI (Configuração da integração Stripe)

### Arquivo 1: `.env` (PRINCIPAL)
**Caminho:** `D:\Axio\axio_gestto\.env`

```env
# Só mexe nestas 4 linhas:
STRIPE_PUBLIC_KEY=pk_test_COLE_SUA_CHAVE_AQUI     ← MEXE AQUI
STRIPE_SECRET_KEY=sk_test_COLE_SUA_CHAVE_AQUI    ← MEXE AQUI
STRIPE_WEBHOOK_SECRET=whsec_COLE_AQUI            ← MEXE AQUI
SITE_URL=http://localhost:8000                   ← MEXE AQUI (quando subir pra produção)
```

**Como pegar as chaves:**
1. https://dashboard.stripe.com/test/apikeys
2. Copiar e colar

**IMPORTANTE:** Se quebrar, é porque:
- ❌ Copiou chave errada
- ❌ Esqueceu de reiniciar servidor após alterar
- ❌ Tem espaço em branco antes/depois da chave

---

### Arquivo 2: Admin Django (atualizar Price IDs)
**Caminho:** `http://localhost:8000/admin/assinaturas/plano/`

**O que fazer:**
1. Criar produtos no Stripe Dashboard
2. Copiar os `price_id` de cada produto
3. Editar cada plano no Admin:
   - Essencial → Campo `stripe_price_id` → Colar price_id
   - Profissional → Campo `stripe_price_id` → Colar price_id
   - Empresarial → Campo `stripe_price_id` → Colar price_id

**IMPORTANTE:** Se quebrar, é porque:
- ❌ Price ID errado (não bate com produto do Stripe)
- ❌ Copiou o Product ID ao invés do Price ID
- ❌ Produto está inativo no Stripe

---

## 🔴 NÃO MEXE AQUI (Funciona sozinho)

### ❌ `assinaturas/stripe_integration.py`
**Por que existe:** Código que conversa com Stripe API
**Quando mexer:** NUNCA (a menos que ache um bug)
**Se quebrar:** Problema é nas chaves do .env, não no código

### ❌ `assinaturas/views.py` (create_tenant, webhooks)
**Por que existe:** Cria clientes automaticamente
**Quando mexer:** NUNCA
**Se quebrar:** Problema é no webhook ou nas chaves

### ❌ `core/middleware.py`
**Por que existe:** Bloqueia clientes quando atingem limites
**Quando mexer:** Só se quiser desativar limites (comentar)
**Se quebrar:** Não quebra, ele só para de funcionar

---

## 🟡 TALVEZ MEXE (Raramente)

### 📄 `assinaturas/models.py` (Plano model)
**Quando mexer:**
- Criar um novo plano diferente (Ex: "Plano Premium" R$ 499)
- Mudar limites de um plano existente

**Como mexer:**
```python
# Django shell
from assinaturas.models import Plano

plano = Plano.objects.get(nome='essencial')
plano.max_agendamentos_mes = 1000  # Aumentar limite
plano.preco_mensal = 59.00         # Mudar preço
plano.save()
```

**IMPORTANTE:** Mudanças afetam só NOVAS assinaturas

---

### 📄 `config/settings.py` (Desativar limites)
**Quando mexer:**
- Se quiser desativar bloqueios por limite

**Como mexer:**
```python
# Linha 45 (aproximadamente)
MIDDLEWARE = [
    # ... outros ...
    'core.middleware.AssinaturaExpiracaoMiddleware',  # Mantém
    # 'core.middleware.LimitesPlanoMiddleware',       # ← Comentar esta linha
    'core.middleware.UsageTrackingMiddleware',
]
```

**Depois:** Reiniciar servidor

---

## 🗺️ Mapa de Arquivos

```
Gestto/
│
├── .env                          🟢 MEXE SEMPRE (chaves Stripe)
│
├── assinaturas/
│   ├── models.py                 🟡 Raramente (mudar limites)
│   ├── stripe_integration.py     🔴 NUNCA MEXE
│   ├── asaas_integration.py      🔴 NUNCA MEXE
│   └── views.py                  🔴 NUNCA MEXE
│
├── core/
│   ├── middleware.py             🟡 Só para desativar limites
│   ├── views.py                  🟢 Dia a dia (dashboard, etc)
│   └── onboarding_views.py       🔴 NUNCA MEXE (funciona sozinho)
│
├── agendamentos/
│   ├── models.py                 🟢 Dia a dia (adicionar campos)
│   ├── views.py                  🟢 Dia a dia (lógica negócio)
│   └── bot_api.py                🟡 Raramente (mudar bot)
│
├── config/
│   ├── settings.py               🟡 Raramente (desativar limites)
│   └── urls.py                   🔴 NUNCA MEXE
│
└── templates/
    ├── dashboard.html            🟢 Dia a dia (visual)
    ├── agendamentos/             🟢 Dia a dia (telas)
    └── onboarding/               🔴 NUNCA MEXE (funciona sozinho)
```

**Legenda:**
- 🟢 **Verde:** Você VAI mexer frequentemente
- 🟡 **Amarelo:** Mexe raramente ou só 1 vez
- 🔴 **Vermelho:** NÃO mexe (funciona sozinho)

---

## 🔧 Fluxo de Correção de Problemas

### 1. Erro ao criar checkout

```
┌─────────────────────┐
│ Deu erro no         │
│ checkout do Stripe? │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Verificar .env:     │
│ - STRIPE_SECRET_KEY │
│ - STRIPE_PUBLIC_KEY │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Verificar Admin:    │
│ - stripe_price_id   │
│ do plano está certo?│
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Reiniciar servidor  │
│ python manage.py    │
│ runserver           │
└─────────────────────┘
```

### 2. Webhook não chegou

```
┌─────────────────────┐
│ Pagamento OK mas    │
│ assinatura não      │
│ ativou?             │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Stripe CLI está     │
│ rodando?            │
│ stripe listen ...   │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ STRIPE_WEBHOOK_     │
│ SECRET está correto │
│ no .env?            │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Ver logs no Admin:  │
│ HistoricoPagamento  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Ativar manualmente  │
│ (script no doc)     │
└─────────────────────┘
```

### 3. Limites bloqueando cliente

```
┌─────────────────────┐
│ Cliente não consegue│
│ criar agendamento?  │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Ver uso atual:      │
│ Admin → Assinaturas │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Opção 1:            │
│ Cliente faz upgrade │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Opção 2:            │
│ Aumentar limite no  │
│ Admin → Planos      │
└──────┬──────────────┘
       │
       ▼
┌─────────────────────┐
│ Opção 3:            │
│ Desativar middleware│
│ de limites          │
└─────────────────────┘
```

---

## 📋 Checklist de Manutenção

### Toda semana:
- [ ] Verificar assinaturas que expiram em 7 dias (Admin)
- [ ] Verificar logs de webhook (HistoricoPagamento)
- [ ] Backup do banco de dados

### Todo mês:
- [ ] Ver quais clientes atingiram 80% do limite
- [ ] Entrar em contato para upgrade
- [ ] Verificar se há pagamentos falhados

### Só quando precisar:
- [ ] Criar novo plano (Admin → Planos → Add)
- [ ] Mudar limites de plano existente
- [ ] Desativar middleware de limites
- [ ] Atualizar chaves Stripe (se mudou conta)

---

## 🎯 Resumão Final

### O que você VAI mexer:
1. **`.env`** - Chaves do Stripe (1 vez)
2. **Admin Django** - Price IDs dos planos (1 vez)
3. **Admin Django** - Gerenciar clientes/assinaturas (dia a dia)

### O que você NUNCA mexe:
1. `assinaturas/stripe_integration.py`
2. `assinaturas/views.py`
3. `core/middleware.py` (exceto para desativar)
4. `core/onboarding_views.py`

### Se algo quebrar:
1. Verificar `.env`
2. Verificar Admin (price_id)
3. Reiniciar servidor
4. Ver logs (HistoricoPagamento)
5. Ativar manualmente se urgente

---

**TOTAL DE ARQUIVOS QUE VOCÊ MEXE: 1 (o .env)**
**TOTAL DE CLIQUES NO ADMIN: 3 (para configurar price_ids)**

**Pronto! Mais simples impossível! 🚀**
