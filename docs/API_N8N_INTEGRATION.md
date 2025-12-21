# 🤖 Guia de Integração API n8n - Axio Gestto

## ✅ Status da API

**A API está PRONTA para integração com n8n!**

### ✅ O que está implementado:

1. **Autenticação segura** - API Key + Empresa ID
2. **Rate Limiting** - 500 req/hora por empresa
3. **Logging completo** - Todas as interações registradas
4. **4 intenções** - agendar, cancelar, consultar, confirmar
5. **Validações** - Conflitos, horários passados, disponibilidade
6. **Respostas formatadas** - WhatsApp-friendly

### ⚠️ Pontos de atenção:

- Certificado SSL auto-assinado (dev) - Use Let's Encrypt em produção
- Validação de telefone básica - Recomendo validar no n8n
- Horário de funcionamento hardcoded (8h-18h) - Pode precisar ajustar

---

## 🔑 Credenciais

### Endpoint
```
POST https://seu-dominio.com/api/bot/processar/
```

### Headers Obrigatórios
```http
X-API-Key: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw
X-Empresa-ID: 1
Content-Type: application/json
```

**⚠️ IMPORTANTE:** Guarde a `X-API-Key` em segredo no n8n (use credenciais)

---

## 📡 Formato das Requisições

### 1️⃣ Agendar

**Request:**
```json
{
  "telefone": "5511999998888",
  "mensagem_original": "Quero agendar corte amanhã 14h",
  "intencao": "agendar",
  "dados": {
    "servico": "corte de cabelo",
    "data": "2025-12-23",
    "hora": "14:00",
    "profissional": "João",
    "nome_cliente": "Maria Silva"
  }
}
```

**Campos:**
- `telefone` **(obrigatório)**: Telefone com DDI (5511999998888)
- `mensagem_original` (opcional): Mensagem original do WhatsApp
- `intencao` **(obrigatório)**: `"agendar"`
- `dados.servico` **(obrigatório)**: Nome do serviço (busca por similaridade)
- `dados.data` **(obrigatório)**: Data no formato `YYYY-MM-DD`
- `dados.hora` **(obrigatório)**: Hora no formato `HH:MM` (24h)
- `dados.profissional` (opcional): Nome do profissional (auto-seleciona se não informado)
- `dados.nome_cliente` (opcional): Nome do cliente (se novo)

**Response Sucesso (200):**
```json
{
  "sucesso": true,
  "mensagem": "✅ Agendamento confirmado!\n\n📅 Serviço: Corte de Cabelo\n👤 Profissional: João Silva\n🕐 Data: 23/12/2025 às 14:00\n💰 Valor: R$ 50.00\n📝 Código: A3B9C2\n\nPara cancelar: CANCELAR A3B9C2",
  "dados": {
    "agendamento_id": 123,
    "codigo": "A3B9C2",
    "data_hora": "23/12/2025 às 14:00",
    "valor": 50.0
  }
}
```

**Response Horário Ocupado (200):**
```json
{
  "sucesso": false,
  "mensagem": "Este horário já está ocupado! 😔\n\nHorários disponíveis para 23/12/2025:\n🕐 14:30  🕐 15:00  🕐 15:30",
  "horarios_alternativos": ["14:30", "15:00", "15:30"]
}
```

**Response Serviço Não Encontrado (200):**
```json
{
  "sucesso": false,
  "mensagem": "Não encontrei o serviço \"corte\". Serviços disponíveis: Corte de Cabelo, Barba, Sobrancelha"
}
```

---

### 2️⃣ Cancelar

**Request:**
```json
{
  "telefone": "5511999998888",
  "mensagem_original": "cancelar A3B9C2",
  "intencao": "cancelar",
  "dados": {
    "codigo": "A3B9C2"
  }
}
```

**Campos:**
- `telefone` **(obrigatório)**
- `intencao` **(obrigatório)**: `"cancelar"`
- `dados.codigo` **(obrigatório)**: Código do agendamento (6 caracteres)

**Response Sucesso (200):**
```json
{
  "sucesso": true,
  "mensagem": "✅ Agendamento cancelado com sucesso!\n\nCódigo: A3B9C2\nData: 23/12/2025 às 14:00\n\nEsperamos você em breve! 😊"
}
```

**Response Código Inválido (200):**
```json
{
  "sucesso": false,
  "mensagem": "Não encontrei agendamento com código A3B9C2. Verifique se digitou corretamente."
}
```

**Response Telefone Diferente (200):**
```json
{
  "sucesso": false,
  "mensagem": "Este agendamento não pertence a você!"
}
```

---

### 3️⃣ Consultar Horários

**Request:**
```json
{
  "telefone": "5511999998888",
  "mensagem_original": "quais horários disponíveis amanhã?",
  "intencao": "consultar",
  "dados": {
    "data": "2025-12-23",
    "profissional": "João"
  }
}
```

**Campos:**
- `telefone` **(obrigatório)**
- `intencao` **(obrigatório)**: `"consultar"`
- `dados.data` (opcional): Data `YYYY-MM-DD` (default: hoje)
- `dados.profissional` (opcional): Nome do profissional (default: todos)

**Response (200):**
```json
{
  "sucesso": true,
  "mensagem": "📅 Horários disponíveis em 23/12/2025:\n\n🕐 08:00  🕐 08:30  🕐 09:00\n🕐 09:30  🕐 10:00  🕐 10:30\n\nPara agendar, diga: \"Quero agendar [serviço] às [hora]\"",
  "horarios": ["08:00", "08:30", "09:00", "09:30", "10:00", "10:30"]
}
```

---

### 4️⃣ Confirmar

**Request:**
```json
{
  "telefone": "5511999998888",
  "mensagem_original": "confirmar A3B9C2",
  "intencao": "confirmar",
  "dados": {
    "codigo": "A3B9C2"
  }
}
```

**Campos:**
- `telefone` **(obrigatório)**
- `intencao` **(obrigatório)**: `"confirmar"`
- `dados.codigo` **(obrigatório)**: Código do agendamento

**Response (200):**
```json
{
  "sucesso": true,
  "mensagem": "✅ Agendamento confirmado!\n\nTe esperamos em 23/12/2025 às 14:00!"
}
```

---

## ⚠️ Erros

### Autenticação Falhou (401)
```json
{
  "detail": "X-API-Key não fornecida"
}
```

### Rate Limit Excedido (429)
```json
{
  "detail": "Request was throttled. Expected available in 3600 seconds."
}
```

### Erro Interno (500)
```json
{
  "sucesso": false,
  "mensagem": "Desculpe, ocorreu um erro ao processar sua solicitação.",
  "erro": "Detalhes do erro"
}
```

---

## 🧪 Testando a API

### cURL (Desenvolvimento Local)

```bash
# Agendar
curl -k -X POST https://localhost/api/bot/processar/ \
  -H "X-API-Key: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw" \
  -H "X-Empresa-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "5511999998888",
    "intencao": "agendar",
    "dados": {
      "servico": "corte",
      "data": "2025-12-25",
      "hora": "14:00",
      "nome_cliente": "Teste Bot"
    }
  }'

# Consultar horários
curl -k -X POST https://localhost/api/bot/processar/ \
  -H "X-API-Key: eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw" \
  -H "X-Empresa-ID: 1" \
  -H "Content-Type: application/json" \
  -d '{
    "telefone": "5511999998888",
    "intencao": "consultar",
    "dados": {
      "data": "2025-12-25"
    }
  }'
```

**Nota:** `-k` ignora certificado SSL auto-assinado (apenas dev!)

---

## 🔧 Configuração no n8n

### 1. Criar Credencial

1. **Settings** → **Credentials** → **Create New**
2. **Type**: Header Auth
3. **Name**: `Axio Gestto API`
4. **Headers**:
   ```json
   {
     "X-API-Key": "eoq4dvyfSDzKzXaanzijLF-LHfwoAqyhiJhJBaR0gjw",
     "X-Empresa-ID": "1"
   }
   ```

### 2. Node HTTP Request

**Configuração básica:**
- **Method**: POST
- **URL**: `https://seu-dominio.com/api/bot/processar/`
- **Authentication**: Header Auth (usar credencial criada)
- **Body Content Type**: JSON
- **Ignore SSL Issues**: ✅ (apenas dev!)

**Body:**
```json
{
  "telefone": "{{ $json.from }}",
  "mensagem_original": "{{ $json.body }}",
  "intencao": "{{ $json.intent }}",
  "dados": {{ $json.data }}
}
```

### 3. Workflow Exemplo

```
1. Webhook (WhatsApp)
   ↓
2. OpenAI/ChatGPT (extrair intenção e dados)
   ↓
3. Function (formatar para API)
   ↓
4. HTTP Request (Axio Gestto API)
   ↓
5. WhatsApp (enviar resposta)
```

**Function Node (exemplo):**
```javascript
// Extrair intenção e dados da resposta do ChatGPT
const message = $input.item.json.choices[0].message.content;
const data = JSON.parse(message); // ChatGPT deve retornar JSON

return {
  json: {
    telefone: $input.item.json.from,
    mensagem_original: $input.item.json.body,
    intencao: data.intencao,
    dados: data.dados
  }
};
```

---

## 📊 Logs e Monitoramento

### Ver logs no Django

```bash
# Logs em tempo real
docker-compose logs -f web

# Logs do Celery (tarefas async)
docker-compose logs -f celery
```

### Ver histórico de mensagens (Admin)

1. Acesse: `https://seu-dominio.com/admin/`
2. **Agendamentos** → **Logs de Mensagens Bot**
3. Filtros disponíveis:
   - Empresa
   - Status (sucesso/erro)
   - Data
   - Telefone

### Campos do Log:
- `empresa`: Qual empresa
- `telefone`: Cliente
- `mensagem_original`: Mensagem recebida
- `intencao_detectada`: Intenção interpretada
- `dados_extraidos`: Dados extraídos (JSON)
- `status`: sucesso, erro, parcial
- `resposta_enviada`: O que foi respondido
- `erro_detalhes`: Se houver erro
- `agendamento`: Vinculado se criado

---

## 🚨 Troubleshooting

### Erro: "Empresa não encontrada"
**Problema:** X-Empresa-ID inválido

**Solução:**
```bash
# Listar empresas disponíveis
docker exec -it gestao_web python manage.py shell
>>> from empresas.models import Empresa
>>> Empresa.objects.all().values('id', 'nome')
```

### Erro: "Serviço não encontrado"
**Problema:** Nome do serviço não existe ou está desativado

**Solução:**
1. Admin → **Empresas** → **Serviços**
2. Verificar se serviço existe e está `ativo=True`
3. Testar busca parcial (ex: "corte" encontra "Corte de Cabelo")

### Erro: "Profissional não encontrado"
**Problema:** Profissional não existe ou está desativado

**Solução:**
1. Admin → **Empresas** → **Profissionais**
2. Verificar `ativo=True`
3. Se não informar, sistema escolhe automaticamente

### Erro: "Data/hora inválida"
**Problema:** Formato incorreto

**Solução:**
- Data: `YYYY-MM-DD` (ex: `2025-12-25`)
- Hora: `HH:MM` 24h (ex: `14:30`)

### Rate Limit Atingido
**Problema:** Mais de 500 requests/hora

**Solução:**
- Aguardar 1 hora
- Ou ajustar em `config/settings.py:133`:
  ```python
  'bot_api': '1000/hour',  # Aumentar limite
  ```

---

## 🔐 Segurança - Checklist

- [ ] Trocar `X-API-Key` em produção (gerar nova)
- [ ] Usar HTTPS com certificado válido (Let's Encrypt)
- [ ] Não expor `X-API-Key` em logs do n8n
- [ ] Validar telefone no n8n (formato brasileiro)
- [ ] Rate limiting configurado (500 req/hora)
- [ ] Logs habilitados para auditoria
- [ ] Whitelist de IPs (opcional, via Nginx)

---

## 🎯 Próximos Passos

### Para integração completa:

1. **Criar empresa no sistema**
   ```bash
   docker exec -it gestao_web python manage.py shell
   >>> from empresas.models import Empresa
   >>> emp = Empresa.objects.create(nome="Minha Barbearia", cnpj="12345678000100")
   >>> emp.id  # Usar este ID no X-Empresa-ID
   ```

2. **Criar serviços**
   - Admin → Empresas → Serviços → Adicionar
   - Ex: Corte (R$ 50, 30min), Barba (R$ 30, 20min)

3. **Criar profissionais**
   - Admin → Empresas → Profissionais → Adicionar
   - Ex: João Silva, Maria Santos

4. **Configurar n8n workflow**
   - Webhook WhatsApp
   - OpenAI para extrair intenção
   - HTTP Request para API Axio
   - Resposta WhatsApp

5. **Testar fluxo completo**
   - Enviar mensagem WhatsApp
   - Verificar log no Admin
   - Confirmar agendamento criado

---

## 📞 Suporte

- **Documentação**: `API_N8N_INTEGRATION.md` (este arquivo)
- **Segurança**: `SECURITY.md`
- **Deploy**: `DEPLOY.md`
- **Issues**: Criar issue no repositório

---

## ✅ Checklist de Integração

- [ ] API rodando (`docker-compose up -d`)
- [ ] Health check retorna 200 (`curl http://localhost/health/`)
- [ ] Empresa criada no sistema
- [ ] Serviços cadastrados
- [ ] Profissionais cadastrados
- [ ] `X-API-Key` configurada no n8n
- [ ] `X-Empresa-ID` correto
- [ ] Workflow n8n configurado
- [ ] Teste de agendamento funcionando
- [ ] Teste de cancelamento funcionando
- [ ] Logs aparecendo no Admin

---

**A API está PRONTA! Bora integrar com n8n! 🚀**
