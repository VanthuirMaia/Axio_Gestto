# 📚 Documentação - Axio Gestto + n8n

## 🎯 Índice Geral

Bem-vindo à documentação completa da integração Gestto + n8n!

---

## 🚀 Começando

### **Para Quem Tem Pressa (5 min):**
👉 **[QUICK_START_N8N.md](QUICK_START_N8N.md)** - Setup e teste em 5 minutos

### **Para Quem Quer Entender Tudo:**
👉 **[N8N_INTEGRATION_ANALYSIS.md](N8N_INTEGRATION_ANALYSIS.md)** - Análise completa da integração

---

## 📖 Documentação por Tópico

### **1. Integração e Arquitetura**

#### **Integração n8n**
- **[N8N_INTEGRATION_ANALYSIS.md](N8N_INTEGRATION_ANALYSIS.md)** - Análise completa da integração
- **[N8N_READY_TO_USE.md](N8N_READY_TO_USE.md)** - APIs Django prontas para n8n
- **[ONBOARDING_FLOW.md](ONBOARDING_FLOW.md)** - Fluxo de onboarding multi-tenant

#### **Webhooks**
- **[WEBHOOK_EXPLICACAO_SIMPLES.md](WEBHOOK_EXPLICACAO_SIMPLES.md)** ⭐ - Explicação super didática
- **[WEBHOOK_FLOW_DINAMICO.md](WEBHOOK_FLOW_DINAMICO.md)** - Documentação técnica completa

---

### **2. Templates e Workflows**

#### **Guias de Templates**
- **[N8N_TEMPLATE_COMPARISON.md](N8N_TEMPLATE_COMPARISON.md)** ⭐ - Qual template usar?
- **[N8N_TEMPLATE_GUIDE.md](N8N_TEMPLATE_GUIDE.md)** - Guia do template SaaS
- **[N8N_VPS_SETUP.md](N8N_VPS_SETUP.md)** - Setup em VPS sem credenciais

#### **Conceitos de Workflows**
- **[N8N_DYNAMIC_WORKFLOWS.md](N8N_DYNAMIC_WORKFLOWS.md)** - Workflows dinâmicos vs estáticos
- **[N8N_HUMANIZACAO_IA.md](N8N_HUMANIZACAO_IA.md)** ⭐ - Como manter comunicação humanizada

---

### **3. Testes**

- **[QUICK_START_N8N.md](QUICK_START_N8N.md)** ⭐ - Teste rápido em 5 minutos
- **[TESTE_INTEGRACAO_N8N.md](TESTE_INTEGRACAO_N8N.md)** - Guia completo de testes

**Script Automatizado:**
- `scripts/testar_integracao_n8n.py` - Testes automatizados

---

## 🗂️ Estrutura dos Documentos

### **Nível 1: Começar Agora**
Para quem quer configurar e testar rapidamente:

```
1. QUICK_START_N8N.md (5 min)
   ↓
2. N8N_TEMPLATE_COMPARISON.md (escolher template)
   ↓
3. TESTE_INTEGRACAO_N8N.md (validar)
```

---

### **Nível 2: Entender o Sistema**
Para quem quer entender como funciona:

```
1. WEBHOOK_EXPLICACAO_SIMPLES.md (como funciona?)
   ↓
2. N8N_DYNAMIC_WORKFLOWS.md (por que dinâmico?)
   ↓
3. N8N_HUMANIZACAO_IA.md (como humanizar?)
   ↓
4. ONBOARDING_FLOW.md (multi-tenant)
```

---

### **Nível 3: Documentação Técnica**
Para quem precisa de detalhes técnicos:

```
1. N8N_INTEGRATION_ANALYSIS.md (análise completa)
   ↓
2. N8N_READY_TO_USE.md (APIs disponíveis)
   ↓
3. WEBHOOK_FLOW_DINAMICO.md (webhook técnico)
   ↓
4. N8N_TEMPLATE_GUIDE.md (templates detalhados)
```

---

## 🎯 Guia por Caso de Uso

### **Caso 1: "Quero testar se está funcionando"**
→ Leia: `QUICK_START_N8N.md`
→ Execute: `scripts/testar_integracao_n8n.py`

---

### **Caso 2: "Uso n8n em VPS, qual template usar?"**
→ Leia: `N8N_TEMPLATE_COMPARISON.md`
→ Recomendação: `TEMPLATE_Bot_Universal_VPS_Simplificado.json`
→ Setup: `N8N_VPS_SETUP.md`

---

### **Caso 3: "Como funciona o webhook? Não entendi"**
→ Leia: `WEBHOOK_EXPLICACAO_SIMPLES.md` ⭐
→ Exemplo prático com João agendando corte

---

### **Caso 4: "Tenho 1, 3 ou 6 profissionais. Preciso de workflows diferentes?"**
→ Leia: `N8N_DYNAMIC_WORKFLOWS.md`
→ Resposta: **NÃO!** Um workflow serve para N profissionais

---

### **Caso 5: "Como manter comunicação humanizada?"**
→ Leia: `N8N_HUMANIZACAO_IA.md` ⭐
→ Dica: System prompt + Temperature 0.8

---

### **Caso 6: "Como o cliente faz onboarding?"**
→ Leia: `ONBOARDING_FLOW.md`
→ Fluxo: Cadastro → QR Code → Conectar → Pronto

---

### **Caso 7: "Quais APIs Django posso usar no n8n?"**
→ Leia: `N8N_READY_TO_USE.md`
→ 8 endpoints prontos para usar

---

## 📦 Templates Disponíveis

### **n8n Cloud (com credenciais):**
- `TEMPLATE_Bot_Universal_SaaS.json`
- Guia: `N8N_TEMPLATE_GUIDE.md`

### **VPS Self-hosted (sem credenciais):**

1. **Simplificado** ⭐ RECOMENDADO
   - `TEMPLATE_Bot_Universal_VPS_Simplificado.json`
   - Config visual no node
   - Sem restart

2. **Humanizado**
   - `TEMPLATE_Bot_Universal_VPS_Humanizado.json`
   - Luna IA + Temperature 0.8
   - Variáveis de ambiente

3. **Básico**
   - `TEMPLATE_Bot_Universal_VPS.json`
   - Funcional simples
   - Variáveis de ambiente

**Comparação:** `N8N_TEMPLATE_COMPARISON.md`

---

## 🧪 Como Testar?

### **Opção 1: Teste Automatizado (Recomendado)**
```bash
python scripts/testar_integracao_n8n.py
```

### **Opção 2: Teste Manual**
Siga: `TESTE_INTEGRACAO_N8N.md`

### **Opção 3: Quick Test (5 min)**
Siga: `QUICK_START_N8N.md`

---

## 🔑 Conceitos-Chave

### **Multi-tenant**
- 1 Django para todas as empresas
- 1 Evolution API com múltiplas instâncias
- 1 n8n com workflow universal
- Cada empresa = instância separada

### **Workflow Dinâmico**
- Busca dados via API
- Funciona para N profissionais
- Não precisa replicar

### **Webhook Intermediário**
```
Evolution → Django → n8n
```
- Django valida assinatura
- Django adiciona empresa_id
- Django encaminha para n8n

### **Humanização**
- System prompt conversacional
- Temperature 0.7-0.8
- Emojis moderados
- Linguagem natural

---

## 📊 Estatísticas

**Documentação:**
- 10 documentos Markdown
- ~4.800 linhas
- 8 tópicos principais

**Templates:**
- 4 workflows n8n
- ~1.900 linhas JSON
- Todos 100% dinâmicos

**Código:**
- Webhook intermediário
- 8 APIs n8n prontas
- Script de testes automatizado

---

## 🎯 Checklist de Implementação

### **Backend (Django):**
- [ ] APIs n8n implementadas (`api_n8n.py`)
- [ ] Webhook intermediário (`configuracoes/views.py`)
- [ ] Evolution API integrada (`evolution_api.py`)
- [ ] Configurações no `.env`

### **n8n:**
- [ ] Template importado
- [ ] Configurações preenchidas
- [ ] Workflow ativado
- [ ] Webhook URL copiada

### **Testes:**
- [ ] APIs retornam dados
- [ ] Webhook funciona
- [ ] n8n processa
- [ ] Agendamento cria
- [ ] WhatsApp responde

### **Produção:**
- [ ] Domínios configurados
- [ ] SSL ativo
- [ ] Monitoramento configurado
- [ ] Backup de workflows
- [ ] Documentação para equipe

---

## 🆘 Troubleshooting Rápido

### **Bot não responde:**
1. Workflow n8n ativado?
2. `N8N_WEBHOOK_URL` configurado?
3. Instância WhatsApp conectada?

### **API Key inválida:**
1. Verifique `.env` → `N8N_API_KEY`
2. Verifique n8n → `config_django_key`
3. Devem ser iguais!

### **IA não entende:**
1. OpenAI API Key válida?
2. Tem créditos na conta?
3. Model `gpt-4o-mini` disponível?

**Mais detalhes:** `TESTE_INTEGRACAO_N8N.md` → Seção Troubleshooting

---

## 🚀 Roadmap de Estudo

### **Dia 1: Setup Básico**
1. Ler `QUICK_START_N8N.md`
2. Importar template
3. Rodar testes

### **Dia 2: Entender Sistema**
1. Ler `WEBHOOK_EXPLICACAO_SIMPLES.md`
2. Ler `N8N_DYNAMIC_WORKFLOWS.md`
3. Experimentar com dados reais

### **Dia 3: Personalização**
1. Ler `N8N_HUMANIZACAO_IA.md`
2. Customizar system prompt
3. Testar tom de voz

### **Dia 4: Multi-tenant**
1. Ler `ONBOARDING_FLOW.md`
2. Criar 2+ empresas
3. Testar isolamento

### **Dia 5: Produção**
1. Ler `TESTE_INTEGRACAO_N8N.md`
2. Rodar todos os testes
3. Deploy!

---

## 🎉 Recursos Extras

### **Scripts Úteis:**
- `scripts/testar_integracao_n8n.py` - Testes automatizados
- `scripts/debug_*.py` - Scripts de debug

### **Workflows Legados:**
- `n8n-workflows/Bot_Barbearia_Brandao.json` - Exemplo estático
- **Não use em produção!** Apenas referência.

---

## 💡 Dicas

### **Para Desenvolvedores:**
- Leia código em `api_n8n.py` e `bot_api.py`
- Entenda autenticação `APIKeyAuthentication`
- Veja como queries multi-tenant funcionam

### **Para Product Managers:**
- Foque em `ONBOARDING_FLOW.md`
- Entenda fluxo do cliente
- Veja métricas em `TESTE_INTEGRACAO_N8N.md`

### **Para DevOps:**
- Configure `N8N_WEBHOOK_URL` correto
- Monitore logs: Django + n8n + Evolution
- Backup de workflows n8n

---

## ✅ Próximos Passos

1. **Leia:** `QUICK_START_N8N.md`
2. **Teste:** `scripts/testar_integracao_n8n.py`
3. **Customize:** Templates e system prompts
4. **Deploy:** Produção!
5. **Monitore:** Logs e métricas

---

## 📞 Suporte

**Documentação:**
- Todos os arquivos `.md` desta pasta
- README em `n8n-workflows/`

**Comunidade:**
- Issues no GitHub
- Documentação oficial n8n
- Documentação Evolution API

---

## 🎯 Resumo Executivo

**O que você tem:**
- ✅ Sistema multi-tenant completo
- ✅ Bot WhatsApp inteligente (IA)
- ✅ Agendamentos automáticos
- ✅ Workflows dinâmicos (N profissionais)
- ✅ Comunicação humanizada
- ✅ Documentação completa
- ✅ Testes automatizados

**Está pronto para produção!** 🚀

---

**Última atualização:** Dezembro 2025
**Versão:** 1.0.0
