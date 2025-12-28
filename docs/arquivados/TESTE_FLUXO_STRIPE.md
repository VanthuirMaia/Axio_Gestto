# 🧪 Guia de Teste - Fluxo Completo Stripe

## ✅ O que foi implementado:

1. ✅ Views de sucesso/cancelamento criadas
2. ✅ Templates bonitos com animações
3. ✅ Integração checkout no cadastro
4. ✅ Planos atualizados com Price IDs
5. ✅ Webhook secret configurado
6. ✅ Stripe CLI instalado e configurado

---

## 🚀 Como Testar (Passo a Passo)

### 📋 Pré-requisitos

Certifique-se que você tem **3 terminais abertos**:

#### **Terminal 1 - Django Server**
```bash
python manage.py runserver
```

#### **Terminal 2 - Stripe CLI**
```bash
stripe listen --forward-to http://localhost:8000/api/webhooks/stripe/
```

#### **Terminal 3 - Comandos de teste**
Deixe livre para executar comandos.

---

## 🎯 TESTE 1: Cadastro + Checkout Simples

### Passo 1: Acessar Landing Page
```
http://localhost:8000/
```

### Passo 2: Ir em "Começar Grátis" ou "Preços"
```
http://localhost:8000/precos/
```

### Passo 3: Clicar em "Começar Teste Grátis" em qualquer plano

### Passo 4: Preencher formulário de cadastro
```
Nome da Empresa: Salão Teste
Email: teste@exemplo.com
Telefone: 11999999999
Plano: essencial (ou outro)
```

### Passo 5: Clicar em "Cadastrar"

**✅ ESPERADO:**
- Sistema cria empresa
- Sistema redireciona automaticamente para página do Stripe
- Você vê formulário de pagamento do Stripe

### Passo 6: Preencher dados do cartão de teste
```
Número do cartão: 4242 4242 4242 4242
Data de expiração: 12/34 (qualquer data futura)
CVV: 123
Nome no cartão: Teste
CEP: 12345
```

### Passo 7: Clicar em "Assinar"

**✅ ESPERADO:**
- Stripe processa pagamento (teste)
- Redireciona para: `http://localhost:8000/assinatura/sucesso?session_id=cs_test_...`
- Você vê página de sucesso bonita com emoji 🎉

### Passo 8: Verificar logs do Stripe CLI (Terminal 2)

**✅ ESPERADO:**
```
✔️ webhook_id: evt_xxxxx checkout.session.completed [200]
✔️ webhook_id: evt_xxxxx customer.subscription.created [200]
```

### Passo 9: Verificar no Admin Django

Acessar: `http://localhost:8000/admin/`

- **Assinaturas > Assinaturas**
  - Verificar se assinatura foi criada
  - Status deve ser "ativa" (não "trial")
  - `subscription_id_externo` deve estar preenchido

- **Assinaturas > Histórico de Pagamentos**
  - Deve ter registro do pagamento
  - Gateway: stripe
  - Status: succeeded

---

## 🎯 TESTE 2: Cancelamento do Checkout

### Passo 1: Fazer cadastro novamente
Usar email diferente: `teste2@exemplo.com`

### Passo 2: Na página do Stripe, clicar em "← Voltar"

**✅ ESPERADO:**
- Redireciona para: `http://localhost:8000/assinatura/cancelado`
- Você vê página de cancelamento bonita com emoji 😕
- Botão "Tentar Novamente" funciona

---

## 🎯 TESTE 3: Testar Webhook Manualmente

No **Terminal 3**, executar:

```bash
stripe trigger checkout.session.completed
```

**✅ ESPERADO:**
- Terminal 2 mostra: `✔️ webhook_id: evt_xxxxx checkout.session.completed [200]`
- Terminal 1 (Django) mostra logs de processamento

---

## 🎯 TESTE 4: Verificar Email (Console)

Como o email está configurado para console, verificar no **Terminal 1** (Django):

**✅ ESPERADO:**
Você deve ver algo como:
```
Subject: Bem-vindo ao Gestto!
From: noreply@axiogesto.com
To: teste@exemplo.com

Olá Admin Salão Teste,

Sua conta foi criada com sucesso!

Suas credenciais de acesso:
Email: teste@exemplo.com
Senha temporária: Abc123XyZ...

Acesse: http://localhost:8000/onboarding/
```

---

## 📊 Checklist Final de Testes

- [ ] Cadastro redireciona para Stripe
- [ ] Formulário de pagamento Stripe aparece
- [ ] Cartão de teste 4242... funciona
- [ ] Página de sucesso aparece após pagamento
- [ ] Página de cancelamento aparece ao voltar
- [ ] Webhook 200 no Stripe CLI
- [ ] Assinatura criada no admin com status "ativa"
- [ ] Histórico de pagamento registrado
- [ ] Email aparece no console do Django
- [ ] Stripe trigger funciona

---

## 🐛 Troubleshooting

### Erro: "Plano sem preço configurado no Stripe"
**Solução:** Rodar novamente:
```bash
python atualizar_planos_stripe.py
```

### Erro 404 ao acessar /assinatura/sucesso
**Solução:** Verificar se o servidor Django está rodando

### Webhook retorna 400/500
**Verificar:**
1. `STRIPE_WEBHOOK_SECRET` está correto no `.env`?
2. Servidor Django foi reiniciado após mudar `.env`?
3. Stripe CLI está rodando?

### Não redireciona para Stripe
**Verificar logs no Terminal 1:**
- Procurar por: `Checkout URL criada para empresa...`
- Se aparecer erro, verificar:
  - `STRIPE_SECRET_KEY` está correto?
  - Plano tem `stripe_price_id`?

### Página do Stripe dá erro
**Possíveis causas:**
- Chave `STRIPE_SECRET_KEY` está expirada
- Price ID inválido
- Trial days configurado incorretamente

---

## 📹 Fluxo Visual Esperado

```
1. Landing Page
   ↓
2. Cadastro (formulário)
   ↓
3. [SISTEMA] Cria empresa + assinatura trial + usuário
   ↓
4. [SISTEMA] Gera checkout URL do Stripe
   ↓
5. Redirect → Stripe Checkout
   ↓
6. Cliente preenche cartão
   ↓
7. Stripe processa pagamento
   ↓
8. [WEBHOOK] Stripe notifica nosso sistema
   ↓
9. [SISTEMA] Ativa assinatura + envia email
   ↓
10. Redirect → Página de Sucesso 🎉
```

---

## 🎓 Próximos Passos Após Testes OK

1. [ ] Testar com todos os 3 planos (Essencial, Profissional, Empresarial)
2. [ ] Testar cartão recusado (4000 0000 0000 0002)
3. [ ] Testar webhook de renovação mensal
4. [ ] Testar cancelamento de assinatura
5. [ ] Configurar email SMTP real (Gmail/SendGrid)
6. [ ] Adicionar testes automatizados

---

## 🔐 Lembrete de Segurança

**IMPORTANTE:** Você está usando chaves de **TESTE** do Stripe:
- `pk_test_...`
- `sk_test_...`

Quando for para produção:
1. Trocar por chaves LIVE (`pk_live_...`, `sk_live_...`)
2. Recriar produtos e preços no modo LIVE do Stripe
3. Atualizar `stripe_price_id` dos planos
4. Configurar webhook no modo LIVE

---

**Bons testes! 🚀**

Se tudo funcionar, o próximo passo é:
- Criar template de gerenciamento de assinatura
- Deploy em produção
