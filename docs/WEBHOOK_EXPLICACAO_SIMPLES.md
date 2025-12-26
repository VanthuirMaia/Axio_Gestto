# 🎯 Como Funciona o Webhook? (Explicação SUPER Simples)

## 📱 História Prática: João Quer Agendar

Vou explicar com um exemplo real, passo a passo:

---

## 🏪 Cenário:

**Empresa:** Barbearia do Pedro (ID = 1)
**WhatsApp da Barbearia:** +55 11 98765-4321
**Instância Evolution:** `empresa_barbearia_pedro`
**Cliente:** João (telefone +55 11 99999-9999)

---

## 📞 Passo 1: João Envia Mensagem

João pega o celular e envia no WhatsApp:

```
Para: +55 11 98765-4321 (WhatsApp da Barbearia)
Mensagem: "Oi, quero agendar corte amanhã 14h"
```

---

## 📡 Passo 2: Evolution API Recebe

A Evolution API está "escutando" o WhatsApp da barbearia.

Quando João envia a mensagem, a Evolution API pensa:

```
💭 "Recebi uma mensagem no WhatsApp da instância 'empresa_barbearia_pedro'"
💭 "Preciso avisar o sistema!"
💭 "Vou enviar para a URL do webhook que configuraram..."
```

A Evolution pega a URL do webhook que foi configurada quando criou a instância:

```
https://axiogestto.com/api/webhooks/whatsapp-n8n/1/abc123def456/
                                                  ↑   ↑
                                             empresa  secret
                                               ID=1
```

---

## 🌐 Passo 3: Evolution Envia Webhook para Django

A Evolution API faz um POST para essa URL com este payload:

```json
POST https://axiogestto.com/api/webhooks/whatsapp-n8n/1/abc123def456/

Body:
{
  "instance": "empresa_barbearia_pedro",  ← AQUI ESTÁ A IDENTIFICAÇÃO!
  "data": {
    "key": {
      "remoteJid": "5511999999999@s.whatsapp.net",
      "fromMe": false
    },
    "pushName": "João Silva",
    "message": {
      "conversation": "Oi, quero agendar corte amanhã 14h"
    },
    "messageTimestamp": "1703692800"
  }
}
```

**IMPORTANTE:** Veja que o payload JÁ VEM COM:
- ✅ `instance`: "empresa_barbearia_pedro" (qual empresa)
- ✅ `message`: "Oi, quero agendar..." (o que João disse)
- ✅ `remoteJid`: "5511999999999..." (telefone do João)

---

## 🔐 Passo 4: Django Recebe e Valida

O Django recebe o POST na URL: `/api/webhooks/whatsapp-n8n/1/abc123def456/`

Django faz as checagens:

### Checagem 1: Empresa Existe?
```python
empresa_id = 1  # Veio da URL!
empresa = Empresa.objects.get(id=1)  # ✅ Encontrou: "Barbearia do Pedro"
```

### Checagem 2: Secret Correto?
```python
secret_da_url = "abc123def456"
secret_do_banco = empresa.whatsapp_config.webhook_secret

if secret_da_url == secret_do_banco:  # ✅ Correto!
    print("Secret válido!")
```

### Checagem 3: Assinatura Ativa?
```python
if empresa.assinatura_ativa:  # ✅ Sim, está pagando!
    print("Pode processar!")
```

**Tudo OK!** ✅ Django vai encaminhar para n8n.

---

## 📦 Passo 5: Django Enriquece o Payload

Django adiciona informações úteis:

```json
{
  "empresa_id": 1,  ← Django adicionou!
  "empresa_nome": "Barbearia do Pedro",  ← Django adicionou!
  "instance": "empresa_barbearia_pedro",  ← Já veio da Evolution
  "body": {
    "data": {
      "key": {...},
      "message": {
        "conversation": "Oi, quero agendar corte amanhã 14h"
      }
    }
  }
}
```

---

## 🚀 Passo 6: Django Encaminha para n8n

Django faz um POST para n8n:

```
POST https://seu-n8n.com/webhook/bot-universal

Body: (o payload enriquecido acima)
```

---

## 🤖 Passo 7: n8n Processa

n8n recebe e extrai os dados:

```javascript
// Node "Configurações + Dados"
empresa_id = 1  ← Veio do Django!
instance_name = "empresa_barbearia_pedro"  ← Veio da Evolution!
telefone = "5511999999999"
mensagem = "Oi, quero agendar corte amanhã 14h"
```

Agora n8n pode:

1. **Buscar dados da empresa certa:**
   ```
   GET https://axiogestto.com/api/n8n/profissionais/?empresa_id=1
   GET https://axiogestto.com/api/n8n/servicos/?empresa_id=1
   ```

2. **Processar com IA:**
   ```
   OpenAI: "João quer agendar corte amanhã 14h"
   Resposta: { intencao: "agendar", servico: "Corte", data: "2025-12-27", hora: "14:00" }
   ```

3. **Criar agendamento:**
   ```
   POST https://axiogestto.com/api/bot/processar/
   Body: { empresa_id: 1, telefone: "5511999999999", ... }
   ```

---

## 📲 Passo 8: n8n Envia Resposta

n8n sabe para qual instância responder (porque veio no payload!):

```javascript
POST https://evolution.axiodev.cloud/message/sendText/empresa_barbearia_pedro
                                                        ↑
                                    Usa a instância que veio no webhook!

Body:
{
  "number": "5511999999999",  ← Telefone do João
  "text": "✅ Agendamento confirmado!\n📅 Corte de Cabelo\n🕐 Amanhã às 14h\n..."
}
```

---

## ✅ Passo 9: João Recebe Resposta

João vê no WhatsApp:

```
Barbearia do Pedro:
✅ Agendamento confirmado!
📅 Corte de Cabelo
🕐 Amanhã às 14h
💰 Valor: R$ 30,00

Te aguardamos! 😊
```

---

## 🎯 Resumo Visual

```
[João]
  ↓ "Quero agendar corte"
[WhatsApp]
  ↓
[Evolution API]
  ↓ POST com instance="empresa_barbearia_pedro"
[Django - Webhook Intermediário]
  ↓ Valida: empresa_id=1, secret, assinatura
  ↓ Adiciona: empresa_id, empresa_nome
[n8n Workflow]
  ↓ Extrai: empresa_id=1, instance_name, mensagem
  ↓ Busca: profissionais e serviços da empresa_id=1
  ↓ IA processa
  ↓ Cria agendamento
[Evolution API]
  ↓ POST /message/sendText/empresa_barbearia_pedro
[WhatsApp]
  ↓
[João]
  ✅ "Agendamento confirmado!"
```

---

## 🤔 Como Sabe Qual Instância?

### **A Resposta Simples:**

O payload da Evolution API **JÁ VEM COM** o nome da instância!

```json
{
  "instance": "empresa_barbearia_pedro"  ← AQUI!
}
```

Então:
1. Evolution envia `instance: "empresa_barbearia_pedro"`
2. Django passa isso para n8n
3. n8n usa esse valor para responder na instância certa!

**Não há mágica!** É simplesmente pegar o valor que veio e usar na resposta! 🎯

---

## 🏢 E Se Tiver 3 Empresas?

Vamos ver um exemplo com 3 empresas:

### **Empresa 1: Barbearia do Pedro**
- Evolution instância: `empresa_barbearia_pedro`
- Webhook URL: `https://axiogestto.com/api/webhooks/whatsapp-n8n/1/secret1/`
- Quando cliente envia mensagem → Evolution envia `instance: "empresa_barbearia_pedro"` → n8n responde em `empresa_barbearia_pedro`

### **Empresa 2: Salão da Maria**
- Evolution instância: `empresa_salao_maria`
- Webhook URL: `https://axiogestto.com/api/webhooks/whatsapp-n8n/2/secret2/`
- Quando cliente envia mensagem → Evolution envia `instance: "empresa_salao_maria"` → n8n responde em `empresa_salao_maria`

### **Empresa 3: Clínica Dr. João**
- Evolution instância: `empresa_clinica_joao`
- Webhook URL: `https://axiogestto.com/api/webhooks/whatsapp-n8n/3/secret3/`
- Quando cliente envia mensagem → Evolution envia `instance: "empresa_clinica_joao"` → n8n responde em `empresa_clinica_joao`

**Cada empresa tem:**
- ✅ URL do webhook diferente (empresa_id e secret diferentes)
- ✅ Instância Evolution diferente
- ✅ **MAS TODOS USAM O MESMO WORKFLOW N8N!**

O workflow n8n é **dinâmico** - ele pega o `empresa_id` e `instance` que vêm no payload e usa para buscar os dados certos e responder no lugar certo!

---

## 🔑 Pontos-Chave

1. **O `instance` JÁ VEM no payload da Evolution**
   - Não precisa descobrir, já está lá!

2. **O `empresa_id` vem na URL do webhook**
   - `/api/webhooks/whatsapp-n8n/1/secret/`
   - Django extrai o `1` da URL

3. **Django adiciona `empresa_id` ao payload para n8n**
   - n8n usa para buscar dados da empresa certa

4. **n8n usa `instance` para enviar resposta**
   - `/message/sendText/{instance_name}`

5. **UM ÚNICO WORKFLOW serve todas as empresas!**
   - Porque busca dados dinamicamente via API
   - Usa o `empresa_id` que veio no payload

---

## 🚀 Ficou Claro?

Se ainda tiver dúvida, pense assim:

**É como correio:**
- Evolution = Carteiro que entrega a carta (com remetente escrito)
- Django = Recepção que valida e encaminha
- n8n = Departamento que processa e responde
- Resposta vai para o remetente (instance) que estava escrito na carta!

**Não há mágica, é só ler o que já vem! 📧**

---

## 📋 Configuração .env

Adicione no `.env` do Django:

```bash
# URL do webhook n8n
N8N_WEBHOOK_URL=https://seu-n8n.com/webhook/bot-universal
```

E pronto! 🎉
