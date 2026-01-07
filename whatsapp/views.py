import json
import logging
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from whatsapp.models import WhatsAppInstance
from django.conf import settings

logger = logging.getLogger(__name__)

@csrf_exempt
def webhook_whatsapp_global(request):
    """
    Webhook global que recebe eventos da Evolution API
    e encaminha ao n8n com contexto do cliente.
    """

    if request.method != 'POST':
        return JsonResponse({'error': 'Apenas POST permitido'}, status=405)

    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        logger.warning("Webhook WhatsApp: payload inválido (não é JSON)")
        return JsonResponse({'error': 'Payload inválido'}, status=400)

    instance_name = body.get("instance")
    if not instance_name:
        logger.warning("Webhook WhatsApp: sem 'instance' no payload")
        return JsonResponse({'error': 'Instance name ausente'}, status=400)

    try:
        instance = WhatsAppInstance.objects.select_related("cliente").get(instance_name=instance_name)
        cliente = instance.cliente
        logger.info(f"Webhook recebido: instance={instance_name}, cliente={cliente.username}")
    except WhatsAppInstance.DoesNotExist:
        logger.error(f"Webhook: instância desconhecida: {instance_name}")
        return JsonResponse({'error': 'Instância não reconhecida'}, status=404)

    # Montar payload para o n8n
    payload_n8n = {
        "instance": instance_name,
        "cliente_id": str(cliente.id),
        "cliente_email": cliente.email,
        "body": body,
    }

    # URL do n8n (configurada no settings)
    n8n_url = getattr(settings, "N8N_WEBHOOK_URL", None)
    if not n8n_url:
        logger.error("N8N_WEBHOOK_URL não configurada nos settings")
        return JsonResponse({'error': 'Configuração interna ausente'}, status=500)

    try:
        response = requests.post(n8n_url, json=payload_n8n, timeout=10)

        if response.status_code == 200:
            logger.info(f"Webhook encaminhado ao n8n com sucesso: cliente={cliente.username}")
            return JsonResponse({"success": True})

        logger.error(f"n8n retornou erro: {response.status_code} - {response.text[:200]}")
        return JsonResponse({
            "success": False,
            "error": "Erro ao encaminhar para o n8n"
        }, status=500)

    except requests.exceptions.RequestException as e:
        logger.error(f"Falha ao enviar ao n8n: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": "Falha ao conectar ao n8n"
        }, status=502)
