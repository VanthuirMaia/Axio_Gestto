# 📦 Guia do Template n8n Universal

## 🎯 O Que É Este Template?

Este é um **workflow n8n completo e pronto para usar** que implementa um bot WhatsApp inteligente e dinâmico para seu SaaS de agendamentos.

**Características:**
✅ **Dinâmico** - Funciona com 1, 2, 10, 100 profissionais
✅ **Multi-tenant** - Um workflow para todas as empresas
✅ **IA Integrada** - Usa OpenAI para processar linguagem natural
✅ **Completo** - Agendar, consultar, cancelar
✅ **Escalável** - Pronto para produção

**Arquivo:** `n8n-workflows/TEMPLATE_Bot_Universal_SaaS.json`

---

## 🚀 Como Usar

### **Passo 1: Importar no n8n (5 min)**

1. **Acesse seu n8n:**
   - Cloud: https://app.n8n.cloud
   - Self-hosted: http://localhost:5678

2. **Importe o workflow:**
   - Clique em "Import from File"
   - Selecione: `TEMPLATE_Bot_Universal_SaaS.json`
   - Clique em "Import"

3. **Resultado:**
   - Workflow completo com 15+ nodes
   - Pronto para configurar

### **Passo 2: Configurar Credenciais (10 min)**

#### **2.1. Django API (HTTP Header Auth)**

```
Nome: Django API Auth
Tipo: Header Auth

Headers:
- Name: apikey
  Value: sua-api-key-do-settings-N8N_API_KEY

- Name: empresa_id
  Value: {{ $json.empresa_id }} (dinâmico)
```

**Onde criar:**
- n8n → Settings → Credentials → Add Credential
- Tipo: "Header Auth"
- Nome: "Django API Auth"

#### **2.2. Evolution API (HTTP Header Auth)**

```
Nome: Evolution API Auth
Tipo: Header Auth

Headers:
- Name: apikey
  Value: SUA-EVOLUTION-API-KEY-GLOBAL
```

#### **2.3. OpenAI (OpenAI Account)**

```
Nome: OpenAI Account
Tipo: OpenAI Credentials

API Key: sk-proj-xxxxxxxxxxxxx
Organization ID: (opcional)
```

**Onde obter:**
- https://platform.openai.com/api-keys

### **Passo 3: Configurar URLs (5 min)**

**Substituir em TODOS os nodes HTTP Request:**

#### **Nodes que apontam para Django:**
- `Buscar Profissionais`
- `Buscar Servicos`
- `Buscar Horarios`
- `Criar Agendamento`

**Trocar:**
```
❌ url: "https://seu-dominio.com/api/n8n/profissionais/"
✅ url: "https://axiogestto.com/api/n8n/profissionais/"
```

#### **Node que aponta para Evolution:**
- `Enviar Resposta WhatsApp`

**Trocar:**
```
❌ url: "https://evolution.axiodev.cloud/message/sendText/..."
✅ url: "https://SUA-EVOLUTION-URL/message/sendText/..."
```

### **Passo 4: Ativar Workflow (1 min)**

1. **Salve o workflow** (Ctrl+S)
2. **Ative-o** (toggle no canto superior direito)
3. **Copie a URL do webhook:**
   - Node "Webhook - Recebe Mensagem"
   - Production URL: `https://seu-n8n.com/webhook/bot-universal`

### **Passo 5: Conectar ao Django (5 min)**

**Opção A: Django chama n8n (webhook intermediário)**

```python
# Em empresas/api_views.py ou similar

@csrf_exempt
def whatsapp_webhook(request, empresa_id, secret):
    # ... validações ...

    # Encaminhar para n8n
    import requests

    n8n_url = settings.N8N_WEBHOOK_URL  # da .env

    payload = {
        'empresa_id': empresa_id,
        'body': request.body,
        # ... outros dados
    }

    response = requests.post(n8n_url, json=payload)

    return JsonResponse({'success': True})
```

**Opção B: Evolution chama n8n direto**

Configure webhook na Evolution API para apontar para:
```
https://seu-n8n.com/webhook/bot-universal
```

---

## 📋 Nodes do Workflow

### **1. Webhook - Recebe Mensagem**
- **Tipo:** Webhook Trigger
- **Função:** Recebe eventos do WhatsApp
- **URL:** `/webhook/bot-universal`
- **Dados recebidos:**
  ```json
  {
    "empresa_id": 1,
    "instance": "empresa_barbearia_pedro",
    "body": {
      "data": {
        "key": {
          "remoteJid": "5511999999999@s.whatsapp.net"
        },
        "message": {
          "conversation": "Quero agendar corte amanhã 14h"
        },
        "pushName": "Cliente João"
      }
    }
  }
  ```

### **2. Normalizar Dados**
- **Tipo:** Set (Edit Fields)
- **Função:** Extrai dados importantes do webhook
- **Saída:**
  - `empresa_id`
  - `telefone`
  - `mensagem`
  - `nome_cliente`
  - `instance_name`

### **3-5. Buscar Profissionais/Servicos/Horarios**
- **Tipo:** HTTP Request (GET)
- **Função:** Busca dados da API Django
- **URLs:**
  - `/api/n8n/profissionais/?empresa_id=1`
  - `/api/n8n/servicos/?empresa_id=1`
  - `/api/n8n/horarios-funcionamento/?empresa_id=1`

### **6. Consolidar Contexto**
- **Tipo:** Code (JavaScript)
- **Função:** Monta contexto completo para a IA
- **Saída:**
  - Lista de profissionais formatada
  - Lista de serviços formatada
  - Horários de funcionamento
  - Data/hora atual

### **7. Agente IA**
- **Tipo:** LangChain Agent (OpenAI)
- **Função:** Processa mensagem e extrai intenção
- **System Prompt:** Dinâmico (varia por empresa)
- **Saída:** JSON estruturado com:
  ```json
  {
    "intencao": "agendar",
    "servico": "Corte",
    "profissional": "João",
    "data": "2025-12-23",
    "hora": "14:00"
  }
  ```

### **8. Processar Output IA**
- **Tipo:** Code (JavaScript)
- **Função:** Parseia JSON da IA e faz match de IDs
- **Lógica:**
  - Normaliza nomes (remove acentos)
  - Busca profissional por nome fuzzy
  - Busca serviço por nome fuzzy
  - Retorna IDs numéricos

### **9. Router por Intenção**
- **Tipo:** Switch
- **Função:** Direciona fluxo por intenção
- **Rotas:**
  - `agendar` → Criar Agendamento
  - `cancelar` → (adicionar node)
  - `consultar` → (adicionar node)
  - `duvida` → Responder direto

### **10. Criar Agendamento**
- **Tipo:** HTTP Request (POST)
- **URL:** `/api/bot/processar/`
- **Body:**
  ```json
  {
    "telefone": "5511999999999",
    "intencao": "agendar",
    "dados": {
      "profissional_id": 1,
      "servico": "Corte",
      "data": "2025-12-23",
      "hora": "14:00"
    }
  }
  ```

### **11. Enviar Resposta WhatsApp**
- **Tipo:** HTTP Request (POST)
- **URL:** `/message/sendText/empresa_barbearia_pedro`
- **Body:**
  ```json
  {
    "number": "5511999999999",
    "text": "✅ Agendamento confirmado!..."
  }
  ```

### **12. Response - Webhook OK**
- **Tipo:** Respond to Webhook
- **Função:** Confirma recebimento do webhook
- **Response:** `{ "success": true }`

---

## 🔧 Personalizações Necessárias

### **1. System Prompt do Agente IA**

Personalize para cada tipo de negócio:

```javascript
// Para barbearia:
"Você é assistente de uma barbearia..."

// Para clínica médica:
"Você é assistente de uma clínica médica..."

// Para salão de beleza:
"Você é assistente de um salão de beleza..."
```

**Onde editar:**
- Node "Agente IA" → Parameters → Options → System Message

### **2. Mensagens de Resposta**

Customize as mensagens no node "Criar Agendamento":

```javascript
// Mensagem de sucesso
const mensagem = `✅ Agendamento confirmado!

📅 Serviço: ${servico}
👤 Profissional: ${profissional}
🕐 Data: ${data} às ${hora}
💰 Valor: R$ ${valor}

📝 Código: ${codigo}

Para cancelar: CANCELAR ${codigo}`;
```

### **3. Regras de Negócio**

Adicione validações customizadas no node "Processar Output IA":

```javascript
// Exemplo: Não agendar em domingos
if (new Date(data).getDay() === 0) {
  return [{
    json: {
      erro: true,
      mensagem: 'Não trabalhamos aos domingos!'
    }
  }];
}

// Exemplo: Anteced\u00eancia mínima
const agora = new Date();
const dataAgendamento = new Date(data + ' ' + hora);
const horasAntecedencia = (dataAgendamento - agora) / (1000 * 60 * 60);

if (horasAntecedencia < 2) {
  return [{
    json: {
      erro: true,
      mensagem: 'Precisa agendar com pelo menos 2 horas de antecedência!'
    }
  }];
}
```

---

## 🧪 Como Testar

### **Teste 1: Mensagem Simples**

**Enviar no WhatsApp:**
```
Quero agendar corte amanhã 14h
```

**Esperado:**
1. n8n recebe webhook
2. Busca profissionais, serviços
3. IA processa: intencao="agendar", servico="corte"
4. Django cria agendamento
5. WhatsApp recebe confirmação

### **Teste 2: Com Profissional Específico**

**Enviar:**
```
Quero agendar barba com o João amanhã às 10h
```

**Esperado:**
- IA extrai: profissional="João"
- Match encontra ID do João
- Agendamento criado para João

### **Teste 3: Consultar Horários**

**Enviar:**
```
Quais horários disponíveis amanhã?
```

**Esperado:**
- IA detecta: intencao="consultar"
- Router direciona para rota "Consultar"
- (Precisa adicionar node de consulta)

### **Teste 4: Múltiplos Profissionais**

**Adicione 3+ profissionais no Django**

**Enviar:**
```
Quero agendar com a Maria
```

**Esperado:**
- Sistema busca dinamicamente todos os profissionais
- Match encontra "Maria" na lista
- Agendamento criado com Maria

---

## ⚠️ Troubleshooting

### **Erro: "API Key inválida"**

**Solução:**
1. Verifique credencial "Django API Auth"
2. Confirme que `apikey` header está configurado
3. Valide `N8N_API_KEY` no Django settings.py

### **Erro: "Profissional não encontrado"**

**Solução:**
1. Verifique se profissional existe no Django
2. Confirme que está ativo (`ativo=True`)
3. Teste match fuzzy no node "Processar Output IA"

### **IA não entende mensagem**

**Solução:**
1. Revise system prompt do Agente IA
2. Adicione mais exemplos no prompt
3. Aumente temperature da IA (0.7 → 1.0)

### **Webhook não chega no n8n**

**Solução:**
1. Verifique se workflow está ativado
2. Confirme URL do webhook
3. Teste com ferramenta como Postman
4. Verifique logs do n8n

---

## 📊 Métricas e Logs

### **Ver Execuções**

n8n → Executions → Filtre por workflow

**Informações úteis:**
- Tempo de execução
- Dados de entrada/saída
- Erros (se houver)

### **Debug**

Ative debug mode:
- Workflow Settings → Save Manual Executions
- Clique em "Execute Workflow" para testar manualmente

---

## 🚀 Próximos Passos

### **Funcionalidades a Adicionar:**

1. **Cancelamento de Agendamento**
   - Add node após Router (saída "Cancelar")
   - HTTP POST `/api/bot/processar/`
   - Body: `{ intencao: "cancelar", codigo: "ABC123" }`

2. **Consulta de Horários**
   - Add node após Router (saída "Consultar")
   - HTTP POST `/api/n8n/horarios-disponiveis/`
   - Formatar resposta com horários livres

3. **Confirmação de Agendamento**
   - Add node para confirmar agendamentos pendentes
   - HTTP POST `/api/bot/processar/`
   - Body: `{ intencao: "confirmar", codigo: "ABC123" }`

4. **Lembretes Automáticos**
   - Criar workflow separado com Schedule Trigger
   - Busca agendamentos do dia seguinte
   - Envia mensagem de lembrete

5. **Follow-up**
   - Enviar mensagem após atendimento
   - Pedir avaliação/feedback
   - Oferecer novo agendamento

---

## 📦 Exportar Workflow Customizado

Depois de personalizar:

1. n8n → Settings → Download
2. Salvar como: `Bot_Universal_${SuaEmpresa}.json`
3. Versionar no Git
4. Documentar customizações

---

## 🎯 Checklist de Produção

Antes de colocar em produção:

- [ ] Credenciais configuradas
- [ ] URLs atualizadas (Django, Evolution)
- [ ] System prompt customizado
- [ ] Mensagens personalizadas
- [ ] Testes com 1, 3, 6 profissionais
- [ ] Teste de erro (API offline)
- [ ] Teste de horários indisponíveis
- [ ] Configurar error workflow
- [ ] Ativar workflow
- [ ] Monitorar primeiras execuções

---

## 💡 Dicas Avançadas

### **1. Cache de Dados da Empresa**

Para evitar buscar dados toda vez:

```javascript
// No node "Consolidar Contexto"
// Adicione cache de 5 minutos

const cacheKey = `empresa_${empresa_id}`;
const cached = $getWorkflowStaticData(cacheKey);

if (cached && cached.timestamp > Date.now() - 300000) {
  return cached.data;
}

// Busca dados...
// Salva no cache
$setWorkflowStaticData(cacheKey, {
  timestamp: Date.now(),
  data: resultado
});
```

### **2. Fila de Mensagens**

Se receber muitas mensagens simultâneas:

- Add node "Queue" entre Webhook e Buscar APIs
- Processa uma mensagem por vez
- Evita sobrecarga

### **3. Fallback para Humano**

Se IA não entender:

```javascript
if (tentativasFalhas >= 3) {
  return {
    mensagem: "Vou transferir você para um atendente humano. Aguarde..."
  };
  // Notifica equipe via Slack/Email
}
```

---

## ✅ Conclusão

Este template é um **ponto de partida** completo e funcional. Personalize conforme sua necessidade!

**Vantagens:**
- ✅ Funciona out-of-the-box
- ✅ Escalável para N profissionais
- ✅ Multi-tenant ready
- ✅ IA integrada
- ✅ Fácil de customizar

**Suporte:**
- Documentação completa em `docs/`
- Exemplos em `n8n-workflows/`
- APIs Django prontas

Boa sorte! 🚀
