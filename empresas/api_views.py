"""
API Views para webhooks e integrações externas
"""
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
import json
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def whatsapp_webhook(request, empresa_id, secret):
    """
    Webhook para receber eventos da Evolution API

    URL: /api/webhooks/whatsapp/{empresa_id}/{secret}/

    Eventos recebidos:
    - QRCODE_UPDATED: Novo QR Code disponível
    - CONNECTION_UPDATE: Mudança no status da conexão
    - MESSAGES_UPSERT: Nova mensagem recebida
    - etc.
    """
    from .models import ConfiguracaoWhatsApp
    from .services import EvolutionAPIService

    try:
        # Buscar configuração e validar secret
        try:
            config = ConfiguracaoWhatsApp.objects.get(
                empresa_id=empresa_id,
                webhook_secret=secret
            )
        except ConfiguracaoWhatsApp.DoesNotExist:
            logger.warning(f"Webhook inválido: empresa={empresa_id}, secret={secret[:10]}...")
            return JsonResponse({'error': 'Invalid webhook'}, status=404)

        # Parsear payload
        try:
            payload = json.loads(request.body)
        except json.JSONDecodeError:
            logger.error("Webhook: Payload JSON inválido")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

        # Log do evento recebido
        event_type = payload.get('event', 'unknown')
        logger.info(f"Webhook recebido: empresa={empresa_id}, event={event_type}")

        # Processar webhook via service
        service = EvolutionAPIService(config)
        result = service.processar_webhook(payload)

        # Log do resultado
        if result.get('processed'):
            logger.info(f"Webhook processado: tipo={result.get('type')}")
        else:
            logger.warning(f"Webhook não processado: tipo={result.get('type')}")

        return JsonResponse({
            'success': True,
            'processed': result.get('processed', False),
            'message': 'Webhook received'
        })

    except Exception as e:
        logger.error(f"Erro ao processar webhook: {str(e)}", exc_info=True)
        return JsonResponse({
            'error': 'Internal server error',
            'message': str(e)
        }, status=500)
