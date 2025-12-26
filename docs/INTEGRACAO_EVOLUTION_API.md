# 🚀 Integração com Evolution API - Documentação Completa

## 📋 Índice

1. [Visão Geral](#visão-geral)
2. [Arquitetura](#arquitetura)
3. [Fluxo de Configuração](#fluxo-de-configuração)
4. [Componentes Criados](#componentes-criados)
5. [Próximos Passos](#próximos-passos)
6. [Referências](#referências)

---

## 🎯 Visão Geral

Sistema completo de integração com Evolution API v2 que permite que cada empresa (tenant) tenha sua própria instância WhatsApp conectada de forma automatizada.

### O que foi implementado:

✅ **Model `ConfiguracaoWhatsApp`** - Armazena configuração e status da integração
✅ **Service Layer `EvolutionAPIService`** - Comunicação completa com Evolution API
✅ **Migrations** - Banco de dados atualizado
✅ **Documentação** - Guia de uso e arquitetura

### O que falta implementar:

⏳ **Views** - Endpoints para configurar WhatsApp
⏳ **Templates** - Interface visual (wizard passo-a-passo)
⏳ **Webhooks** - Endpoint para receber eventos da Evolution
⏳ **Admin** - Painel administrativo

---

## 🏗️ Arquitetura

### Diagrama de Fluxo

```
┌─────────────────────┐
│  Usuário (Cliente)  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────────────────────┐
│   Frontend (Template Wizard)       │
│  - Configurar WhatsApp              │
│  - Conectar Instância               │
│  - Escanear QR Code                 │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│   Views Django                      │
│  - whatsapp_configurar()            │
│  - whatsapp_criar_instancia()       │
│  - whatsapp_obter_qr()              │
│  - whatsapp_status()                │
│  - whatsapp_desconectar()           │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│   EvolutionAPIService               │
│  - criar_instancia()                │
│  - obter_qrcode()                   │
│  - obter_status_conexao()           │
│  - enviar_mensagem_texto()          │
│  - processar_webhook()              │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│   Evolution API (Externa)           │
│  - Gerencia instâncias WhatsApp     │
│  - Gera QR Codes                    │
│  - Envia/Recebe mensagens           │
│  - Dispara webhooks                 │
└─────────────────────────────────────┘
```

### Modelos de Dados

#### `ConfiguracaoWhatsApp`

```python
empresa = OneToOneField(Empresa)  # 1 config por empresa

# Configuração Evolution API
evolution_api_url = "https://evolution.servidor.com"
evolution_api_key = "sua_api_key"

# Instância
instance_name = "axio_1"  # {slug_empresa}_{id}
instance_token = "token_gerado_automaticamente"

# Status
status = "conectado"  # nao_configurado, aguardando_qr, conectando, conectado, desconectado, erro

# QR Code
qr_code = "data:image/png;base64,..."  # Base64 do QR
qr_code_expira_em = datetime

# Webhook
webhook_url = "https://gestto.com/api/webhooks/whatsapp/1/secret/"
webhook_secret = "secret_aleatorio_gerado"

# Dados da conexão
numero_conectado = "5511999999999"
nome_perfil = "Barbearia do João"
foto_perfil_url = "https://..."
```

---

## 🔄 Fluxo de Configuração

### Opção 1: Configuração Manual (Cliente faz tudo)

**Passo 1: Acessar Configurações**
```
Cliente → Configurações → WhatsApp
```

**Passo 2: Conectar API Evolution (se cada cliente tem sua própria)**
```python
# View: whatsapp_configurar_api()
POST /configuracoes/whatsapp/api/
{
  "evolution_url": "https://minha-evolution.com",
  "api_key": "minha_chave"
}
```

**Passo 3: Criar Instância**
```python
# View: whatsapp_criar_instancia()
POST /configuracoes/whatsapp/criar-instancia/

# Backend chama:
service = EvolutionAPIService(config)
result = service.criar_instancia()

# Evolution retorna:
{
  "instance": {
    "instanceName": "axio_1",
    "token": "abc123...",
    "status": "created"
  }
}
```

**Passo 4: Obter QR Code**
```python
# View (AJAX polling a cada 5 segundos):
GET /configuracoes/whatsapp/qrcode/

# Backend chama:
result = service.obter_qrcode()

# Retorna:
{
  "qrcode": "data:image/png;base64,iVBOR...",
  "expires_in": 120  # segundos
}
```

**Passo 5: Cliente escaneia QR Code com WhatsApp**
```
1. Cliente abre WhatsApp no celular
2. Vai em "Dispositivos Conectados"
3. Escaneia o QR Code mostrado na tela
4. Evolution recebe conexão
5. Evolution envia webhook para nosso sistema
```

**Passo 6: Webhook confirma conexão**
```python
# Webhook recebido:
POST /api/webhooks/whatsapp/{empresa_id}/{secret}/
{
  "event": "CONNECTION_UPDATE",
  "data": {
    "state": "open",
    "statusReason": "connected"
  }
}

# Backend atualiza:
config.status = 'conectado'
config.numero_conectado = "5511999999999"
config.save()
```

**Passo 7: Pronto! WhatsApp Conectado** ✅

---

### Opção 2: Auto-Configuração (1 Clique)

**Cenário:** Servidor Evolution centralizado (você gerencia para todos os clientes)

**Vantagem:** Cliente só clica em "Conectar WhatsApp" e escaneia QR

**Implementação:**

1. Configurar no `.env`:
```env
EVOLUTION_API_URL=https://evolution.seuservidor.com
EVOLUTION_API_KEY=sua_api_key_master
SITE_URL=https://gestto.com
```

2. View simplificada:
```python
@login_required
def whatsapp_conectar_auto(request):
    """Cliente só clica aqui"""
    empresa = request.user.empresa

    # Criar ou buscar config
    config, created = ConfiguracaoWhatsApp.objects.get_or_create(
        empresa=empresa,
        defaults={
            'evolution_api_url': settings.EVOLUTION_API_URL,
            'evolution_api_key': settings.EVOLUTION_API_KEY,
        }
    )

    # Criar instância automaticamente
    service = EvolutionAPIService(config)
    result = service.criar_instancia()

    if result['success']:
        # Redirecionar para página de QR Code
        return redirect('whatsapp_qrcode')
    else:
        messages.error(request, f"Erro: {result['error']}")
        return redirect('configuracoes_whatsapp')
```

3. Template mostra QR Code automaticamente:
```html
<!-- Polling a cada 3 segundos para pegar novo QR se expirar -->
<div id="qrcode-container">
  <img src="data:image/png;base64,{{ qr_code }}" />
  <p>Escaneie com seu WhatsApp</p>
</div>

<script>
setInterval(async () => {
  const response = await fetch('/configuracoes/whatsapp/qrcode/');
  const data = await response.json();

  if (data.status === 'conectado') {
    window.location.href = '/configuracoes/whatsapp/sucesso/';
  } else if (data.qrcode) {
    document.querySelector('#qrcode-container img').src = data.qrcode;
  }
}, 3000);
</script>
```

---

## 📦 Componentes Criados

### 1. Model: `ConfiguracaoWhatsApp`

**Arquivo:** `empresas/models.py` (linhas 208-352)

**Campos principais:**
- `empresa` - OneToOne com Empresa
- `evolution_api_url` - URL da Evolution
- `evolution_api_key` - API Key
- `instance_name` - Nome da instância (auto-gerado)
- `status` - Estado atual (conectado, desconectado, etc)
- `qr_code` - QR Code em base64
- `webhook_url` - URL do webhook
- `webhook_secret` - Secret de validação

**Métodos úteis:**
- `gerar_instance_name()` - Cria nome único baseado no slug
- `gerar_webhook_secret()` - Cria secret aleatório
- `esta_conectado()` - Verifica se está conectado

---

### 2. Service: `EvolutionAPIService`

**Arquivo:** `empresas/services/evolution_api.py`

**Métodos de Gerenciamento:**
- `criar_instancia()` - Cria nova instância na Evolution
- `obter_qrcode()` - Pega QR Code atual
- `obter_status_conexao()` - Verifica estado da conexão
- `desconectar_instancia()` - Faz logout
- `deletar_instancia()` - Remove instância (irreversível)

**Métodos de Mensagens:**
- `enviar_mensagem_texto(numero, mensagem)` - Envia texto
- `enviar_mensagem_imagem(numero, url, legenda)` - Envia imagem

**Métodos de Webhook:**
- `processar_webhook(payload)` - Processa eventos recebidos

---

## 🔜 Próximos Passos

### Passo 1: Criar Views

```python
# configuracoes/views.py

@login_required
def whatsapp_dashboard(request):
    """Página principal de WhatsApp"""
    empresa = request.user.empresa
    config, created = ConfiguracaoWhatsApp.objects.get_or_create(empresa=empresa)

    context = {
        'config': config,
        'conectado': config.esta_conectado(),
    }
    return render(request, 'configuracoes/whatsapp.html', context)


@login_required
def whatsapp_criar_instancia(request):
    """Cria instância e retorna QR Code"""
    if request.method == 'POST':
        config = request.user.empresa.config_whatsapp
        service = EvolutionAPIService(config)

        result = service.criar_instancia()

        if result['success']:
            # Obter QR Code
            qr_result = service.obter_qrcode()

            if qr_result['success']:
                return JsonResponse({
                    'success': True,
                    'qrcode': qr_result['qrcode'],
                    'status': config.status
                })

        return JsonResponse({
            'success': False,
            'error': result.get('error', 'Erro desconhecido')
        })


@login_required
def whatsapp_obter_qr(request):
    """AJAX - Retorna QR Code atual"""
    config = request.user.empresa.config_whatsapp
    service = EvolutionAPIService(config)

    result = service.obter_qrcode()

    return JsonResponse({
        'success': result['success'],
        'qrcode': result.get('qrcode', ''),
        'status': config.status,
        'conectado': config.esta_conectado()
    })


@login_required
def whatsapp_status(request):
    """AJAX - Retorna status da conexão"""
    config = request.user.empresa.config_whatsapp
    service = EvolutionAPIService(config)

    result = service.obter_status_conexao()

    return JsonResponse({
        'success': result['success'],
        'status': config.status,
        'conectado': config.esta_conectado(),
        'numero': config.numero_conectado,
        'nome': config.nome_perfil
    })
```

---

### Passo 2: Criar Webhook Endpoint

```python
# api/views.py (ou criar novo app 'webhooks')

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import json

@csrf_exempt
def whatsapp_webhook(request, empresa_id, secret):
    """
    Recebe webhooks da Evolution API

    URL: /api/webhooks/whatsapp/{empresa_id}/{secret}/
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    try:
        # Buscar configuração
        config = ConfiguracaoWhatsApp.objects.get(
            empresa_id=empresa_id,
            webhook_secret=secret
        )
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({'error': 'Invalid webhook'}, status=404)

    # Processar payload
    payload = json.loads(request.body)

    service = EvolutionAPIService(config)
    result = service.processar_webhook(payload)

    return JsonResponse(result)
```

---

### Passo 3: Criar Template (Wizard)

Ver arquivo separado: `TEMPLATE_WHATSAPP_WIZARD.md`

---

### Passo 4: Adicionar ao Admin

```python
# empresas/admin.py

from .models import ConfiguracaoWhatsApp

@admin.register(ConfiguracaoWhatsApp)
class ConfiguracaoWhatsAppAdmin(admin.ModelAdmin):
    list_display = ['empresa', 'status', 'numero_conectado', 'instance_name', 'criado_em']
    list_filter = ['status', 'ativo']
    search_fields = ['empresa__nome', 'numero_conectado', 'instance_name']
    readonly_fields = ['criado_em', 'atualizado_em', 'ultima_sincronizacao']
```

---

## 📚 Referências

- **Evolution API Docs:** https://doc.evolution-api.com/v2/pt/
- **Evolution GitHub:** https://github.com/EvolutionAPI/evolution-api
- **WhatsApp Business API:** https://developers.facebook.com/docs/whatsapp

---

## 🔒 Segurança

### Webhook Secret
- Sempre valide o secret no webhook
- Use `secrets.token_urlsafe(32)` para gerar
- Nunca exponha em logs

### API Keys
- Armazene no `.env`, nunca no código
- Use variáveis de ambiente diferentes para dev/prod
- Rotacione periodicamente

### HTTPS Obrigatório
- Webhooks DEVEM usar HTTPS em produção
- Evolution API rejeita webhooks HTTP

---

## 🐛 Troubleshooting

### QR Code não aparece
- Verifique se Evolution API está rodando
- Confirme API Key e URL no `.env`
- Veja logs: `service.criar_instancia()` retorna erro

### Webhook não recebe eventos
- Confirme URL pública (HTTPS)
- Teste com ngrok em desenvolvimento
- Verifique logs da Evolution API

### Instância desconecta sozinha
- WhatsApp foi desconectado no celular
- Timeout de inatividade
- Problema no servidor Evolution

---

**Status:** ✅ Backend pronto | ⏳ Views e Frontend pendentes
**Próximo passo:** Implementar Views e Templates
