import json
import logging
import requests
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.conf import settings
from whatsapp.models import WhatsAppInstance

logger = logging.getLogger(__name__)


@csrf_exempt
def webhook_whatsapp_global(request):
    """
    Webhook global que recebe eventos da Evolution API
    e encaminha ao n8n com contexto do cliente.
    """

    if request.method != 'POST':
        return JsonResponse({'error': 'Apenas POST permitido'}, status=405)

    # =============================
    # 1️⃣ Validação do payload
    # =============================
    try:
        body = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        logger.warning("Webhook WhatsApp: payload inválido (não é JSON)")
        return JsonResponse({'error': 'Payload inválido'}, status=400)

    instance_name = body.get("instance")
    if not instance_name:
        logger.warning("Webhook WhatsApp: sem 'instance' no payload")
        return JsonResponse({'error': 'Instance name ausente'}, status=400)

    # =============================
    # 2️⃣ Resolução da instância
    # =============================
    try:
        instance = WhatsAppInstance.objects.select_related("cliente").get(instance_name=instance_name)
        cliente = instance.cliente
        logger.info(f"[Webhook] Instance={instance_name}, Cliente={cliente.username}")
    except WhatsAppInstance.DoesNotExist:
        logger.error(f"[Webhook] Instância desconhecida: {instance_name}")
        return JsonResponse({'error': 'Instância não reconhecida'}, status=404)

    # =============================
    # 3️⃣ Montagem do payload para o n8n
    # =============================
    payload_n8n = {
        "instance": instance_name,
        "cliente_id": str(cliente.id),
        "cliente_email": cliente.email,
        "body": body,  # Payload original da Evolution
    }

    n8n_url = getattr(settings, "N8N_WEBHOOK_URL", None)
    if not n8n_url:
        logger.error("[Webhook] N8N_WEBHOOK_URL não configurada nos settings")
        return JsonResponse({'error': 'Configuração interna ausente'}, status=500)

    # =============================
    # 4️⃣ Encaminhar para o n8n
    # =============================
    try:
        response = requests.post(n8n_url, json=payload_n8n, timeout=10)

        if response.status_code == 200:
            logger.info(f"[Webhook] Encaminhado ao n8n com sucesso: cliente={cliente.username}")
            return JsonResponse({"success": True})

        logger.error(f"[Webhook] n8n retornou erro {response.status_code}: {response.text[:200]}")
        return JsonResponse({
            "success": False,
            "error": f"Erro ao encaminhar para o n8n ({response.status_code})"
        }, status=500)

    except requests.exceptions.Timeout:
        logger.error(f"[Webhook] Timeout ao enviar para o n8n ({n8n_url})")
        return JsonResponse({"error": "Timeout ao conectar ao n8n"}, status=504)

    except requests.exceptions.RequestException as e:
        logger.error(f"[Webhook] Falha ao enviar ao n8n: {str(e)}")
        return JsonResponse({"error": "Falha de conexão com n8n"}, status=502)
