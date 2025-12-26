# Correção da Configuração de Webhook - Evolution API v2

## Problema Identificado

As configurações de webhook não estavam sendo marcadas corretamente na Evolution API porque o formato dos parâmetros estava **incorreto**.

### Formato INCORRETO (anterior):

```json
{
  "instanceName": "...",
  "webhookUrl": "...",
  "webhookByEvents": true,
  "webhookBase64": true,
  "events": [...]
}
```

### Formato CORRETO (atual):

```json
{
  "instanceName": "...",
  "webhook": {
    "url": "...",
    "byEvents": true,
    "base64": true,
    "events": [...]
  }
}
```

## Mudanças Realizadas

### 1. `empresas/services/evolution_api.py`

**Método `criar_instancia()` (linha 117-144):**
- ✅ Correção do formato de webhook para objeto aninhado
- ✅ `webhook.url` em vez de `webhookUrl`
- ✅ `webhook.byEvents` em vez de `webhookByEvents`
- ✅ `webhook.base64` em vez de `webhookBase64`
- ✅ `webhook.events[]` array de eventos dentro do objeto webhook
- ✅ Adicionado evento `SEND_MESSAGE`
- ✅ Logs de debug para rastrear o payload enviado

**Método `configurar_webhook()` (linha 312-345):**
- ✅ Ajustado para usar `webhook_by_events` (snake_case) no endpoint `/webhook/set`
- ✅ Ajustado para usar `webhook_base64` (snake_case) no endpoint `/webhook/set`
- ✅ Adicionado evento `SEND_MESSAGE`

**Novos métodos de sincronização:**
- ✅ `verificar_existencia_instancia()` - verifica se instância existe na Evolution
- ✅ `sincronizar_status()` - sincroniza status e detecta deleção externa

### 2. `configuracoes/views.py`

**View `whatsapp_dashboard()` (linha 415-459):**
- ✅ Sincronização automática ao carregar a página
- ✅ Detecta instâncias deletadas externamente
- ✅ Mostra mensagem de aviso ao usuário

**Nova view `whatsapp_sincronizar()` (linha 694-745):**
- ✅ Endpoint AJAX para sincronização manual
- ✅ Retorna status atualizado

### 3. `configuracoes/urls.py`

**Novas rotas:**
- ✅ `/configuracoes/whatsapp/reconfigurar/` - Reconfigura webhook e settings
- ✅ `/configuracoes/whatsapp/sincronizar/` - Sincroniza status

## Eventos Configurados

Os seguintes eventos serão recebidos via webhook:

1. **QRCODE_UPDATED** - Quando o QR Code é atualizado
2. **MESSAGES_UPSERT** - Nova mensagem recebida/enviada ✓
3. **MESSAGES_UPDATE** - Mensagem atualizada (lida, deletada, etc)
4. **SEND_MESSAGE** - Confirmação de envio de mensagem
5. **CONNECTION_UPDATE** - Mudança no status de conexão

## Como Testar

### 1. Verificar o Payload de Criação

Execute o script de debug:

```bash
cd D:\Axio\axio_gestto
python scripts\debug_evolution_webhook.py
```

Este script mostrará:
- O payload exato que será enviado
- Verificações de cada configuração
- Status de instâncias existentes

### 2. Criar Nova Instância

1. Acesse `/configuracoes/whatsapp/`
2. Se houver instância antiga, delete-a primeiro
3. Clique em "Conectar WhatsApp"
4. Aguarde o QR Code aparecer
5. **Verifique na Evolution API:**
   - Acesse o painel da Evolution API
   - Vá em "Instances" → Sua instância → "Events/Webhook"
   - **Deve estar marcado:**
     - ✅ Enable
     - ✅ Webhook Base64
     - ✅ MESSAGES_UPSERT
     - ✅ MESSAGES_UPDATE
     - ✅ QRCODE_UPDATED
     - ✅ SEND_MESSAGE
     - ✅ CONNECTION_UPDATE

### 3. Verificar Logs

Monitore os logs do Django para ver o payload sendo enviado:

```bash
# Se estiver usando manage.py runserver
# Você verá logs como:
INFO - Criando instância empresa_123 com webhook: https://...
DEBUG - Payload de criação: {...}
```

### 4. Testar Sincronização

1. Delete a instância manualmente na Evolution API
2. Volte para `/configuracoes/whatsapp/` no sistema
3. O sistema deve:
   - Detectar que a instância foi deletada
   - Resetar a configuração local
   - Mostrar mensagem: "A instância do WhatsApp foi removida externamente..."

## Endpoints da Evolution API Utilizados

| Endpoint | Método | Uso |
|----------|--------|-----|
| `/instance/create` | POST | Criar instância com webhook |
| `/webhook/set/{instance}` | POST | Configurar webhook (backup) |
| `/settings/set/{instance}` | POST | Configurar settings |
| `/instance/fetchInstances` | GET | Listar instâncias (sincronização) |
| `/instance/connectionState/{instance}` | GET | Verificar status |
| `/instance/connect/{instance}` | GET | Obter QR Code |

## Documentação de Referência

- [Evolution API v2 - Webhooks](https://doc.evolution-api.com/v2/en/configuration/webhooks)
- [Evolution API v2 - Create Instance](https://doc.evolution-api.com/v2/api-reference/instance-controller/create-instance-basic)
- [Set Webhook Documentation](https://docs.evolution-api.com/docs/04-Webhooks/00-set-webhook/)
- [Postman Collection v2.2.2](https://www.postman.com/agenciadgcode/evolution-api/documentation/jn0bbzv/evolution-api-v2-2-2)

## Troubleshooting

### Webhook ainda não está sendo marcado

1. Verifique os logs do Django para ver o payload enviado
2. Execute `python scripts\debug_evolution_webhook.py`
3. Confirme que a Evolution API está na versão 2.x
4. Verifique se a API Key está correta
5. Teste manualmente via curl/Postman usando o payload do script de debug

### Erro ao criar instância

- Verifique se `EVOLUTION_API_URL` e `EVOLUTION_API_KEY` estão configurados
- Confirme que a URL não tem trailing slash duplo
- Verifique se o servidor da Evolution está acessível

### Instância criada mas webhook não funciona

- Use a rota `/configuracoes/whatsapp/reconfigurar/` para reaplicar configurações
- Verifique os logs da Evolution API
- Confirme que a URL do webhook é acessível publicamente

## Próximos Passos

1. ✅ Testar criação de instância
2. ✅ Verificar se webhook está marcado na Evolution
3. ✅ Testar recebimento de mensagens
4. ⏳ Implementar processamento de webhooks recebidos
5. ⏳ Implementar templates de mensagens automáticas
