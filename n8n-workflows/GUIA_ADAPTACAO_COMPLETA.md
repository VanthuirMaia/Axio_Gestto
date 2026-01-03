# 🔧 Guia de Adaptação Completa - AtendimentoAxio → BotAgendamentoGestto

## 📋 Pré-requisitos

- [ ] Deploy do backend Gestto concluído
- [ ] `GESTTO_API_KEY` configurada em produção
- [ ] URLs funcionando:
  - `https://axiogestto.com/api/n8n/servicos/`
  - `https://axiogestto.com/api/n8n/profissionais/`
  - `https://axiogestto.com/api/bot/processar/`
- [ ] Evolution API funcionando

---

## 🎯 FASE 1: Preparação (5 min)

### 1.1 Duplicar Workflow

1. No n8n, abra o workflow "AtendimentoAxio"
2. Clique em **"⋮"** (menu) → **"Duplicate"**
3. Renomeie para: **"BotAgendamentoGestto"**
4. Desative o workflow original (para não conflitar)

### 1.2 Atualizar Configurações no Node "Normaliza"

**Node:** Normaliza (Edit Fields / Set)

**ADICIONAR** estes campos (mantendo os existentes):

```
gestto_api_url = https://axiogestto.com
gestto_api_key = SUA_CHAVE_GESTTO_AQUI
```

**Exemplo completo:**
```javascript
{
  // Campos existentes (manter)
  "telefone": "{{ $json.body.data.key.remoteJid }}",
  "mensagem": "{{ $json.body.data.message.conversation }}",
  "instance": {
    "Name": "AxioAtendimento",
    "Apikey": "sua-evolution-key",
    "Server_url": "https://evolution.axiodev.cloud"
  },

  // NOVOS campos para Gestto
  "gestto_api_url": "https://axiogestto.com",
  "gestto_api_key": "sua-chave-gestto-aqui"
}
```

---

## 🎯 FASE 2: Criar Sub-Workflows (Tools) (20 min)

### 2.1 Tool 1: "Gestto - Consultar Serviços"

**Criar novo workflow:**

1. Nome: **"Gestto - Consultar Servicos"**
2. Adicionar nodes:

```
[Webhook]
  ↓
[HTTP Request - Buscar Serviços]
  ↓
[Code - Formatar para IA]
  ↓
[Respond to Workflow]
```

**Configuração detalhada:**

**Node 1: Webhook**
- Tipo: Workflow Webhook
- Webhook Path: `gestto-consultar-servicos`
- HTTP Method: POST

**Node 2: HTTP Request**
- Method: GET
- URL: `={{ $('Webhook').item.json.gestto_api_url }}/api/n8n/servicos/`
- Authentication: None
- Headers:
  ```
  X-API-Key = {{ $('Webhook').item.json.gestto_api_key }}
  ```

**Node 3: Code (Formatar para IA)**
```javascript
// Formatar serviços para a IA entender
const servicos = $json.servicos || [];

if (servicos.length === 0) {
  return [{
    json: {
      resposta: "Não há serviços cadastrados no momento."
    }
  }];
}

const listaServicos = servicos.map(s =>
  `- ${s.nome}: R$ ${s.preco} (${s.duracao_minutos} minutos)${s.descricao ? ' - ' + s.descricao : ''}`
).join('\n');

return [{
  json: {
    resposta: `Serviços disponíveis:\n\n${listaServicos}`
  }
}];
```

**Node 4: Respond to Workflow**
- Respond With: Text
- Response: `={{ $json.resposta }}`

**SALVAR E ATIVAR** o workflow.

---

### 2.2 Tool 2: "Gestto - Consultar Profissionais"

**Criar novo workflow:**

1. Nome: **"Gestto - Consultar Profissionais"**
2. Estrutura idêntica ao anterior, mas com endpoint diferente

**Node 2: HTTP Request**
- URL: `={{ $('Webhook').item.json.gestto_api_url }}/api/n8n/profissionais/`

**Node 3: Code**
```javascript
const profissionais = $json.profissionais || [];

if (profissionais.length === 0) {
  return [{
    json: {
      resposta: "Não há profissionais cadastrados."
    }
  }];
}

const listaProfissionais = profissionais.map(p =>
  `- ${p.nome}${p.especialidade ? ' (' + p.especialidade + ')' : ''}`
).join('\n');

return [{
  json: {
    resposta: `Profissionais disponíveis:\n\n${listaProfissionais}`
  }
}];
```

**SALVAR E ATIVAR** o workflow.

---

### 2.3 Tool 3: "Gestto - Consultar Horários"

**Criar novo workflow:**

1. Nome: **"Gestto - Consultar Horarios"**

**Node 2: HTTP Request**
- URL: `={{ $('Webhook').item.json.gestto_api_url }}/api/n8n/horarios-funcionamento/`

**Node 3: Code**
```javascript
const horarios = $json.horarios || [];

if (horarios.length === 0) {
  return [{
    json: {
      resposta: "Horários de funcionamento não cadastrados."
    }
  }];
}

const listaHorarios = horarios.map(h =>
  `${h.dia_semana_nome}: ${h.hora_abertura} às ${h.hora_fechamento}${h.intervalo_inicio ? ` (intervalo ${h.intervalo_inicio} às ${h.intervalo_fim})` : ''}`
).join('\n');

return [{
  json: {
    resposta: `Horários de funcionamento:\n\n${listaHorarios}`
  }
}];
```

**SALVAR E ATIVAR** o workflow.

---

### 2.4 Tool 4: "Gestto - Criar Agendamento" ⭐ PRINCIPAL

**Criar novo workflow:**

1. Nome: **"Gestto - Criar Agendamento"**

```
[Webhook]
  ↓
[Code - Validar Dados]
  ↓
[HTTP Request - POST /api/bot/processar/]
  ↓
[Code - Formatar Resposta]
  ↓
[Respond to Workflow]
```

**Node 1: Webhook**
- Path: `gestto-criar-agendamento`
- Method: POST

**Node 2: Code - Validar Dados**
```javascript
// Recebe da IA: servico, data, hora, profissional (opcional), nome_cliente
const params = $json;

// Validar campos obrigatórios
if (!params.servico) {
  throw new Error('Serviço não informado');
}

if (!params.data) {
  throw new Error('Data não informada');
}

if (!params.hora) {
  throw new Error('Hora não informada');
}

if (!params.nome_cliente) {
  throw new Error('Nome do cliente não informado');
}

if (!params.telefone) {
  throw new Error('Telefone não informado');
}

// Retornar dados validados
return [{
  json: {
    telefone: params.telefone,
    servico: params.servico,
    profissional: params.profissional || null,
    data: params.data,
    hora: params.hora,
    nome_cliente: params.nome_cliente,
    gestto_api_url: params.gestto_api_url,
    gestto_api_key: params.gestto_api_key
  }
}];
```

**Node 3: HTTP Request**
- Method: POST
- URL: `={{ $json.gestto_api_url }}/api/bot/processar/`
- Authentication: None
- Headers:
  ```
  X-API-Key = {{ $json.gestto_api_key }}
  Content-Type = application/json
  ```
- Body Type: **Expression** (importante!)
- Body:
```javascript
={{
  {
    "telefone": $json.telefone,
    "mensagem_original": "Agendamento via bot",
    "intencao": "agendar",
    "dados": {
      "servico": $json.servico,
      "profissional": $json.profissional,
      "data": $json.data,
      "hora": $json.hora
    }
  }
}}
```

**Node 4: Code - Formatar Resposta**
```javascript
const response = $json;

// Se deu erro
if (!response.sucesso) {
  return [{
    json: {
      resposta: response.mensagem || 'Erro ao criar agendamento. Tente novamente.'
    }
  }];
}

// Se deu certo
return [{
  json: {
    resposta: response.mensagem
  }
}];
```

**Node 5: Respond to Workflow**
- Response: `={{ $json.resposta }}`

**SALVAR E ATIVAR** o workflow.

---

## 🎯 FASE 3: Adaptar AI Agent (15 min)

### 3.1 Remover Tools Desnecessários

No workflow principal "BotAgendamentoGestto":

1. Abra o node **"AI Agent"**
2. Na seção **"Tools"**, remova:
   - ❌ Calculator
   - ❌ Think
   - ❌ Qualquer outro tool que não seja útil

### 3.2 Adicionar Tools do Gestto

No node **"AI Agent"**:

1. Clique em **"Add Tool"** → **"Call n8n Workflow"**
2. Configure:
   - **Name:** `consultarServicos`
   - **Description:** `Consulta lista de serviços disponíveis com preços e duração`
   - **Workflow:** Selecione "Gestto - Consultar Servicos"
   - **Fields to Send:** (vazio - envia tudo automaticamente)

3. Clique em **"Add Tool"** novamente
   - **Name:** `consultarProfissionais`
   - **Description:** `Consulta lista de profissionais disponíveis`
   - **Workflow:** "Gestto - Consultar Profissionais"

4. Mais um:
   - **Name:** `consultarHorarios`
   - **Description:** `Consulta horários de funcionamento do estabelecimento`
   - **Workflow:** "Gestto - Consultar Horarios"

5. E o principal:
   - **Name:** `criarAgendamento`
   - **Description:** `Cria um agendamento. Parâmetros obrigatórios: servico (nome), data (YYYY-MM-DD), hora (HH:MM), nome_cliente (string), telefone (string com DDD). Parâmetro opcional: profissional (nome)`
   - **Workflow:** "Gestto - Criar Agendamento"

### 3.3 Configurar passagem de dados para Tools

**IMPORTANTE:** Os tools precisam receber `gestto_api_url` e `gestto_api_key`.

No node **"AI Agent"**, antes da seção Tools, adicione:

**Fields to Send to All Tools:**
```
gestto_api_url = {{ $('Normaliza').item.json.gestto_api_url }}
gestto_api_key = {{ $('Normaliza').item.json.gestto_api_key }}
telefone = {{ $('Normaliza').item.json.telefone }}
```

---

## 🎯 FASE 4: Atualizar Prompt do AI Agent (10 min)

No node **"AI Agent"**, na opção **"Prompt"** ou **"System Message"**:

**SUBSTITUIR TODO O PROMPT** por:

```
## IDENTIDADE
Você é o Assistente Virtual do Gestto, especialista em agendamentos de serviços.

Você atende com naturalidade e eficiência, ajudando clientes a agendar serviços de forma rápida.

Data/hora atual: {{ $now.setZone("America/Recife").toFormat("dd/MM/yyyy HH:mm") }} ({{ $now.setZone("America/Recife").toFormat("cccc", { locale: 'pt-BR' }) }})

## CLASSIFICAÇÃO DE INTENÇÕES

Classifique a mensagem do cliente em UMA das intenções:

- **agendar** → cliente quer marcar um horário
- **cancelar** → quer cancelar agendamento existente
- **consultar** → quer saber horários, preços, serviços disponíveis
- **duvida** → pergunta geral, saudação, outra dúvida
- **confirmacao** → confirmar dados de agendamento

## TOOLS DISPONÍVEIS

Você tem acesso às seguintes ferramentas:

1. **consultarServicos** - Lista serviços com preços e duração
2. **consultarProfissionais** - Lista profissionais disponíveis
3. **consultarHorarios** - Horários de funcionamento
4. **criarAgendamento** - Efetua o agendamento (use APENAS quando tiver TODOS os dados)

## FLUXO DE AGENDAMENTO

Para criar um agendamento, você PRECISA coletar:

1. ✅ **Serviço** - Use consultarServicos para mostrar opções
2. ✅ **Data** - Em formato YYYY-MM-DD (ex: 2026-01-05)
3. ✅ **Hora** - Em formato HH:MM (ex: 14:00)
4. ✅ **Nome completo** do cliente
5. ⚠️ **Profissional** (opcional) - Se cliente não mencionar, pode deixar vazio

**IMPORTANTE:**
- Pergunte UMA coisa por vez
- Confirme todos os dados antes de usar criarAgendamento
- Normalize datas relativas:
  - "amanhã" → calcule a data
  - "próxima segunda" → calcule a data
  - "hoje" → use data atual

## REGRAS DE USO DE TOOLS

✅ **QUANDO USAR consultarServicos:**
- Cliente pergunta "quais serviços vocês fazem?"
- Cliente pergunta "quanto custa?"
- No início do agendamento (para mostrar opções)

✅ **QUANDO USAR criarAgendamento:**
- Você JÁ coletou: serviço, data, hora, nome_cliente
- Você JÁ confirmou os dados com o cliente
- NUNCA use sem confirmar antes

❌ **NUNCA:**
- Crie agendamento sem confirmar com cliente
- Invente dados que o cliente não informou
- Use criarAgendamento sem ter todos os dados obrigatórios

## ESTILO DE COMUNICAÇÃO

- Responda em até 3-4 linhas
- Tom amigável, profissional e objetivo
- Use 1 emoji por mensagem (quando apropriado)
- Conduza a conversa para o próximo passo
- Seja claro e direto

## EXEMPLOS DE CONVERSAS

**Exemplo 1 - Agendamento completo:**

Cliente: "Quero agendar um corte"
Você: *usa consultarServicos*
"Ótimo! Nosso corte de cabelo custa R$ 50 e leva 30 minutos. Qual dia você prefere? 💈"

Cliente: "Amanhã"
Você: "Perfeito! E que horário fica melhor pra você?"

Cliente: "14h"
Você: "Show! Só pra confirmar: corte de cabelo amanhã (05/01/2026) às 14:00. Qual seu nome completo?"

Cliente: "João Silva"
Você: *usa criarAgendamento com data="2026-01-05", hora="14:00", servico="Corte de Cabelo", nome_cliente="João Silva"*
"✅ Agendamento confirmado, João! Te espero amanhã às 14h. Até lá! 😊"

**Exemplo 2 - Consulta de horários:**

Cliente: "Vocês abrem no domingo?"
Você: *usa consultarHorarios*
"Estes são nossos horários de funcionamento:\n[resposta da tool]\n\nQuer agendar algum serviço? 😊"

**Exemplo 3 - Saudação:**

Cliente: "Oi"
Você: "Olá! 👋 Sou o assistente do Gestto. Posso te ajudar a agendar um serviço ou tirar alguma dúvida. Em que posso ajudar?"

## FORMATO DE SAÍDA

Retorne APENAS o texto da resposta ao cliente.
NÃO retorne JSON, listas técnicas ou explicações internas.
```

**SALVAR** as mudanças no AI Agent.

---

## 🎯 FASE 5: Limpeza (10 min)

### 5.1 Remover Vector Store Supabase

1. No workflow principal, localize o node **"Vector Store Supabase"**
2. Clique com botão direito → **Delete**
3. Remova também o node **"Embeddings OpenAI"** se houver

### 5.2 Remover Tratamento de Imagens/Documentos (OPCIONAL)

Se quiser simplificar (recomendado para começar):

1. Localize nodes:
   - "Envio de Imagens"
   - "Converter Imagem"
   - "Envio de Documentos1"
   - "Converter Arquivo1"

2. Delete todos

3. No **Switch de Origem**, remova as rotas para esses nodes

### 5.3 Manter Apenas Áudio + Texto

**Manter:**
- ✅ Mensagem de Audio
- ✅ Converter Áudio
- ✅ OpenAI (transcrição)
- ✅ Filtra Msg App (texto)

**Resultado:** Bot aceita mensagem de texto OU áudio.

---

## 🎯 FASE 6: Ajustar Conexões (5 min)

### 6.1 Verificar fluxo completo:

```
Webhook1
  ↓
Normaliza
  ↓
Switch de Origem
  ├─ Audio → Mensagem de Audio → Converter Áudio → OpenAI2 (transcrever) → AI Agent
  └─ Texto → AI Agent
      ↓
  [AI Agent usa tools conforme necessário]
      ↓
  Enviar Resposta WhatsApp
```

### 6.2 Conectar saída do AI Agent

1. A saída do **AI Agent** deve ir para um node que envia a resposta no WhatsApp
2. Localize o node de envio (provavelmente já existe no workflow original)
3. Certifique-se que está usando Evolution API

---

## 🎯 FASE 7: Testes (15 min)

### 7.1 Teste 1: Saudação

Envie no WhatsApp: `"Oi"`

**Esperado:** Bot responde com saudação amigável

### 7.2 Teste 2: Consulta de Serviços

Envie: `"Quais serviços vocês fazem?"`

**Esperado:** Bot usa tool consultarServicos e lista os serviços

### 7.3 Teste 3: Agendamento Completo

```
Você: "Quero agendar um corte"
Bot: [pergunta data]
Você: "Amanhã"
Bot: [pergunta hora]
Você: "14h"
Bot: [pergunta nome]
Você: "Seu Nome"
Bot: ✅ Confirmação do agendamento
```

### 7.4 Teste 4: Áudio

Envie um **áudio** dizendo: `"Quero agendar corte amanhã 14h"`

**Esperado:** Bot transcreve e processa normalmente

---

## 🎯 FASE 8: Ajustes Finais (10 min)

### 8.1 Configurar Redis (se ainda não configurado)

Se você já tem Redis configurado no workflow original, apenas certifique-se que está ativo.

Se não tem:
1. Pode remover os nodes de Redis por enquanto
2. O bot funcionará, mas sem memória de conversas anteriores

### 8.2 Configurar timeout de conversa

Localize o node **"Gera Timeout"** (Redis) - mantê-lo evita conversas infinitas.

---

## ✅ CHECKLIST FINAL

Antes de colocar em produção:

- [ ] Todos os 4 sub-workflows criados e ativados
- [ ] AI Agent com prompt do Gestto
- [ ] Tools conectadas ao AI Agent
- [ ] Configs do Gestto no node Normaliza
- [ ] Vector Store removido
- [ ] Imagens/Docs removidos (se optou por isso)
- [ ] Teste de saudação funcionando
- [ ] Teste de consulta funcionando
- [ ] Teste de agendamento completo funcionando
- [ ] Teste de áudio funcionando (se manteve)
- [ ] Workflow salvo e ativado

---

## 🆘 Troubleshooting

### Erro: "Tool não encontrada"
→ Certifique que os sub-workflows estão **ativados**

### Erro: "API Key inválida"
→ Verifique se `gestto_api_key` no Normaliza está correto

### Bot não envia resposta
→ Verifique conexão AI Agent → node de envio WhatsApp

### Áudio não funciona
→ Verifique se OpenAI2 está configurado com modelo que suporta transcrição (whisper-1)

---

## 🎉 Pronto!

Agora você tem um bot robusto com:
- ✅ Conversação natural com IA
- ✅ Suporte a áudio
- ✅ Memória de conversas (Redis)
- ✅ Integração completa com Gestto
- ✅ Agendamento automático

**Dúvidas em alguma fase?** Me avisa que eu te ajudo! 🚀
