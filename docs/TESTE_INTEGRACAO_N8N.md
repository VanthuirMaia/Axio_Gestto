# 🧪 Guia de Testes - Integração Gestto + n8n

## 🎯 Objetivo

Testar a integração completa entre:
- Django (Gestto)
- Evolution API (WhatsApp)
- n8n (Automação)

---

## ✅ Pré-requisitos

Antes de começar, certifique-se de ter:

- [ ] Django rodando (local ou produção)
- [ ] Evolution API configurada e rodando
- [ ] n8n instalado (VPS ou Cloud)
- [ ] Pelo menos 1 empresa cadastrada no Gestto
- [ ] OpenAI API Key com créditos

---

## 📋 Checklist de Configuração

### **1. Django (.env)**

```bash
# Verifique se está configurado:
SITE_URL=https://axiogestto.com  # ou http://localhost:8000
N8N_API_KEY=sua-chave-secreta-para-n8n
N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/bot-universal
EVOLUTION_API_URL=https://evolution.axiodev.cloud
EVOLUTION_API_KEY=sua-evolution-api-key
```

### **2. n8n (Template Importado)**

- [ ] Template `TEMPLATE_Bot_Universal_VPS_Simplificado.json` importado
- [ ] Node "⚙️ Configurações + Dados" editado com URLs e chaves
- [ ] Workflow salvo e **ATIVADO**
- [ ] URL do webhook copiada

### **3. Gestto (Empresa Configurada)**

- [ ] Empresa criada
- [ ] Assinatura ativa
- [ ] Pelo menos 1 profissional cadastrado
- [ ] Pelo menos 1 serviço cadastrado
- [ ] Horários de funcionamento configurados

---

## 🚀 Testes Passo a Passo

### **Teste 1: Validar Configuração do Django** ⚙️

#### **1.1 - Testar N8N_WEBHOOK_URL**

Abra o shell do Django:

```bash
python manage.py shell
```

Execute:

```python
from django.conf import settings

# Verificar se variáveis estão carregadas
print("N8N_WEBHOOK_URL:", settings.N8N_WEBHOOK_URL)
print("N8N_API_KEY:", settings.N8N_API_KEY[:10] + "..." if settings.N8N_API_KEY else "NÃO CONFIGURADO")
print("EVOLUTION_API_URL:", settings.EVOLUTION_API_URL)

# Deve imprimir os valores corretos
```

**Resultado Esperado:**
```
N8N_WEBHOOK_URL: https://seu-n8n.com/webhook/bot-universal
N8N_API_KEY: n19kq-oh-2...
EVOLUTION_API_URL: https://evolution.axiodev.cloud
```

❌ **Se retornar vazio:** Verifique o `.env` e reinicie o Django.

---

#### **1.2 - Testar Rota do Webhook**

No shell do Django:

```python
from django.urls import reverse

# Testar se rota existe
url = reverse('whatsapp_webhook_n8n', kwargs={'empresa_id': 1, 'secret': 'teste123'})
print("URL do webhook:", url)
# Deve imprimir: /api/webhooks/whatsapp-n8n/1/teste123/
```

**Resultado Esperado:**
```
URL do webhook: /api/webhooks/whatsapp-n8n/1/teste123/
```

✅ **Rota existe!**

---

### **Teste 2: Testar APIs n8n (Endpoints Django)** 📡

Estes são os endpoints que o n8n vai chamar para buscar dados.

#### **2.1 - Listar Profissionais**

**Usando curl:**

```bash
curl -X GET "http://localhost:8000/api/n8n/profissionais/?empresa_id=1" \
  -H "apikey: sua-chave-N8N_API_KEY" \
  -H "empresa_id: 1"
```

**Usando Postman/Insomnia:**
- Method: `GET`
- URL: `http://localhost:8000/api/n8n/profissionais/?empresa_id=1`
- Headers:
  - `apikey`: `sua-chave-N8N_API_KEY`
  - `empresa_id`: `1`

**Resultado Esperado:**
```json
{
  "profissionais": [
    {
      "id": 1,
      "nome": "Pedro Silva",
      "telefone": "11999999999",
      "email": "pedro@example.com",
      "foto_url": null,
      "especialidades": [],
      "ativo": true
    }
  ],
  "total": 1
}
```

✅ **API funcionando!**

---

#### **2.2 - Listar Serviços**

```bash
curl -X GET "http://localhost:8000/api/n8n/servicos/?empresa_id=1" \
  -H "apikey: sua-chave-N8N_API_KEY" \
  -H "empresa_id: 1"
```

**Resultado Esperado:**
```json
{
  "servicos": [
    {
      "id": 1,
      "nome": "Corte de Cabelo",
      "descricao": "",
      "preco": "30.00",
      "duracao_minutos": 30,
      "ativo": true
    }
  ],
  "total": 1
}
```

✅ **API funcionando!**

---

#### **2.3 - Listar Horários de Funcionamento**

```bash
curl -X GET "http://localhost:8000/api/n8n/horarios-funcionamento/?empresa_id=1" \
  -H "apikey: sua-chave-N8N_API_KEY" \
  -H "empresa_id: 1"
```

**Resultado Esperado:**
```json
{
  "horarios": [
    {
      "dia_semana": 1,
      "dia_semana_nome": "Segunda-feira",
      "hora_abertura": "08:00",
      "hora_fechamento": "18:00",
      "ativo": true
    },
    ...
  ],
  "total": 5
}
```

✅ **APIs prontas!**

---

### **Teste 3: Testar n8n (Workflow Isolado)** 🤖

#### **3.1 - Testar Webhook do n8n**

Envie um payload de teste diretamente para o n8n:

```bash
curl -X POST "https://seu-n8n.com/webhook/bot-universal" \
  -H "Content-Type: application/json" \
  -d '{
    "empresa_id": 1,
    "empresa_nome": "Barbearia Teste",
    "instance": "teste_instance",
    "body": {
      "data": {
        "key": {
          "remoteJid": "5511999999999@s.whatsapp.net"
        },
        "pushName": "João Teste",
        "message": {
          "conversation": "Oi, quero agendar corte amanhã 14h"
        }
      }
    }
  }'
```

**Resultado Esperado:**
- Status: `200 OK`
- Body: `{ "success": true, "message": "Processado" }`

**Verifique no n8n:**
- Vá em "Executions" no n8n
- Deve aparecer uma execução recente
- Clique para ver o fluxo completo
- Verifique se passou por todos os nodes

✅ **n8n recebeu e processou!**

---

#### **3.2 - Verificar Logs de Execução**

No n8n, clique na execução e verifique:

**Node "⚙️ Configurações + Dados":**
```json
{
  "empresa_id": 1,
  "instance_name": "teste_instance",
  "telefone": "5511999999999",
  "mensagem": "Oi, quero agendar corte amanhã 14h",
  "nome_cliente": "João Teste"
}
```

**Node "Buscar Profissionais":**
```json
{
  "profissionais": [
    { "id": 1, "nome": "Pedro Silva" }
  ]
}
```

**Node "🌙 Luna IA":**
```json
{
  "choices": [
    {
      "message": {
        "content": "{\"intencao\": \"agendar\", ...}"
      }
    }
  ]
}
```

✅ **Workflow processando corretamente!**

---

### **Teste 4: Testar Webhook Intermediário (Django)** 🔐

Agora vamos testar se o Django recebe e encaminha corretamente.

#### **4.1 - Obter Secret da Empresa**

No shell do Django:

```python
from empresas.models import ConfiguracaoWhatsApp

config = ConfiguracaoWhatsApp.objects.get(empresa_id=1)
print("Secret:", config.webhook_secret)
print("Instance:", config.instance_name)
```

Copie o secret.

---

#### **4.2 - Simular Webhook da Evolution**

Simule um POST que a Evolution API faria:

```bash
curl -X POST "http://localhost:8000/api/webhooks/whatsapp-n8n/1/SEU-SECRET-AQUI/" \
  -H "Content-Type: application/json" \
  -d '{
    "instance": "empresa_barbearia_teste",
    "data": {
      "key": {
        "remoteJid": "5511999999999@s.whatsapp.net",
        "fromMe": false
      },
      "pushName": "João Teste",
      "message": {
        "conversation": "Oi, quero agendar corte amanhã 14h"
      }
    }
  }'
```

**Resultado Esperado:**
```json
{
  "success": true,
  "forwarded_to_n8n": true,
  "empresa": "Barbearia Teste"
}
```

**Verifique os logs do Django:**
```
INFO Webhook recebido: empresa=Barbearia Teste (ID=1), instance=empresa_barbearia_teste
INFO Webhook encaminhado para n8n com sucesso: empresa=Barbearia Teste
```

**Verifique no n8n:**
- Deve ter uma nova execução
- Verifique se processou corretamente

✅ **Django → n8n funcionando!**

---

### **Teste 5: Criar Instância WhatsApp** 📱

Agora vamos criar uma instância real para testar end-to-end.

#### **5.1 - Criar Instância**

Acesse o Gestto:
1. Login no sistema
2. Vá em "Configurações" → "WhatsApp"
3. Clique em "Criar Nova Instância"

**Verifique:**
- ✅ Instância criada
- ✅ QR Code apareceu
- ✅ URL do webhook configurada: `/api/webhooks/whatsapp-n8n/1/secret/`

---

#### **5.2 - Conectar WhatsApp**

1. Abra WhatsApp no celular
2. Vá em "Aparelhos Conectados"
3. Escaneie o QR Code
4. Aguarde conexão

**Verifique no Gestto:**
- Status deve mudar para "Conectado"
- Deve aparecer informações do WhatsApp conectado

✅ **WhatsApp conectado!**

---

### **Teste 6: Teste End-to-End Completo** 🎯

Agora vamos testar o fluxo COMPLETO: Cliente → WhatsApp → Evolution → Django → n8n → Resposta

#### **6.1 - Enviar Mensagem de Teste**

**Com outro celular** (ou peça para alguém), envie uma mensagem para o WhatsApp da empresa:

```
Oi
```

**Resultado Esperado:**
- Bot responde: "Olá! Sou a Luna, assistente virtual. Posso te ajudar a agendar um horário ou tirar alguma dúvida? 😊"

✅ **Bot respondeu!**

---

#### **6.2 - Testar Agendamento Incompleto**

Envie:
```
Quero cortar cabelo
```

**Resultado Esperado:**
- Bot pergunta: "Que legal! Para quando você quer agendar o corte? Temos disponibilidade amanhã e nos próximos dias 😊"

✅ **IA entendeu e está pedindo mais informações!**

---

#### **6.3 - Testar Agendamento Completo**

Envie:
```
Quero agendar corte amanhã 14h
```

**Resultado Esperado:**
- Bot cria agendamento e responde:
```
✅ Agendamento confirmado!

📅 Serviço: Corte de Cabelo
👤 Profissional: Pedro Silva
🕐 Data: 27/12/2025 às 14:00
💰 Valor: R$ 30,00

📝 Código: ABC123

Qualquer dúvida, estou por aqui! 😊
```

**Verifique no Gestto:**
- Vá em "Agendamentos"
- Deve aparecer o novo agendamento
- Cliente: João Teste (ou nome que você usou)
- Profissional: Pedro Silva
- Data/Hora: Amanhã 14h

✅ **AGENDAMENTO CRIADO! Sistema completo funcionando!** 🎉

---

### **Teste 7: Verificar Logs** 📊

#### **7.1 - Logs do Django**

Verifique o terminal onde Django está rodando:

```
INFO Webhook recebido: empresa=Barbearia Teste (ID=1), instance=empresa_barbearia_teste
INFO Webhook encaminhado para n8n com sucesso: empresa=Barbearia Teste
```

#### **7.2 - Logs do n8n**

No n8n:
1. Vá em "Executions"
2. Veja a execução mais recente
3. Clique para ver detalhes
4. Verifique cada node:
   - ✅ Webhook recebeu dados
   - ✅ Configurações extraiu empresa_id
   - ✅ APIs buscaram profissionais/serviços
   - ✅ IA processou mensagem
   - ✅ Agendamento criado
   - ✅ Resposta enviada

#### **7.3 - Logs da Evolution API**

Se tiver acesso aos logs da Evolution:

```
[INFO] Webhook sent to https://axiogestto.com/api/webhooks/whatsapp-n8n/1/...
[INFO] Message sent to 5511999999999
```

✅ **Logs OK em todos os sistemas!**

---

## 🔍 Testes de Casos Específicos

### **Teste 8: Múltiplos Profissionais**

**Pré-requisito:** Cadastre 3 profissionais no Gestto

Envie:
```
Quero agendar com a Maria
```

**Resultado Esperado:**
- Bot identifica "Maria" na lista de profissionais
- Agenda com Maria (não com outro profissional)

✅ **Match de nome funcionando!**

---

### **Teste 9: Serviço Específico**

Envie:
```
Quero fazer barba amanhã 10h
```

**Resultado Esperado:**
- Bot identifica serviço "Barba"
- Cria agendamento para Barba (não Corte)

✅ **Match de serviço funcionando!**

---

### **Teste 10: Horário Inválido**

Envie:
```
Quero agendar às 2h da manhã
```

**Resultado Esperado:**
- Bot identifica que está fora do horário de funcionamento
- Sugere horários válidos

---

### **Teste 11: Cancelamento** (Se implementado)

Envie:
```
CANCELAR ABC123
```

**Resultado Esperado:**
- Bot cancela o agendamento
- Confirma cancelamento

---

## ⚠️ Troubleshooting

### **Problema 1: Bot não responde**

**Checklist:**
- [ ] Workflow n8n está **ativado**? (toggle verde)
- [ ] N8N_WEBHOOK_URL configurado no Django .env?
- [ ] Django reiniciado após alterar .env?
- [ ] Instância WhatsApp está **conectada**?
- [ ] Webhook URL está correto na Evolution?

**Debug:**
```bash
# Verificar se webhook está chegando no Django
tail -f logs/django.log | grep "Webhook recebido"

# Verificar execuções do n8n
# Ir em n8n → Executions → Ver última execução
```

---

### **Problema 2: "API Key inválida"**

**Causa:** Chave N8N_API_KEY diferente entre Django e n8n

**Solução:**
1. Verifique `config/settings.py` → `N8N_API_KEY`
2. Verifique node "Configurações + Dados" → `config_django_key`
3. Devem ser **exatamente iguais**

---

### **Problema 3: "Empresa não encontrada"**

**Causa:** `empresa_id` errado no webhook

**Solução:**
1. Verifique no Django qual é o ID da empresa:
```python
from empresas.models import Empresa
Empresa.objects.all().values('id', 'nome')
```
2. Use o ID correto nos testes

---

### **Problema 4: IA não entende mensagens**

**Checklist:**
- [ ] OpenAI API Key configurada?
- [ ] Tem créditos na conta OpenAI?
- [ ] Model `gpt-4o-mini` está disponível?

**Teste direto:**
```bash
curl -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Authorization: Bearer sk-proj-SUA-CHAVE" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4o-mini",
    "messages": [{"role": "user", "content": "Oi"}]
  }'
```

---

### **Problema 5: "Assinatura inativa"**

**Causa:** Empresa sem assinatura ativa

**Solução:**
```python
from empresas.models import Empresa

empresa = Empresa.objects.get(id=1)
print("Assinatura ativa?", empresa.assinatura_ativa)

# Se retornar False, ative manualmente para teste:
# (Ou configure plano e pagamento corretamente)
```

---

## 📋 Checklist Final de Validação

Antes de ir para produção, valide:

### **Backend:**
- [ ] Todas as APIs n8n retornam dados corretos
- [ ] Webhook Django recebe e encaminha para n8n
- [ ] Logs aparecem corretamente
- [ ] Validação de assinatura funcionando
- [ ] Secret sendo validado

### **n8n:**
- [ ] Workflow ativado
- [ ] Todas as configurações preenchidas
- [ ] Execuções aparecem no histórico
- [ ] Não há erros nas execuções
- [ ] Resposta é enviada corretamente

### **WhatsApp:**
- [ ] Instância conectada
- [ ] Webhook configurado corretamente
- [ ] Bot recebe mensagens
- [ ] Bot responde mensagens
- [ ] Respostas são humanizadas

### **Agendamentos:**
- [ ] Agendamentos são criados no banco
- [ ] Cliente é criado/vinculado
- [ ] Profissional correto é selecionado
- [ ] Serviço correto é selecionado
- [ ] Data/hora corretas

### **Multi-tenant:**
- [ ] Cada empresa tem sua própria instância
- [ ] Webhook tem empresa_id correto
- [ ] Dados não vazam entre empresas
- [ ] UM workflow serve todas as empresas

---

## 🎯 Métricas de Sucesso

Uma integração bem-sucedida deve ter:

- ✅ **Tempo de resposta:** < 3 segundos
- ✅ **Taxa de sucesso:** > 95%
- ✅ **Precisão da IA:** > 90% (entende corretamente)
- ✅ **Uptime:** 99.9%

---

## 🚀 Próximos Passos

Após validar tudo:

1. **Monitoramento:**
   - Configure alertas para falhas
   - Monitore logs diariamente
   - Acompanhe métricas

2. **Melhorias:**
   - Adicionar cancelamento
   - Adicionar consulta de horários
   - Adicionar lembretes automáticos
   - Melhorar system prompt

3. **Produção:**
   - Migre para domínios reais
   - Configure SSL
   - Backup de workflows n8n
   - Documentação para equipe

---

## ✅ Conclusão

Se passou por todos os testes acima, sua integração está **100% funcional**! 🎉

**Parabéns!** Você agora tem:
- ✅ Bot WhatsApp inteligente
- ✅ Agendamentos automáticos
- ✅ Comunicação humanizada
- ✅ Sistema multi-tenant
- ✅ Arquitetura escalável

**Próximo passo:** Colocar em produção e monitorar! 🚀
