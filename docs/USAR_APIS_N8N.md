# Como Usar as APIs Django no n8n

## Autenticação

Todas as APIs usam **API Key Authentication**.

**Header obrigatório:**
```
apikey: SUA_CHAVE_AQUI
```

A mesma chave configurada no `.env`:
```
N8N_API_KEY=eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

---

## URLs Base

**Desenvolvimento Local:**
```
http://127.0.0.1:8000
```

**Produção (quando fizer deploy):**
```
https://seu-dominio.com
```

---

## 1. API de Serviços

**Substitui:** Google Sheets Tool `serviTool` (aba "Serviços")

### Endpoint
```
GET /api/n8n/servicos/
```

### Headers
```
apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

### Response
```json
{
  "sucesso": true,
  "total": 5,
  "servicos": [
    {
      "id": 1,
      "nome": "Corte de Cabelo",
      "descricao": "Corte masculino tradicional",
      "preco": "40.00",
      "duracao_minutos": 30
    },
    {
      "id": 2,
      "nome": "Barba",
      "descricao": "Barba completa",
      "preco": "25.00",
      "duracao_minutos": 20
    },
    {
      "id": 3,
      "nome": "Corte + Barba",
      "descricao": "Combo completo",
      "preco": "55.00",
      "duracao_minutos": 45
    }
  ]
}
```

### Uso no n8n

**Node: HTTP Request**
```
Method: GET
URL: http://127.0.0.1:8000/api/n8n/servicos/
Authentication: None (usar Header)
Headers:
  - Name: apikey
    Value: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

**Acessar dados:**
```
{{ $json.servicos }}                    // Lista completa
{{ $json.servicos[0].nome }}            // Primeiro serviço
{{ $json.servicos[0].duracao_minutos }} // Duração em minutos
```

---

## 2. API de Profissionais

**Substitui:** Verificação manual de profissionais

### Endpoint
```
GET /api/n8n/profissionais/
```

### Headers
```
apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

### Response
```json
{
  "sucesso": true,
  "total": 2,
  "profissionais": [
    {
      "id": 1,
      "nome": "Pedro Brandão",
      "email": "pedro@barbearia.com",
      "telefone": "87999998888",
      "servicos": ["Corte de Cabelo", "Barba", "Corte + Barba"],
      "cor_hex": "#1e3a8a"
    },
    {
      "id": 2,
      "nome": "Juan Alves",
      "email": "juan@barbearia.com",
      "telefone": "87999997777",
      "servicos": ["Corte de Cabelo", "Barba"],
      "cor_hex": "#3b82f6"
    }
  ]
}
```

---

## 3. API de Horários de Funcionamento

**Substitui:** Google Sheets Tool `horarios` (aba "horarios")

### Endpoint
```
GET /api/n8n/horarios-funcionamento/
GET /api/n8n/horarios-funcionamento/?dia_semana=0
```

### Query Parameters
- `dia_semana` (opcional): 0-6 (0=segunda, 6=domingo)

### Headers
```
apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

### Response
```json
{
  "sucesso": true,
  "total": 6,
  "horarios": [
    {
      "dia_semana": 0,
      "dia_semana_nome": "Segunda-feira",
      "hora_abertura": "09:00",
      "hora_fechamento": "18:00",
      "intervalo_inicio": "12:00",
      "intervalo_fim": "13:00"
    },
    {
      "dia_semana": 1,
      "dia_semana_nome": "Terça-feira",
      "hora_abertura": "09:00",
      "hora_fechamento": "18:00",
      "intervalo_inicio": "12:00",
      "intervalo_fim": "13:00"
    },
    ...
  ]
}
```

### Uso no n8n

**Consultar horário de hoje:**
```javascript
// Code node - Calcular dia da semana
const hoje = new Date();
const diaSemana = hoje.getDay(); // 0-6 (domingo=0)
const diaSemanaBr = (diaSemana + 6) % 7; // Converter para 0=segunda

return [{ json: { dia_semana: diaSemanaBr } }];
```

**HTTP Request:**
```
URL: http://127.0.0.1:8000/api/n8n/horarios-funcionamento/?dia_semana={{ $json.dia_semana }}
```

---

## 4. API de Datas Especiais

**Substitui:** Google Sheets Tool `datas_especiais` (aba "datas_especiais")

### Endpoint
```
GET /api/n8n/datas-especiais/
GET /api/n8n/datas-especiais/?data_inicio=2025-12-01&data_fim=2025-12-31
GET /api/n8n/datas-especiais/?tipo=feriado
```

### Query Parameters
- `data_inicio` (opcional): YYYY-MM-DD
- `data_fim` (opcional): YYYY-MM-DD
- `tipo` (opcional): `feriado` ou `especial`

### Headers
```
apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

### Response
```json
{
  "sucesso": true,
  "total": 3,
  "datas_especiais": [
    {
      "data": "2025-12-25",
      "data_formatada": "25/12/2025",
      "descricao": "Natal",
      "tipo": "feriado",
      "tipo_display": "Feriado - Fechado",
      "hora_abertura": null,
      "hora_fechamento": null
    },
    {
      "data": "2025-12-24",
      "data_formatada": "24/12/2025",
      "descricao": "Véspera de Natal",
      "tipo": "especial",
      "tipo_display": "Horário Especial",
      "hora_abertura": "09:00",
      "hora_fechamento": "14:00"
    }
  ]
}
```

---

## 5. API de Horários Disponíveis

**Substitui:** Lógica de verificação de horários no n8n

### Endpoint
```
POST /api/n8n/horarios-disponiveis/
```

### Headers
```
Content-Type: application/json
apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

### Body
```json
{
  "data": "2025-12-23",
  "profissional_id": 1,
  "servico_id": 2
}
```

**Campos:**
- `data` (obrigatório): YYYY-MM-DD
- `profissional_id` (opcional): ID do profissional
- `servico_id` (opcional): ID do serviço (para calcular duração)

### Response - Horários Disponíveis
```json
{
  "sucesso": true,
  "data": "2025-12-23",
  "data_formatada": "23/12/2025",
  "dia_semana": "Segunda-feira",
  "profissional": "Pedro Brandão",
  "servico": "Corte + Barba",
  "duracao_minutos": 45,
  "total_horarios": 12,
  "horarios_disponiveis": [
    "09:00",
    "09:30",
    "10:00",
    "10:30",
    "11:00",
    "11:30",
    "14:00",
    "14:30",
    "15:00",
    "15:30",
    "16:00",
    "16:30"
  ]
}
```

### Response - Fechado (Feriado)
```json
{
  "sucesso": true,
  "data": "2025-12-25",
  "dia_semana": "Quarta-feira",
  "mensagem": "Fechado: Natal",
  "horarios_disponiveis": []
}
```

### Uso no n8n

**Node: HTTP Request**
```
Method: POST
URL: http://127.0.0.1:8000/api/n8n/horarios-disponiveis/
Authentication: None (usar Header)
Headers:
  - Name: apikey
    Value: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
  - Name: Content-Type
    Value: application/json
Body Type: JSON
Body:
{
  "data": "{{ $json.data_agendamento }}",
  "profissional_id": {{ $json.profissional_id }},
  "servico_id": {{ $json.servico_id }}
}
```

**Formatar resposta para IA:**
```javascript
// Code node - Formatar horários para o agente
const horarios = $json.horarios_disponiveis;

if (horarios.length === 0) {
  return [{
    json: {
      mensagem: `Não há horários disponíveis em ${$json.data_formatada}`
    }
  }];
}

// Mostrar apenas primeiros 5 horários
const primeirosHorarios = horarios.slice(0, 5).join(', ');
const mensagem = `Horários disponíveis em ${$json.data_formatada}:\n${primeirosHorarios}${horarios.length > 5 ? ` e mais ${horarios.length - 5} opções` : ''}`;

return [{
  json: {
    mensagem: mensagem,
    horarios_completos: horarios
  }
}];
```

---

## 6. API de Agendamento (já existe)

**Endpoint existente:** `/api/bot/processar/`

Ver documentação em: `agendamentos/bot_api.py`

---

## Como Adaptar o Workflow n8n

### Workflow 2 - Agente de Agendamento

**ANTES (Google Sheets):**
```
┌──────────────────┐
│ Google Sheets    │
│ Tool: serviTool  │ → Consulta aba "Serviços"
└──────────────────┘

┌──────────────────┐
│ Google Sheets    │
│ Tool: horarios   │ → Consulta aba "horarios"
└──────────────────┘

┌──────────────────┐
│ Google Sheets    │
│ Tool: datas_esp  │ → Consulta aba "datas_especiais"
└──────────────────┘
```

**DEPOIS (Django API):**
```
┌──────────────────┐
│ HTTP Request     │
│ GET /servicos    │ → Retorna JSON com serviços
└──────────────────┘

┌──────────────────┐
│ HTTP Request     │
│ GET /horarios    │ → Retorna JSON com horários
└──────────────────┘

┌──────────────────┐
│ HTTP Request     │
│ GET /datas-esp   │ → Retorna JSON com feriados
└──────────────────┘

┌──────────────────┐
│ HTTP Request     │
│ POST /horarios-  │ → Retorna horários disponíveis
│      disponiveis │    (substitui lógica complexa)
└──────────────────┘
```

### Passos para Adaptar

#### 1. Remover Google Sheets Tools

No workflow **"2- Agente de Agendamento"**:
- Deletar node `serviTool` (Google Sheets)
- Deletar node `horarios` (Google Sheets)
- Deletar node `datas_especiais` (Google Sheets)

#### 2. Adicionar HTTP Request Nodes

**Node 1: Listar Serviços**
```
Name: API - Serviços
Type: HTTP Request
Method: GET
URL: http://127.0.0.1:8000/api/n8n/servicos/
Headers:
  apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

**Node 2: Horários Funcionamento**
```
Name: API - Horários
Type: HTTP Request
Method: GET
URL: http://127.0.0.1:8000/api/n8n/horarios-funcionamento/
Headers:
  apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

**Node 3: Datas Especiais**
```
Name: API - Datas Especiais
Type: HTTP Request
Method: GET
URL: http://127.0.0.1:8000/api/n8n/datas-especiais/
Headers:
  apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
```

**Node 4: Horários Disponíveis**
```
Name: API - Verificar Disponibilidade
Type: HTTP Request
Method: POST
URL: http://127.0.0.1:8000/api/n8n/horarios-disponiveis/
Headers:
  apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
  Content-Type: application/json
Body:
{
  "data": "{{ $json.data }}",
  "profissional_id": {{ $json.profissional_id }},
  "servico_id": {{ $json.servico_id }}
}
```

#### 3. Conectar ao Agente IA

Os HTTP Requests podem ser usados como **Tools** no Langchain Agent:

**Opção A: Tool Workflow**
- Criar sub-workflow que chama a API
- Usar como tool no agente principal

**Opção B: HTTP Request Tool**
- Usar HTTP Request nodes diretamente como tools
- Configurar descrição para o agente entender quando usar

---

## Testando as APIs

### Via curl (linha de comando)

**Listar serviços:**
```bash
curl -H "apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw" \
  http://127.0.0.1:8000/api/n8n/servicos/
```

**Horários disponíveis:**
```bash
curl -X POST \
  -H "apikey: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw" \
  -H "Content-Type: application/json" \
  -d '{"data": "2025-12-23", "profissional_id": 1}' \
  http://127.0.0.1:8000/api/n8n/horarios-disponiveis/
```

### Via Postman

1. Criar nova Request
2. Method: GET ou POST
3. URL: `http://127.0.0.1:8000/api/n8n/servicos/`
4. Headers → Add:
   - Key: `apikey`
   - Value: `eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw`
5. Send

### Via n8n (teste)

1. Criar workflow de teste
2. Add node "HTTP Request"
3. Configurar conforme acima
4. Execute node
5. Ver output em JSON

---

## Próximos Passos

1. ✅ **APIs criadas e funcionando**
2. 🔲 **Popular dados no Django Admin**
   - Cadastrar horários de funcionamento
   - Cadastrar feriados/datas especiais
3. 🔲 **Adaptar workflows n8n**
   - Substituir Google Sheets Tools
   - Testar integração completa
4. 🔲 **Implementar Follow-up Celery**
   - Substituir workflow 4 (n8n)
   - Notificações automáticas pelo Django

---

## Troubleshooting

### Erro: "Authentication credentials were not provided"
- Verificar se header `apikey` está presente
- Verificar valor da chave no `.env`

### Erro: "Empresa não encontrada"
- A API Key está vinculada a uma empresa
- Verificar configuração em `agendamentos/authentication.py`

### Erro 500
- Verificar logs do Django
- Rodar: `python manage.py runserver` e ver console

### Horários vazios
- Verificar se cadastrou horários de funcionamento no Admin
- Verificar se não é feriado
- Verificar se profissional está ativo
