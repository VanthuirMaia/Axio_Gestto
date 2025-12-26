# 📦 n8n Workflows - Axio Gestto

## 🎯 Qual template usar?

### **Você usa n8n em VPS self-hosted SEM sistema de credenciais?**
👉 **Use: `TEMPLATE_Bot_Universal_VPS_Simplificado.json`** ⚡ **RECOMENDADO**

### **Você usa n8n Cloud (ou self-hosted COM sistema de credenciais)?**
👉 **Use: `TEMPLATE_Bot_Universal_SaaS.json`**

---

## 📁 Arquivos Disponíveis

### ✅ Templates Prontos (Use estes!)

#### 1. **TEMPLATE_Bot_Universal_VPS_Simplificado.json** ⭐ MELHOR PARA VPS
- **Para:** VPS self-hosted sem credenciais
- **Config:** Visual, direto no node "⚙️ Configurações + Dados"
- **Humanização:** ✅ Completa (Luna IA)
- **Setup:** 5 minutos
- **Restart n8n:** ❌ Não precisa
- **Documentação:** `docs/N8N_TEMPLATE_COMPARISON.md`

#### 2. **TEMPLATE_Bot_Universal_VPS_Humanizado.json**
- **Para:** VPS com variáveis de ambiente configuradas
- **Config:** Variáveis de ambiente (.env ou docker-compose)
- **Humanização:** ✅ Completa (Luna IA)
- **Setup:** 10 minutos
- **Restart n8n:** ✅ Sim
- **Documentação:** `docs/N8N_HUMANIZACAO_IA.md`

#### 3. **TEMPLATE_Bot_Universal_VPS.json**
- **Para:** VPS básico
- **Config:** Variáveis de ambiente
- **Humanização:** ⚠️ Básica
- **Setup:** 10 minutos
- **Restart n8n:** ✅ Sim
- **Documentação:** `docs/N8N_VPS_SETUP.md`

#### 4. **TEMPLATE_Bot_Universal_SaaS.json**
- **Para:** n8n Cloud ou self-hosted COM sistema de credenciais
- **Config:** Credenciais do n8n (httpHeaderAuth)
- **Humanização:** ✅ Completa
- **Setup:** 10 minutos
- **Restart n8n:** ❌ Não
- **Documentação:** `docs/N8N_TEMPLATE_GUIDE.md`

---

## 🗂️ Workflows Antigos (Não usar!)

Estes são workflows da Barbearia do Brandão (hard-coded para 2 profissionais específicos):

- ❌ `Bot_Barbearia_Brandao.json` - Hard-coded para Pedro e Juan
- ❌ `Bot_Profissional_Juan.json` - Apenas Juan
- ❌ `Bot_Profissional_Pedro.json` - Apenas Pedro
- ❌ `Lembretes_WhatsApp.json` - Sistema de lembretes
- ❌ `Notificacao_Novo_Agendamento.json` - Notificações
- ❌ `Webhook_Evolution_Teste.json` - Teste de webhook
- ❌ `WhatsApp_Agendamento_Inicial.json` - Versão inicial

**Por que não usar?**
- Não são dinâmicos (funcionam só com 2 profissionais)
- Hard-coded (não funciona para outros clientes)
- Falta de documentação
- Não escaláveis

**O que fazer com eles?**
- Manter como referência histórica
- Usar templates novos (`TEMPLATE_*`)

---

## 🚀 Início Rápido (5 minutos)

### **Passo 1: Escolha o template**
```bash
# Para VPS (SEM credenciais) - RECOMENDADO
TEMPLATE_Bot_Universal_VPS_Simplificado.json

# Para n8n Cloud (COM credenciais)
TEMPLATE_Bot_Universal_SaaS.json
```

### **Passo 2: Importe no n8n**
1. Acesse seu n8n
2. Clique em "Import from File"
3. Selecione o arquivo .json
4. Clique em "Import"

### **Passo 3A: Configure (VPS Simplificado)**
1. Clique no node "⚙️ Configurações + Dados"
2. Edite os valores:
   ```javascript
   config_django_url: "https://axiogestto.com"
   config_django_key: "SUA-CHAVE-DJANGO"
   config_evolution_url: "https://evolution.axiodev.cloud"
   config_evolution_key: "SUA-CHAVE-EVOLUTION"
   config_openai_key: "sk-proj-SUA-CHAVE-OPENAI"
   ```
3. Salve (Ctrl+S)

### **Passo 3B: Configure (n8n Cloud/SaaS)**
1. Crie credenciais:
   - Django API Auth (Header Auth)
   - Evolution API Auth (Header Auth)
   - OpenAI Account
2. Atualize URLs nos nodes HTTP Request
3. Salve (Ctrl+S)

### **Passo 4: Ative e teste**
1. Ative o workflow (toggle superior direito)
2. Copie a URL do webhook
3. Configure webhook no Django/Evolution
4. Envie mensagem de teste no WhatsApp!

---

## 📖 Documentação Completa

Toda documentação está em `docs/`:

### **Guias de Setup:**
- `N8N_TEMPLATE_COMPARISON.md` - Comparação entre templates (LEIA PRIMEIRO!)
- `N8N_VPS_SETUP.md` - Setup em VPS sem credenciais
- `N8N_TEMPLATE_GUIDE.md` - Setup no n8n Cloud/SaaS

### **Conceitos:**
- `N8N_HUMANIZACAO_IA.md` - Como funciona a humanização ⭐
- `N8N_DYNAMIC_WORKFLOWS.md` - Workflows dinâmicos vs estáticos
- `N8N_INTEGRATION_ANALYSIS.md` - Análise da integração completa
- `N8N_READY_TO_USE.md` - APIs Django prontas

### **Arquitetura:**
- `ONBOARDING_FLOW.md` - Fluxo de onboarding de clientes
- `ARCHITECTURE.md` - Arquitetura multi-tenant do sistema

---

## 🔧 Troubleshooting

### **Erro: "API Key inválida"**
- Verifique se a chave é a mesma do Django `settings.py`
- Confirme que o header é `apikey` (minúsculo)

### **Erro: "Variável undefined"**
- VPS Simplificado: Edite valores no node "Configurações"
- VPS com env vars: Configure .env e reinicie n8n

### **IA não entende mensagens**
- Verifique OpenAI API Key
- Confirme que tem créditos na conta OpenAI
- Modelo recomendado: `gpt-4o-mini`

### **Webhook não recebe mensagens**
- Verifique se workflow está ativado
- Confirme URL do webhook no Evolution/Django
- Teste com Postman primeiro

---

## 💡 Dicas

### **Personalização:**
- Nome da assistente: Edite "Luna" no system prompt
- Tom de voz: Ajuste personalidade no system prompt
- Temperature: 0.7-0.8 para natural, 0.3-0.5 para conservador

### **Múltiplas Empresas:**
- Duplique o workflow VPS Simplificado
- Edite configurações em cada cópia
- Renomeie: "Bot Empresa A", "Bot Empresa B"

### **Testes:**
- Use workflow em modo "teste" (não ativado)
- Execute manualmente com dados de exemplo
- Verifique execuções no histórico do n8n

---

## ✅ Checklist de Produção

Antes de colocar em produção:

- [ ] Template correto importado
- [ ] Configurações preenchidas (URLs, API Keys)
- [ ] System prompt personalizado para o negócio
- [ ] Temperature ajustada (0.7-0.8)
- [ ] Teste com 1, 3, 6 profissionais
- [ ] Teste de erro (API offline)
- [ ] Teste de horários indisponíveis
- [ ] Webhook configurado no Django/Evolution
- [ ] Workflow ativado
- [ ] Primeiras mensagens reais monitoradas

---

## 🎯 Resumo

**Para VPS (sem credenciais):**
```
TEMPLATE_Bot_Universal_VPS_Simplificado.json ⚡
↓
Editar node "Configurações + Dados"
↓
Salvar e Ativar
↓
Pronto! 🎉
```

**Para n8n Cloud (com credenciais):**
```
TEMPLATE_Bot_Universal_SaaS.json
↓
Criar credenciais
↓
Atualizar URLs
↓
Salvar e Ativar
↓
Pronto! 🎉
```

---

## 🆘 Precisa de Ajuda?

1. Leia `docs/N8N_TEMPLATE_COMPARISON.md` primeiro
2. Verifique troubleshooting acima
3. Confira execuções no histórico do n8n
4. Revise logs do Django e Evolution API

**Boa sorte! 🚀**
