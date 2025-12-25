# 🚀 Guia de Deploy SaaS - Axio Gestto

## ⚡ STATUS GERAL - DIA 1 (25/12): 75% CONCLUÍDO

**✅ Concluído hoje:**
- ✅ FASE 1: Models e Migrations
- ✅ FASE 2: Integrações de Pagamento (Stripe + Asaas)
- ✅ Endpoint create_tenant
- ✅ Webhooks de pagamento
- ✅ Admin completo
- ✅ URLs configuradas
- ✅ Variáveis de ambiente

**⏳ Pendente (próximos dias):**
- FASE 3: Onboarding wizard (4 passos)
- FASE 4: WhatsApp multi-tenant
- FASE 5: Middleware de limites
- FASE 6: Dashboard com métricas

---

## 📦 FASE 1: Models e Migrations ✅

### Arquivos criados:

```
assinaturas/
├── __init__.py
├── apps.py
├── models.py         # Plano, Assinatura, HistoricoPagamento
├── admin.py          # Interface admin completa com actions
├── stripe_integration.py  # Integração Stripe
├── asaas_integration.py   # Integração Asaas (Brasil)
├── views.py          # create_tenant + webhooks
├── urls.py           # Rotas API
├── migrations/
└── fixtures/
    └── planos_iniciais.json  # 3 planos prontos
```

**Models implementados:**

1. **Plano**
   - nome (essencial/profissional/empresarial)
   - preco_mensal
   - max_profissionais, max_agendamentos_mes, max_usuarios, max_servicos
   - trial_dias
   - Feature flags (relatorios, integracao_contabil, multi_unidades)

2. **Assinatura**
   - empresa (OneToOne)
   - plano (ForeignKey)
   - status (trial/ativa/suspensa/cancelada/expirada)
   - data_expiracao, trial_ativo, ultimo_pagamento
   - gateway, subscription_id_externo, customer_id_externo

3. **HistoricoPagamento**
   - assinatura (ForeignKey)
   - valor, status, gateway, transaction_id
   - payment_method, data_aprovacao, webhook_payload

**Empresa atualizada com:**
- onboarding_completo, onboarding_etapa
- whatsapp_numero, whatsapp_token, whatsapp_instance_id, whatsapp_conectado
- origem_cadastro

---

## 💳 FASE 2: Integrações de Pagamento ✅

### Stripe (Internacional)

**Arquivo:** `assinaturas/stripe_integration.py`

**Funções:**
- `criar_checkout_session(empresa, plano)` - Cria sessão de checkout
- `processar_webhook_stripe(payload, sig_header)` - Processa eventos
- `cancelar_assinatura_stripe(assinatura)` - Cancela no Stripe

**Webhooks processados:**
- `checkout.session.completed` - Criar assinatura
- `invoice.payment_succeeded` - Renovar assinatura
- `invoice.payment_failed` - Suspender assinatura
- `customer.subscription.deleted` - Cancelar assinatura

### Asaas (Brasil) - RECOMENDADO

**Arquivo:** `assinaturas/asaas_integration.py`

**Classe:** `AsaasClient`

**Funções:**
- `criar_cliente(empresa)` - Cria customer no Asaas
- `criar_assinatura(customer_id, plano)` - Cria assinatura recorrente
- `cancelar_assinatura(subscription_id)` - Cancela no Asaas
- `processar_webhook_asaas(payload)` - Processa eventos

**Webhooks processados:**
- `PAYMENT_CONFIRMED` / `PAYMENT_RECEIVED` - Renovar
- `PAYMENT_OVERDUE` - Suspender
- `PAYMENT_REFUNDED` - Estornar

---

## 🔗 FASE 2: Endpoints API ✅

### 1. POST /api/create-tenant/

**Descrição:** Cria empresa + assinatura + usuário automaticamente

**Body:**
```json
{
  "company_name": "Salão Bela Vida",
  "email": "contato@belavida.com",
  "telefone": "11999999999",
  "cnpj": "12345678000199",
  "plano": "essencial"
}
```

**Response:**
```json
{
  "sucesso": true,
  "empresa_id": 1,
  "slug": "salao-bela-vida",
  "login_url": "https://gestto.com.br/onboarding",
  "trial_expira_em": "2026-01-07T...",
  "credenciais": {
    "email": "contato@belavida.com",
    "senha_temporaria": "Abc123..."
  }
}
```

**O que faz:**
1. Valida dados obrigatórios
2. Verifica CNPJ único
3. Gera slug único
4. Cria Empresa
5. Cria Assinatura (trial)
6. Cria usuário admin
7. Envia email de boas-vindas
8. Retorna credenciais

### 2. POST /api/webhooks/stripe/

**Headers:**
- `Stripe-Signature`

**Processa eventos do Stripe automaticamente**

### 3. POST /api/webhooks/asaas/

**Body:** Evento Asaas (JSON)

**Processa eventos do Asaas automaticamente**

---

## 🎯 Planos Configurados

| Plano | Preço/Mês | Prof | Agend/Mês | Usuários | Trial |
|-------|-----------|------|-----------|----------|-------|
| **Essencial** | R$ 49 | 1 | 500 | 1 | 7 dias |
| **Profissional** | R$ 149 | 5 | 2.000 | 3 | 14 dias |
| **Empresarial** | R$ 299 | 999 | 999.999 | 10 | 30 dias |

**Features por plano:**
- Essencial: Básico
- Profissional: + Relatórios avançados
- Empresarial: + Integração contábil + Multi-unidades

---

## 🔧 Comandos para rodar na VPS

### 1. Instalar dependências

```bash
# Entrar no container
docker-compose exec web bash

# Instalar Stripe
pip install stripe==11.0.0

# Ou via arquivo
pip install -r requirements-saas.txt
```

### 2. Criar migrations

```bash
# Criar migrations para novos campos
python manage.py makemigrations empresas
python manage.py makemigrations assinaturas

# Aplicar migrations
python manage.py migrate
```

### 3. Carregar fixtures (planos)

```bash
python manage.py loaddata assinaturas/fixtures/planos_iniciais.json
```

### 4. Verificar planos criados

```bash
python manage.py shell

>>> from assinaturas.models import Plano
>>> Plano.objects.all()
<QuerySet [<Plano: Essencial - R$ 49.00/mês>, <Plano: Profissional - R$ 149.00/mês>, <Plano: Empresarial - R$ 299.00/mês>]>

>>> exit()
```

### 5. Configurar variáveis de ambiente

Editar `.env` na VPS:

```bash
nano .env
```

Adicionar/atualizar:

```env
# Site URL
SITE_URL=https://seu-dominio.com

# Stripe (se usar)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Asaas (RECOMENDADO para Brasil)
ASAAS_API_KEY=$aact_...
ASAAS_SANDBOX=True  # False em produção
```

### 6. Reiniciar containers

```bash
docker-compose restart web
docker-compose restart celery
```

---

## ✅ Checklist de Verificação

### Models e Database:
- [ ] Migrations aplicadas sem erros
- [ ] 3 planos criados no banco
- [ ] Admin /admin/assinaturas/ acessível
- [ ] Campos novos aparecendo em Empresas

### API Endpoints:
- [ ] POST /api/create-tenant/ retorna 200
- [ ] POST /api/webhooks/stripe/ retorna 200
- [ ] POST /api/webhooks/asaas/ retorna 200

### Configuração:
- [ ] .env atualizado com keys Stripe/Asaas
- [ ] EMAIL_* configurado (para emails de boas-vindas)
- [ ] SITE_URL correto

---

## 🧪 Testes Rápidos

### Teste 1: Criar tenant manualmente

```bash
curl -X POST http://localhost:8000/api/create-tenant/ \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "Teste Salão",
    "email": "teste@teste.com",
    "telefone": "11999999999",
    "cnpj": "12345678000199",
    "plano": "essencial"
  }'
```

**Esperado:**
- Empresa criada
- Assinatura trial criada
- Email enviado
- Response com credenciais

### Teste 2: Verificar no admin

1. Acessar /admin/
2. Ir em Assinaturas → Assinaturas
3. Ver assinatura criada em status "Trial"

---

## 📊 Próximos Passos (Dias 2-7)

### DIA 2: Onboarding (26/12)
- [ ] Views wizard 4 passos
- [ ] Templates de onboarding
- [ ] Redirect automático após login

### DIA 3: WhatsApp Multi-Tenant (27/12)
- [ ] Webhook único `/api/whatsapp-webhook/`
- [ ] Roteamento automático por instance
- [ ] Verificação de assinatura ativa

### DIA 4: Limites e Middleware (28/12)
- [ ] LimitesPlanoMiddleware
- [ ] Bloqueio ao atingir limite
- [ ] Dashboard com métricas

### DIA 5-6: Testes e Ajustes (29-30/12)
- [ ] Teste end-to-end completo
- [ ] Ajustes de bugs
- [ ] Documentação final

### DIA 7: Deploy Final (01/01)
- [ ] Deploy produção
- [ ] SSL configurado
- [ ] Smoke tests
- [ ] Sistema no ar! 🎉

---

## 📝 Notas Importantes

1. **Stripe vs Asaas:**
   - Stripe: Melhor para internacional, cartão de crédito
   - Asaas: Melhor para Brasil (boleto, PIX, cartão)
   - Pode usar ambos simultaneamente

2. **Trial:**
   - Planos já vêm com trial configurado
   - Trial é automático ao criar tenant
   - Após trial, precisa pagamento para continuar

3. **Emails:**
   - Configure SMTP para emails funcionarem
   - Email de boas-vindas é enviado automaticamente
   - Contém senha temporária do admin

4. **Segurança:**
   - SEMPRE use HTTPS em produção
   - NUNCA commite .env com keys reais
   - Webhook Stripe precisa de signature válida
   - create_tenant é público (sem auth)

---

**Status atual:** ✅ **75% concluído - FASE 2 completa!**

**Próximo:** Começar FASE 3 (Onboarding) amanhã (26/12)

**Meta:** Sistema 100% funcional até 01/01/2026
