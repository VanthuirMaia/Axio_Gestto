# ⚡ Quick Start - Testar n8n em 5 Minutos

## 🎯 Objetivo

Testar rapidamente se a integração Gestto + n8n está funcionando.

---

## ✅ Pré-requisitos

- [ ] Django rodando
- [ ] n8n rodando (VPS ou Cloud)
- [ ] Pelo menos 1 empresa cadastrada
- [ ] OpenAI API Key

---

## 🚀 Passo a Passo (5 min)

### **1. Configure o .env (1 min)**

Adicione no `.env` do Django:

```bash
N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/bot-universal
```

Reinicie o Django:
```bash
# Windows
python manage.py runserver

# Linux/Mac
./manage.py runserver
```

---

### **2. Importe o Template no n8n (1 min)**

1. Acesse seu n8n
2. Clique em "Import from File"
3. Selecione: `n8n-workflows/TEMPLATE_Bot_Universal_VPS_Simplificado.json`
4. Clique em "Import"

---

### **3. Configure o Workflow (2 min)**

1. Clique no node **"⚙️ Configurações + Dados"**
2. Edite os valores:

```javascript
config_django_url: "http://localhost:8000"  // ou sua URL
config_django_key: "n19kq-oh-2-g69-a-df-t42q-o-m6eq0he_prod_2025_secure"  // da sua .env
config_evolution_url: "https://evolution.axiodev.cloud"
config_evolution_key: "SUA-EVOLUTION-KEY"
config_openai_key: "sk-proj-SUA-OPENAI-KEY"
```

3. **Salve** (Ctrl+S)
4. **Ative** o workflow (toggle superior direito)

---

### **4. Teste com o Script (1 min)**

Execute o script de testes:

```bash
python scripts/testar_integracao_n8n.py
```

**Resultado Esperado:**
```
🧪 TESTADOR DE INTEGRAÇÃO GESTTO + N8N
============================================================

TESTE 1: Configuração Django
✅ N8N_WEBHOOK_URL configurado
✅ N8N_API_KEY configurado
✅ EVOLUTION_API_URL configurado

TESTE 2: Seleção de Empresa
✅ Empresa selecionada: Barbearia Teste (ID: 1)

TESTE 3: API - Listar Profissionais
✅ API respondeu OK - 3 profissionais encontrados

TESTE 4: API - Listar Serviços
✅ API respondeu OK - 5 serviços encontrados

TESTE 5: API - Horários de Funcionamento
✅ API respondeu OK - 5 horários configurados

TESTE 6: Webhook Intermediário (Django)
✅ Webhook intermediário OK - Encaminhado para n8n

TESTE 7: Webhook n8n (Direto)
✅ n8n recebeu e processou o webhook!

============================================================
🎉 TODOS OS TESTES PASSARAM!
============================================================
```

✅ **Se todos passaram, está funcionando!**

---

## 🧪 Teste Manual Rápido

Se não quiser rodar o script, teste manualmente:

### **Teste 1: API de Profissionais**

```bash
curl -X GET "http://localhost:8000/api/n8n/profissionais/?empresa_id=1" \
  -H "apikey: n19kq-oh-2-g69-a-df-t42q-o-m6eq0he_prod_2025_secure" \
  -H "empresa_id: 1"
```

✅ **Deve retornar lista de profissionais**

---

### **Teste 2: Webhook n8n**

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

✅ **Deve retornar 200 OK**

**Verifique no n8n:**
- Vá em "Executions"
- Deve aparecer uma execução recente
- Status: Success ✅

---

## ⚠️ Problemas Comuns

### **❌ "N8N_WEBHOOK_URL não configurado"**

**Solução:**
1. Adicione no `.env`: `N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/bot-universal`
2. Reinicie Django

---

### **❌ "API Key inválida"**

**Solução:**
Verifique se a chave é a mesma:
- Django: `config/settings.py` → `N8N_API_KEY`
- n8n: Node "Configurações" → `config_django_key`

---

### **❌ "Empresa não encontrada"**

**Solução:**
Cadastre uma empresa no Gestto ou use o ID correto.

---

### **❌ n8n não responde**

**Checklist:**
- [ ] Workflow está **ativado**? (toggle verde)
- [ ] Node "Webhook" existe?
- [ ] URL do webhook está correta?

---

## 📱 Teste End-to-End (WhatsApp)

Se quiser testar com WhatsApp real:

### **1. Crie Instância**
1. Acesse Gestto → Configurações → WhatsApp
2. Clique em "Criar Nova Instância"
3. Escaneie QR Code
4. Aguarde conexão

### **2. Envie Mensagem**
Com outro celular, envie:
```
Oi
```

### **3. Verifique Resposta**
Bot deve responder:
```
Olá! Sou a Luna, assistente virtual.
Posso te ajudar a agendar um horário
ou tirar alguma dúvida? 😊
```

✅ **Funcionou!**

---

## 📊 Verificar Logs

### **Django:**
```bash
tail -f logs/django.log | grep "Webhook"
```

### **n8n:**
- Acesse: n8n → Executions
- Veja última execução
- Verifique cada node

---

## 🎉 Próximos Passos

Se tudo funcionou:

1. ✅ Leia documentação completa: `docs/TESTE_INTEGRACAO_N8N.md`
2. ✅ Personalize o system prompt da IA
3. ✅ Configure domínios reais
4. ✅ Teste com múltiplas empresas
5. ✅ Coloque em produção!

---

## 🆘 Precisa de Ajuda?

Consulte:
- `docs/TESTE_INTEGRACAO_N8N.md` - Guia completo de testes
- `docs/WEBHOOK_EXPLICACAO_SIMPLES.md` - Como funciona o webhook
- `docs/N8N_TEMPLATE_COMPARISON.md` - Qual template usar
- `n8n-workflows/README.md` - Documentação dos workflows

---

## ✅ Checklist Rápido

- [ ] `.env` configurado com `N8N_WEBHOOK_URL`
- [ ] Template n8n importado e configurado
- [ ] Workflow n8n ativado
- [ ] Script de teste passou (ou testes manuais OK)
- [ ] Instância WhatsApp criada (opcional)
- [ ] Teste end-to-end funcionou (opcional)

**Tudo OK?** Você está pronto! 🚀
