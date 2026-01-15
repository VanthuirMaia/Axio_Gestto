# 🤖 INSTRUÇÕES - CONFIGURAR N8N COM IA

## 📝 RESUMO

Você precisa:
1. Importar workflow no n8n
2. Configurar variáveis (API Keys)
3. Ativar o workflow
4. Copiar URL do webhook
5. Configurar no .env do Django
6. Fazer push para produção

---

## 🔧 PASSO 1: IMPORTAR WORKFLOW NO N8N

### 1.1. Acessar n8n
- URL: https://n8n.axiodev.cloud
- Fazer login

### 1.2. Criar Novo Workflow
1. Clique no botão **"+"** (Add workflow)
2. Clique nos **3 pontinhos** (...) no topo
3. Selecione **"Import from file"**
4. Escolha o arquivo: `n8n-workflows/TEMPLATE_Bot_Universal_VPS_Simplificado.json`

### 1.3. Renomear Workflow (Opcional)
- Nome sugerido: "Bot WhatsApp Gestto - Produção"

---

## ⚙️ PASSO 2: CONFIGURAR VARIÁVEIS

### 2.1. Abrir Nó "Config"
- É o primeiro nó do workflow (ícone de engrenagem)
- Clique duas vezes nele

### 2.2. Preencher Variáveis

```javascript
// URLs e Autenticação
GESTTO_API_URL: "https://gestto.axiodev.cloud"
GESTTO_API_KEY: "SUA_CHAVE_AQUI"  // Mesma do .env

// OpenAI (para IA humanizada)
OPENAI_API_KEY: "sk-..."  // Sua chave da OpenAI

// Evolution API (se usar Evolution Cloud)
EVOLUTION_API_URL: "https://evolution.axiodev.cloud"  // Ou sua URL
```

### 2.3. Onde Obter as Chaves

**GESTTO_API_KEY**:
- Está no seu `.env`: `GESTTO_API_KEY`
- Ou gere uma nova: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

**OPENAI_API_KEY**:
- Crie em: https://platform.openai.com/api-keys
- Escolha modelo: `gpt-4` ou `gpt-3.5-turbo` (mais barato)
- **IMPORTANTE**: Adicione créditos na conta OpenAI!

---

## ✅ PASSO 3: ATIVAR WORKFLOW

1. **Salvar** o workflow (Ctrl+S ou botão "Save")
2. **Toggle no topo** para "Active" (deve ficar verde)
3. ✅ Workflow agora está rodando!

---

## 📋 PASSO 4: COPIAR URL DO WEBHOOK

### 4.1. Localizar Nó Webhook
- É o primeiro nó triangular/roxo
- Nome: "Webhook" ou "Webhook Trigger"

### 4.2. Copiar Production URL
1. Clique no nó Webhook
2. Na sidebar direita, procure **"Production URL"**
3. Copie a URL completa (algo como):
   ```
   https://n8n.axiodev.cloud/webhook/abc123-def456-ghi789
   ```

### 4.3. ⚠️ IMPORTANTE
- **NÃO use a Test URL** (só funciona em teste)
- **USE a Production URL** (funciona em produção)

---

## 🔐 PASSO 5: CONFIGURAR NO DJANGO

### Opção A: Usar Script Automático (Recomendado)

```bash
# Em desenvolvimento (local)
bash configurar_n8n.sh
```

O script vai:
1. Pedir a URL do webhook
2. Atualizar o .env automaticamente
3. Testar conexão

### Opção B: Manual

1. **Editar `.env`** (em produção):
   ```bash
   nano .env
   ```

2. **Adicionar/Atualizar linha**:
   ```env
   N8N_WEBHOOK_URL=https://n8n.axiodev.cloud/webhook/SEU-WEBHOOK-ID-AQUI
   ```

3. **Salvar** (Ctrl+X, Y, Enter)

4. **Reiniciar Django**:
   ```bash
   sudo systemctl restart gunicorn
   # ou
   pm2 restart gestto
   ```

---

## 🧪 PASSO 6: TESTAR

### 6.1. Testar Webhook Manualmente

```bash
# Cole a URL do webhook do n8n aqui:
WEBHOOK_URL="https://n8n.axiodev.cloud/webhook/SEU-ID"

# Testar se está acessível:
curl -X POST $WEBHOOK_URL \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

**Resposta esperada**: Status 200 ou 201 (sucesso)

### 6.2. Testar Fluxo Completo

1. **Conectar WhatsApp** no sistema (se já não conectou)
2. **Enviar mensagem** para o número conectado:
   ```
   Oi, quero agendar
   ```

3. **Verificar logs do n8n**:
   - Abra o workflow no n8n
   - Clique em "Executions" (canto superior direito)
   - Deve aparecer execuções recentes

4. **Bot deve responder** com IA humanizada!

---

## 🐛 TROUBLESHOOTING

### ❌ "Webhook não recebe mensagens"

**Verificar**:
1. Workflow está **Active** (toggle verde)?
2. URL do webhook está correta no `.env`?
3. Django foi reiniciado após alterar `.env`?
4. Evolution API está enviando webhook para a URL correta?

**Comando debug**:
```bash
# Ver URL configurada no Django
grep N8N_WEBHOOK_URL .env

# Ver logs do Django
tail -f logs/django.log
# Procurar por: "Webhook encaminhado para n8n"
```

### ❌ "n8n retorna erro 401/403"

- Verifique se `GESTTO_API_KEY` está correta
- Deve ser a mesma no `.env` do Django e no nó Config do n8n

### ❌ "Bot responde mas sem IA (respostas genéricas)"

- Verifique `OPENAI_API_KEY` no n8n
- Confirme que tem créditos na conta OpenAI
- Veja logs de execução no n8n (pode mostrar erro da OpenAI)

### ❌ "Erro 500 no n8n"

- Abra o workflow no n8n
- Vá em "Executions"
- Clique na execução com erro
- Veja qual nó falhou e a mensagem de erro

---

## 📊 FLUXO COMPLETO (VISUAL)

```
┌──────────────┐
│   Cliente    │
│  (WhatsApp)  │
└──────┬───────┘
       │ 1. Envia: "Quero agendar"
       ↓
┌──────────────┐
│ Evolution API│
└──────┬───────┘
       │ 2. Webhook
       ↓
┌──────────────────────────────────────┐
│         DJANGO (seu sistema)          │
│                                       │
│  configuracoes/views.py:             │
│  whatsapp_webhook_n8n()              │
│                                       │
│  ✓ Valida empresa                    │
│  ✓ Valida secret                     │
│  ✓ Valida assinatura ativa           │
└──────┬───────────────────────────────┘
       │ 3. Encaminha payload enriquecido
       ↓
┌──────────────────────────────────────┐
│         N8N (processamento IA)       │
│                                       │
│  Nó 1: Webhook recebe                │
│  Nó 2: Extrai dados da mensagem      │
│  Nó 3: Busca serviços/profissionais  │
│         (GET /api/n8n/servicos)      │
│  Nó 4: OpenAI processa com IA        │
│         System: "Você é Luna..."     │
│         User: "Quero agendar"        │
│  Nó 5: OpenAI retorna JSON:          │
│         {intencao: "agendar", ...}   │
│  Nó 6: Busca horários disponíveis    │
│  Nó 7: Cria agendamento              │
│         (POST /api/bot/processar)    │
└──────┬───────────────────────────────┘
       │ 4. Retorna resposta humanizada
       ↓
┌──────────────┐
│ Evolution API│
│ (envia msg)  │
└──────┬───────┘
       │ 5. WhatsApp
       ↓
┌──────────────┐
│   Cliente    │
│   Recebe:    │
│  "Oi! 😊     │
│   Adoraria   │
│   agendar    │
│   com você!" │
└──────────────┘
```

---

## 🎯 CHECKLIST FINAL

Antes de ir para produção:

- [ ] Workflow importado no n8n
- [ ] Variáveis configuradas (GESTTO_API_KEY, OPENAI_API_KEY)
- [ ] Workflow ativado (toggle verde)
- [ ] URL do webhook copiada (Production URL)
- [ ] .env atualizado com N8N_WEBHOOK_URL
- [ ] Django reiniciado
- [ ] Teste manual enviou mensagem e bot respondeu com IA
- [ ] Logs do n8n mostram execuções sem erro

---

## 📞 SUPORTE

**Se encontrar problemas**:

1. Veja logs do Django: `tail -f logs/django.log`
2. Veja execuções do n8n: Workflow → Executions
3. Teste endpoint do n8n: `curl -X POST [URL_WEBHOOK]`
4. Verifique Evolution API: Configurações → Webhook URL está correta?

**Arquivos importantes**:
- `n8n-workflows/TEMPLATE_Bot_Universal_VPS_Simplificado.json` - Workflow
- `docs/integracao/n8n.md` - Documentação completa API
- `configuracoes/views.py:755` - Código do webhook intermediário

---

**Boa sorte! 🚀**
