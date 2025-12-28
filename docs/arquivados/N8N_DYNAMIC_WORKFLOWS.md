# 🔄 Workflows n8n Dinâmicos - Escaláveis para N Profissionais

## ⚠️ Problema Identificado

**Workflows da Brandão Barbearia:**
❌ Hard-coded para 2 profissionais (Pedro e Juan)
❌ Switch manual com 2 opções fixas
❌ Não escala para 3, 4, 5, 6+ profissionais

**Exemplo do workflow atual (ERRADO para SaaS):**

```javascript
// 3 - Agendamento Fixo.json (linha 47-97)
Switch →
  Case 1: profissional === "Pedro"  → Call workflow Pedro
  Case 2: profissional === "Juan"   → Call workflow Juan
// E se tiver mais profissionais? 🤔
```

---

## ✅ Solução: Workflows DINÂMICOS

### Princípio: **Buscar dados da API, não hard-codar**

```
❌ ERRADO (Estático):
Switch:
  - Pedro → workflow_pedro
  - Juan → workflow_juan

✅ CERTO (Dinâmico):
1. HTTP Request → GET /api/n8n/profissionais/?empresa_id=1
2. Loop pelos profissionais retornados
3. Match profissional da mensagem com lista da API
4. Executar ação genérica (não específica por profissional)
```

---

## 🏗️ Arquitetura do Workflow Dinâmico

### **Workflow Universal - Adaptável a N Profissionais**

```
┌─────────────────────────────────────────────────────────┐
│ 1. WEBHOOK TRIGGER                                       │
│    Recebe: empresa_id, mensagem, telefone               │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ 2. BUSCAR DADOS DA EMPRESA (HTTP Requests)              │
│    ┌──────────────────────────────────────┐            │
│    │ GET /api/n8n/profissionais/          │            │
│    │ Headers: { empresa_id: 1 }           │            │
│    │                                       │            │
│    │ Response:                             │            │
│    │ {                                     │            │
│    │   "profissionais": [                 │            │
│    │     {"id": 1, "nome": "Pedro"},      │            │
│    │     {"id": 2, "nome": "João"},       │            │
│    │     {"id": 3, "nome": "Maria"}       │ ← Dinâmico!│
│    │   ]                                   │            │
│    │ }                                     │            │
│    └──────────────────────────────────────┘            │
│                                                          │
│    GET /api/n8n/servicos/ (mesma lógica)                │
│    GET /api/n8n/horarios-funcionamento/                 │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ 3. PROCESSAR COM IA (OpenAI Agent)                      │
│    ┌──────────────────────────────────────┐            │
│    │ System Prompt DINÂMICO:              │            │
│    │                                       │            │
│    │ "Você é assistente da {{ $json.empresa.nome }}"   │
│    │                                       │            │
│    │ "Profissionais disponíveis:"         │            │
│    │ {{ $json.profissionais.map(p => p.nome).join(', ') }}│
│    │                                       │            │
│    │ "Serviços disponíveis:"              │            │
│    │ {{ $json.servicos.map(s => s.nome).join(', ') }}  │
│    └──────────────────────────────────────┘            │
│                                                          │
│    OpenAI extrai:                                       │
│    {                                                     │
│      "intencao": "agendar",                             │
│      "servico": "Corte",                                │
│      "profissional": "João",  ← Nome pode variar!       │
│      "data": "2025-12-23",                              │
│      "hora": "14:00"                                    │
│    }                                                     │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ 4. MATCH PROFISSIONAL (Code Node)                       │
│    ┌──────────────────────────────────────┐            │
│    │ const nomeIA = $json.profissional    │            │
│    │ const profissionais = $('Buscar').item.json.profissionais │
│    │                                       │            │
│    │ // Busca fuzzy (Pedro, Pedro Brandão, P. Brandão) │
│    │ const match = profissionais.find(p => │            │
│    │   normalizar(p.nome).includes(normalizar(nomeIA)) │
│    │ )                                     │            │
│    │                                       │            │
│    │ return [{                             │            │
│    │   json: {                             │            │
│    │     profissional_id: match?.id,      │            │
│    │     profissional_nome: match?.nome   │            │
│    │   }                                   │            │
│    │ }]                                    │            │
│    └──────────────────────────────────────┘            │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ 5. CONSULTAR DISPONIBILIDADE (HTTP)                     │
│    POST /api/n8n/horarios-disponiveis/                  │
│    {                                                     │
│      "data": "{{ $json.data }}",                        │
│      "profissional_id": {{ $json.profissional_id }},    │
│      "servico_id": {{ $json.servico_id }}               │
│    }                                                     │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ 6. CRIAR AGENDAMENTO (HTTP)                             │
│    POST /api/bot/processar/                             │
│    {                                                     │
│      "intencao": "agendar",                             │
│      "telefone": "{{ $json.telefone }}",                │
│      "dados": {                                         │
│        "servico": "{{ $json.servico }}",                │
│        "profissional_id": {{ $json.profissional_id }},  │
│        "data": "{{ $json.data }}",                      │
│        "hora": "{{ $json.hora }}"                       │
│      }                                                   │
│    }                                                     │
└─────────────────────────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────┐
│ 7. ENVIAR RESPOSTA (Evolution API)                      │
│    POST /message/sendText/{{ $json.instance_name }}     │
│    {                                                     │
│      "number": "{{ $json.telefone }}",                  │
│      "text": "{{ $json.mensagem_resposta }}"            │
│    }                                                     │
└─────────────────────────────────────────────────────────┘
```

---

## 🔨 Implementação Prática

### **1. Node: Buscar Profissionais (HTTP Request)**

```json
{
  "name": "Buscar Profissionais",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "GET",
    "url": "https://axiogestto.com/api/n8n/profissionais/",
    "authentication": "headerAuth",
    "options": {
      "queryParameters": {
        "parameters": [
          {
            "name": "empresa_id",
            "value": "={{ $json.empresa_id }}"
          }
        ]
      }
    },
    "headerParameters": {
      "parameters": [
        {
          "name": "apikey",
          "value": "sua-api-key-aqui"
        },
        {
          "name": "empresa_id",
          "value": "={{ $json.empresa_id }}"
        }
      ]
    }
  }
}
```

### **2. Node: OpenAI Agent (System Prompt Dinâmico)**

```javascript
{
  "name": "Agente IA",
  "type": "@n8n/n8n-nodes-langchain.agent",
  "parameters": {
    "promptType": "define",
    "text": "={{ $json.mensagem }}",
    "options": {
      "systemMessage": `
## IDENTIDADE
Você é assistente virtual da empresa: {{ $('Buscar Empresa').item.json.nome }}

## PROFISSIONAIS DISPONÍVEIS
{{
  $('Buscar Profissionais').item.json.profissionais
    .map(p => '- ' + p.nome + ' (ID: ' + p.id + ')')
    .join('\\n')
}}

## SERVIÇOS DISPONÍVEIS
{{
  $('Buscar Servicos').item.json.servicos
    .map(s => '- ' + s.nome + ' (R$ ' + s.preco + ', ' + s.duracao_minutos + ' min)')
    .join('\\n')
}}

## HORÁRIOS DE FUNCIONAMENTO
{{
  $('Buscar Horarios').item.json.horarios
    .map(h => h.dia_semana_nome + ': ' + h.hora_abertura + ' às ' + h.hora_fechamento)
    .join('\\n')
}}

## REGRAS
- Se cliente mencionar profissional, agendar com ele
- Se NÃO mencionar, oferecer primeiro disponível
- Sempre confirmar: nome cliente, serviço, data, hora, profissional
`
    }
  }
}
```

### **3. Node: Match Profissional (Code)**

```javascript
{
  "name": "Match Profissional",
  "type": "n8n-nodes-base.code",
  "parameters": {
    "jsCode": `
// Dados do agente IA
const profissionalMencionado = $json.profissional || '';

// Lista de profissionais da API
const profissionais = $('Buscar Profissionais').item.json.profissionais;

// Função de normalização
function normalizar(texto) {
  return texto
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\\u0300-\\u036f]/g, '')
    .trim();
}

const nomeNormalizado = normalizar(profissionalMencionado);

// Buscar match
let profissionalMatch = null;

// 1. Tentar match exato
profissionalMatch = profissionais.find(p =>
  normalizar(p.nome) === nomeNormalizado
);

// 2. Se não achou, tentar match parcial
if (!profissionalMatch) {
  profissionalMatch = profissionais.find(p =>
    normalizar(p.nome).includes(nomeNormalizado) ||
    nomeNormalizado.includes(normalizar(p.nome))
  );
}

// 3. Se ainda não achou, pegar primeiro disponível
if (!profissionalMatch && profissionais.length > 0) {
  profissionalMatch = profissionais[0];
}

// Retornar
return [{
  json: {
    ...($json),
    profissional_id: profissionalMatch?.id,
    profissional_nome: profissionalMatch?.nome,
    profissional_encontrado: !!profissionalMatch
  }
}];
`
  }
}
```

### **4. Node: Consultar Disponibilidade (HTTP)**

```json
{
  "name": "Consultar Disponibilidade",
  "type": "n8n-nodes-base.httpRequest",
  "parameters": {
    "method": "POST",
    "url": "https://axiogestto.com/api/n8n/horarios-disponiveis/",
    "authentication": "headerAuth",
    "sendBody": true,
    "bodyParameters": {
      "parameters": [
        {
          "name": "data",
          "value": "={{ $json.data }}"
        },
        {
          "name": "profissional_id",
          "value": "={{ $json.profissional_id }}"
        },
        {
          "name": "servico_id",
          "value": "={{ $json.servico_id }}"
        }
      ]
    },
    "headerParameters": {
      "parameters": [
        {
          "name": "apikey",
          "value": "sua-api-key"
        },
        {
          "name": "empresa_id",
          "value": "={{ $('Webhook').item.json.empresa_id }}"
        }
      ]
    }
  }
}
```

---

## 📊 Comparação: Estático vs Dinâmico

### **❌ Workflow Estático (Brandão - NÃO USE)**

```
Profissionais: FIXOS (Pedro, Juan)
Nodes: 10+ (um para cada profissional)
Manutenção: DIFÍCIL (adicionar profissional = editar workflow)
Escalabilidade: ZERO (máx 2-3 profissionais)
Multi-tenant: IMPOSSÍVEL
```

**Código do Switch estático:**
```javascript
if (profissional === "Pedro") {
  // workflow específico do Pedro
} else if (profissional === "Juan") {
  // workflow específico do Juan
}
// E se adicionar Maria? Precisa editar workflow! ❌
```

### **✅ Workflow Dinâmico (Seu SaaS - USE)**

```
Profissionais: DINÂMICOS (da API)
Nodes: 5-7 (genéricos, reutilizáveis)
Manutenção: FÁCIL (adicionar profissional = só no Django)
Escalabilidade: INFINITA (1, 2, 3, 10, 100 profissionais)
Multi-tenant: SIM (um workflow para todas empresas)
```

**Código dinâmico:**
```javascript
// Busca profissionais da API
const profissionais = await api.get('/profissionais');

// Match automático
const match = profissionais.find(p =>
  p.nome.includes(nomeMencionado)
);

// Usa o ID encontrado
agendamento.profissional_id = match.id;
```

---

## 🎯 Estratégia de Implementação

### **Fase 1: Criar Workflow Base Universal (1 dia)**

```
1. Criar workflow "Bot Universal v1"
2. Nodes:
   ✅ Webhook Trigger
   ✅ HTTP: Buscar Empresa
   ✅ HTTP: Buscar Profissionais
   ✅ HTTP: Buscar Serviços
   ✅ Code: Match Profissional
   ✅ Agent: OpenAI (prompt dinâmico)
   ✅ HTTP: Criar Agendamento
   ✅ HTTP: Enviar Resposta
3. Testar com 1 empresa
```

### **Fase 2: Parametrizar por Empresa (2-3 horas)**

```
1. Adicionar node "Set Empresa"
   - Extrai empresa_id do webhook
   - Injeta em todos os HTTP requests

2. Testar com 2-3 empresas diferentes
   - Empresa 1: 1 profissional
   - Empresa 2: 3 profissionais
   - Empresa 3: 6 profissionais

3. Validar que funciona para todos
```

### **Fase 3: Otimizações (1 dia)**

```
1. Cache de dados da empresa (evitar buscar toda hora)
2. Tratamento de erros
3. Fallbacks
4. Mensagens personalizadas por empresa
```

---

## 💡 Dicas Importantes

### **1. NUNCA hard-code dados no workflow**

❌ **ERRADO:**
```javascript
const profissionais = ["Pedro", "Juan"];
```

✅ **CERTO:**
```javascript
const profissionais = await $http.get('/api/n8n/profissionais/');
```

### **2. Use IDs, não nomes**

❌ **ERRADO:**
```javascript
agendamento.profissional = "Pedro Brandão";
```

✅ **CERTO:**
```javascript
agendamento.profissional_id = 1; // ID do banco
```

### **3. Normalize strings antes de comparar**

```javascript
function normalizar(texto) {
  return texto
    .toLowerCase()
    .normalize('NFD')  // Remove acentos
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, ' ')  // Normaliza espaços
    .trim();
}

// "Pedro Brandão" === "pedro brandao" ✅
```

### **4. Sempre tenha fallback**

```javascript
const match = profissionais.find(p => ...);

if (!match) {
  // Opção 1: Pegar primeiro disponível
  match = profissionais[0];

  // Opção 2: Perguntar ao cliente
  return "Qual profissional você prefere? " +
         profissionais.map(p => p.nome).join(', ');
}
```

---

## 🚀 Resultado Final

Com workflow dinâmico, você terá:

✅ **1 workflow** para **TODAS as empresas**
✅ **1 workflow** para **1, 2, 3, 10, 100 profissionais**
✅ **Adicionar profissional** = só no Django (sem tocar n8n)
✅ **Manutenção** centralizada
✅ **Escalabilidade** infinita

### **Exemplo Real:**

```
Empresa 1 (Plano Essencial):
- 1 profissional → Workflow funciona ✅

Empresa 2 (Plano Profissional):
- 3 profissionais → Workflow funciona ✅

Empresa 3 (Plano Premium):
- 6 profissionais → Workflow funciona ✅

Empresa 4 (Custom):
- 15 profissionais → Workflow funciona ✅
```

**Sem modificar NADA no n8n!** 🎉

---

## 📝 Checklist de Implementação

- [ ] Criar workflow base com nodes genéricos
- [ ] Implementar busca dinâmica de profissionais
- [ ] Implementar match fuzzy de nomes
- [ ] Testar com 1 profissional
- [ ] Testar com 3 profissionais
- [ ] Testar com 6 profissionais
- [ ] Adicionar tratamento de erros
- [ ] Documentar workflow
- [ ] Exportar como template

---

## 🎁 Bônus: Template Pronto

Vou criar um template de workflow n8n universal para você adaptar. Quer que eu crie agora?
