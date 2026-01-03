# 📊 Análise do Workflow "AtendimentoAxio"

## 🔍 Estrutura Identificada

Este workflow é **comercial da Axio** (venda de automação), não é um bot de agendamento do Gestto.

### **Componentes Principais:**

1. **Webhook1** - Recebe mensagens do WhatsApp (Evolution API)
2. **Normaliza** - Extrai dados da mensagem
3. **Switch de Origem** - Detecta se é áudio, imagem, documento ou texto
4. **Tratamento de Mídia:**
   - Mensagem de Audio → Converter Áudio → OpenAI (transcrição)
   - Envio de Imagens → Converter Imagem
   - Envio de Documentos → Converter Arquivo
5. **Controle de Bloqueio (Redis)** - Evita múltiplas conversas simultâneas
6. **AI Agent** - Agente de IA com OpenAI + ferramentas
7. **Memory Redis** - Histórico de conversas
8. **Vector Store Supabase** - Base de conhecimento
9. **Tools:**
   - Calculator
   - Think (raciocínio)
   - Workflow (executar sub-workflows)

---

## 🎯 Adaptação para Gestto (Bot de Agendamento)

### ✅ **O que MANTER:**

| Component | Por quê |
|-----------|---------|
| **Webhook + Normaliza** | Estrutura de entrada já funciona |
| **Tratamento de Áudio** | Cliente pode enviar áudio para agendar |
| **Switch de Origem** | Importante para saber tipo de mensagem |
| **Redis Memory** | Manter contexto de conversas |
| **AI Agent** | Core do bot inteligente |
| **OpenAI LLM** | Motor de IA |

### ❌ **O que REMOVER:**

| Component | Por quê |
|-----------|---------|
| **Vector Store Supabase** | Não precisamos de base de conhecimento complexa |
| **Tools Calculator/Think** | Não são relevantes para agendamento |
| **Tool Workflow** | Se não usar sub-workflows |
| **Tratamento de Imagens/Docs** | Cliente não precisa enviar docs para agendar |
| **Prompt da Axio** | Trocar pelo prompt do Gestto |

### 🆕 **O que ADICIONAR:**

| Component | Função |
|-----------|---------|
| **Tool "Consultar API Gestto"** | Buscar serviços, profissionais, horários |
| **Tool "Criar Agendamento"** | Enviar POST /api/bot/processar/ |
| **Node "Formatar Resposta"** | Processar resposta do Django |
| **Configurações no Normaliza** | URLs e API Keys do Gestto |

---

## 🔧 Passo a Passo da Adaptação

### **1. Manter Estrutura Base**

```
Webhook1
  ↓
Normaliza (+ config Gestto)
  ↓
Switch de Origem
  ├─ Audio → Converter → OpenAI (transcrever)
  └─ Texto → AI Agent
```

### **2. Configurar "Normaliza"**

Adicionar ao node "Normaliza" (Set):

```json
{
  "telefone": "{{ $json.body.data.key.remoteJid }}",
  "mensagem": "{{ $json.body.data.message.conversation }}",
  "instance": {
    "Name": "AxioAtendimento",
    "Apikey": "sua-evolution-key",
    "Server_url": "https://evolution.axiodev.cloud"
  },
  "gestto": {
    "api_url": "https://axiogestto.com",
    "api_key": "sua-gestto-key"
  }
}
```

### **3. Atualizar Prompt do AI Agent**

**SUBSTITUIR** o prompt atual por:

```
## IDENTIDADE
Você é o Assistente Inteligente do Gestto, especialista em agendamentos.

Data atual: {{ $now.setZone("America/Recife").toFormat("dd/MM/yyyy") }}
({{ $now.setZone("America/Recife").toFormat("cccc", { locale: 'pt-BR' }) }})

## CLASSIFICAÇÃO DE INTENÇÕES
Classifique a mensagem em UMA das intenções:
- **agendar** → cliente quer marcar horário
- **cancelar** → quer cancelar agendamento
- **consultar** → quer ver horários disponíveis, preços, serviços
- **duvida** → perguntas gerais, saudação
- **confirmacao** → confirmar agendamento pendente

## INFORMAÇÕES DISPONÍVEIS (via tools)
Você tem acesso às seguintes tools:
- **consultarServicos** → lista serviços, preços e duração
- **consultarProfissionais** → lista profissionais
- **consultarHorarios** → horários de funcionamento
- **criarAgendamento** → efetuar o agendamento

## FLUXO DE AGENDAMENTO
1. Cliente demonstra interesse
2. Pergunte: serviço desejado
3. Pergunte: data preferida
4. Pergunte: horário preferido
5. Confirme: nome do cliente
6. Use tool "criarAgendamento"

## ESTILO
- Responda em até 3-4 linhas
- Tom amigável e profissional
- Use 1 emoji quando apropriado
- Sempre confirme antes de agendar

## EXEMPLO - Agendamento
Cliente: "Quero agendar corte"
Você: "Ótimo! 💈 Temos corte de cabelo por R$ 50 (30 min). Qual dia você prefere?"

Cliente: "Amanhã"
Você: "Perfeito! Qual horário fica melhor pra você?"

Cliente: "14h"
Você: "Confirmando: Corte de cabelo amanhã às 14h. Qual seu nome completo?"

Cliente: "João Silva"
Você: *usa tool criarAgendamento*
"✅ Agendamento confirmado, João! Corte de cabelo em [data] às 14h. Te enviei a confirmação no WhatsApp."

## FORMATO DE SAÍDA
Retorne apenas o texto da resposta ao cliente.
Não retorne JSON ou explicações técnicas.
```

### **4. Criar Tools para o AI Agent**

Você vai precisar criar 2 sub-workflows que o AI Agent vai chamar:

#### **Tool 1: "Consultar Info Gestto"**

```
Webhook (recebe parâmetro "tipo": servicos | profissionais | horarios)
  ↓
Switch (por tipo)
  ├─ servicos → GET /api/n8n/servicos/
  ├─ profissionais → GET /api/n8n/profissionais/
  └─ horarios → GET /api/n8n/horarios-funcionamento/
  ↓
Return (JSON formatado para IA)
```

#### **Tool 2: "Criar Agendamento Gestto"**

```
Webhook (recebe: telefone, servico, profissional, data, hora)
  ↓
POST /api/bot/processar/
  Body: {
    "telefone": "...",
    "mensagem_original": "...",
    "intencao": "agendar",
    "dados": {
      "servico": "...",
      "profissional": "...",
      "data": "...",
      "hora": "..."
    }
  }
  ↓
Return (resposta do Django)
```

### **5. Conectar Tools ao AI Agent**

No node "AI Agent":
1. Adicionar **Tool Workflow**
2. Apontar para o workflow "Consultar Info Gestto"
3. Adicionar outro **Tool Workflow**
4. Apontar para o workflow "Criar Agendamento Gestto"

---

## 📝 Checklist de Implementação

### Fase 1 - Preparação
- [ ] Duplicar workflow "AtendimentoAxio" → "BotAgendamentoGestto"
- [ ] Atualizar node "Normaliza" com configs do Gestto
- [ ] Atualizar prompt do AI Agent

### Fase 2 - Criar Sub-Workflows
- [ ] Criar workflow "Gestto - Consultar Info"
- [ ] Criar workflow "Gestto - Criar Agendamento"
- [ ] Testar ambos workflows individualmente

### Fase 3 - Integração
- [ ] Adicionar Tool Workflows ao AI Agent
- [ ] Conectar tools
- [ ] Remover tools desnecessários (Calculator, etc)

### Fase 4 - Limpeza
- [ ] Remover nodes de Imagem/Documento
- [ ] Remover Vector Store Supabase
- [ ] Manter apenas Audio + Texto

### Fase 5 - Testes
- [ ] Testar saudação
- [ ] Testar consulta de serviços
- [ ] Testar agendamento completo
- [ ] Testar áudio

---

## 🚀 Abordagem Recomendada

**OPÇÃO 1 - Mais Simples (Recomendado):**
- Não usar o workflow "AtendimentoAxio" inteiro
- Criar um workflow novo mais limpo
- Aproveitar apenas a estrutura de Webhook + Normaliza + AI Agent
- Focar só em texto (sem áudio por enquanto)

**OPÇÃO 2 - Adaptação Completa:**
- Usar o workflow existente
- Remover partes desnecessárias
- Adicionar tools do Gestto
- Manter suporte a áudio

---

## ❓ Qual abordagem você prefere?

1. **Simples e Rápida:** Criar workflow novo limpo focado em agendamento
2. **Completa:** Adaptar o "AtendimentoAxio" mantendo áudio e memória

**Me diga qual prefere que eu crio o template específico!** 🎯
