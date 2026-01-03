# 🔧 Instruções de Correção do Workflow n8n

## 1️⃣ Renomear API Key no Backend (JÁ FEITO)

✅ `N8N_API_KEY` foi renomeado para `GESTTO_API_KEY`

Atualize seu `.env` em produção:
```bash
# ANTES
N8N_API_KEY=sua-chave

# DEPOIS
GESTTO_API_KEY=sua-chave
```

---

## 2️⃣ Correções no Workflow n8n

### A) Atualizar Headers de Autenticação

Em **TODOS** os nodes HTTP Request que chamam a API Django:

❌ **ANTES:**
```json
{
  "name": "apikey",
  "value": "={{ $env.DJANGO_API_KEY }}"
}
```

✅ **DEPOIS:**
```json
{
  "name": "X-API-Key",
  "value": "={{ $env.DJANGO_API_KEY }}"
}
```

**Nodes afetados:**
- Buscar Profissionais
- Buscar Servicos
- Buscar Horarios
- Criar Agendamento

---

### B) Remover empresa_id dos Query Params

Nos 3 nodes de busca (Profissionais, Serviços, Horários):

❌ **REMOVER** o query parameter `empresa_id`
❌ **REMOVER** o header `empresa_id`

✅ Deixar apenas o header `X-API-Key`

A API detecta automaticamente a empresa pela chave.

---

### C) **CORREÇÃO CRÍTICA: Node "Consolidar Contexto"**

Este é o node que está dando erro. O código JavaScript precisa ser alterado para usar `$input.all()`:

**Node:** Consolidar Contexto
**Tipo:** Code (JavaScript)

✅ **NOVO CÓDIGO COMPLETO:**

```javascript
// Consolida todos os dados buscados da API
const dados = $('Normalizar Dados').item.json;

// Pega todos os inputs (3 nodes em paralelo)
const allInputs = $input.all();

// Extrai dados de cada node
let profissionais = [];
let servicos = [];
let horarios = [];

for (const input of allInputs) {
  if (input.json.profissionais) {
    profissionais = input.json.profissionais;
  }
  if (input.json.servicos) {
    servicos = input.json.servicos;
  }
  if (input.json.horarios) {
    horarios = input.json.horarios;
  }
}

// Formata dados para o agente
const contextoProfissionais = profissionais
  .map(p => `- ${p.nome} (ID: ${p.id})`)
  .join('\n');

const contextoServicos = servicos
  .map(s => `- ${s.nome}: R$ ${s.preco} (${s.duracao_minutos} min)${s.descricao ? ' - ' + s.descricao : ''}`)
  .join('\n');

const contextoHorarios = horarios
  .map(h => `${h.dia_semana_nome}: ${h.hora_abertura} às ${h.hora_fechamento}${h.intervalo_inicio ? ` (intervalo ${h.intervalo_inicio} às ${h.intervalo_fim})` : ''}`)
  .join('\n');

// Data/hora atual para contexto
const agora = new Date();
const dias = ['domingo', 'segunda', 'terça', 'quarta', 'quinta', 'sexta', 'sábado'];
const meses = ['janeiro', 'fevereiro', 'março', 'abril', 'maio', 'junho', 'julho', 'agosto', 'setembro', 'outubro', 'novembro', 'dezembro'];

const contextoTemporal = `Hoje é ${dias[agora.getDay()]}, ${agora.getDate()} de ${meses[agora.getMonth()]} de ${agora.getFullYear()}, ${agora.getHours()}:${String(agora.getMinutes()).padStart(2, '0')}`;

return [{
  json: {
    ...dados,
    profissionais: profissionais,
    servicos: servicos,
    horarios: horarios,
    contexto_profissionais: contextoProfissionais,
    contexto_servicos: contextoServicos,
    contexto_horarios: contextoHorarios,
    contexto_temporal: contextoTemporal
  }
}];
```

---

### D) Corrigir Payload do Agendamento

**Node:** Criar Agendamento
**Body JSON:**

✅ **CORRETO:**
```json
{
  "telefone": "{{ $json.telefone }}",
  "mensagem_original": "{{ $('Consolidar Contexto').item.json.mensagem }}",
  "intencao": "agendar",
  "dados": {
    "servico": "{{ $json.servico }}",
    "profissional": "{{ $json.profissional }}",
    "data": "{{ $json.data }}",
    "hora": "{{ $json.hora }}"
  }
}
```

**Mudanças:**
- ❌ Removido `nome_cliente` dos dados
- ✅ Usa `profissional` (nome) ao invés de `profissional_id`
- ❌ Removido `observacoes`

---

## 3️⃣ Fazer Deploy das Mudanças Backend

Após corrigir o workflow, certifique-se de fazer deploy do backend com a nova `GESTTO_API_KEY`:

```bash
# 1. Commitar mudanças
git add .
git commit -m "refactor: renomear N8N_API_KEY para GESTTO_API_KEY"
git push origin develop

# 2. Criar PR e fazer merge para main

# 3. Aguardar GitHub Actions deployar

# 4. Atualizar .env em produção
GESTTO_API_KEY=sua-chave-real-aqui
```

---

## 4️⃣ Testar

Após aplicar todas as correções:

1. Salvar o workflow no n8n
2. Ativar o workflow
3. Enviar mensagem de teste via WhatsApp:
   ```
   "Quero agendar um corte amanhã às 14h"
   ```

4. Verificar execução no n8n (não deve mais dar erro no "Consolidar Contexto")

---

## ✅ Checklist

- [ ] Atualizado headers de `apikey` para `X-API-Key`
- [ ] Removido `empresa_id` dos query params/headers
- [ ] Corrigido código JavaScript do "Consolidar Contexto" com `$input.all()`
- [ ] Corrigido payload do "Criar Agendamento"
- [ ] Deploy do backend feito
- [ ] `.env` em produção atualizado com `GESTTO_API_KEY`
- [ ] Workflow testado e funcionando

---

## 🆘 Troubleshooting

### Erro: "Node hasn't been executed"
- **Causa:** JavaScript tentando acessar node que não executou
- **Solução:** Usar `$input.all()` como mostrado acima

### Erro: "API Key inválida"
- **Causa:** Header está como `apikey` ao invés de `X-API-Key`
- **Solução:** Corrigir header em todos os HTTP Request nodes

### Erro: "empresa_id obrigatório"
- **Causa:** Endpoint antigo ainda esperando empresa_id
- **Solução:** Certificar que o backend deployado está atualizado
