import json
import logging
import requests
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.conf import settings
from empresas.models import WhatsAppInstance, ConfiguracaoWhatsApp, Empresa

logger = logging.getLogger(__name__)


@csrf_exempt
def webhook_whatsapp_global(request):
    """
    Webhook global que recebe eventos da Evolution API
    e encaminha ao n8n com contexto da empresa.

    Fluxo:
    1. Evolution API envia evento para este webhook
    2. Identifica a empresa pelo instance_name
    3. Processa evento localmente (QR, conexão)
    4. Encaminha para n8n com dados enriquecidos
    """

    if request.method != 'POST':
        return JsonResponse({'error': 'Apenas POST permitido'}, status=405)

    # =============================
    # 1. Validação do payload
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

    event_type = body.get("event", "unknown")
    logger.info(f"[Webhook] Evento={event_type}, Instance={instance_name}")

    # =============================
    # 2. Resolução da empresa
    # =============================
    try:
        # Busca via ConfiguracaoWhatsApp (relação com Empresa)
        config = ConfiguracaoWhatsApp.objects.select_related("empresa").get(
            instance_name=instance_name
        )
        empresa = config.empresa
        logger.info(f"[Webhook] Empresa identificada: {empresa.nome} (ID={empresa.id})")
    except ConfiguracaoWhatsApp.DoesNotExist:
        # Fallback: buscar via WhatsAppInstance
        try:
            instance = WhatsAppInstance.objects.select_related("empresa").get(
                instance_name=instance_name
            )
            empresa = instance.empresa
            config = getattr(empresa, 'config_whatsapp', None)
            logger.info(f"[Webhook] Empresa via fallback: {empresa.nome}")
        except WhatsAppInstance.DoesNotExist:
            logger.error(f"[Webhook] Instância desconhecida: {instance_name}")
            return JsonResponse({'error': 'Instância não reconhecida'}, status=404)

    # =============================
    # 3. Processar evento localmente
    # =============================
    if config:
        from empresas.services.evolution_api import EvolutionAPIService
        service = EvolutionAPIService(config)
        service.processar_webhook(body)

    # =============================
    # 4. Encaminhar para n8n
    # =============================
    n8n_url = getattr(settings, "N8N_WEBHOOK_URL", None)
    if not n8n_url:
        logger.warning("[Webhook] N8N_WEBHOOK_URL não configurada - processamento local apenas")
        return JsonResponse({"success": True, "processed": "local_only"})

    # Monta payload enriquecido para o n8n
    payload_n8n = {
        "instance": instance_name,
        "empresa_id": empresa.id,
        "empresa_slug": empresa.slug,
        "empresa_nome": empresa.nome,
        "event": event_type,
        "body": body,
    }

    try:
        response = requests.post(n8n_url, json=payload_n8n, timeout=10)

        if response.status_code == 200:
            logger.info(f"[Webhook] Encaminhado ao n8n: empresa={empresa.nome}")
            return JsonResponse({"success": True})

        logger.error(f"[Webhook] n8n erro {response.status_code}: {response.text[:200]}")
        return JsonResponse({
            "success": False,
            "error": f"Erro ao encaminhar para o n8n ({response.status_code})"
        }, status=500)

    except requests.exceptions.Timeout:
        logger.error(f"[Webhook] Timeout n8n ({n8n_url})")
        return JsonResponse({"error": "Timeout ao conectar ao n8n"}, status=504)

    except requests.exceptions.RequestException as e:
        logger.error(f"[Webhook] Falha n8n: {str(e)}")
        return JsonResponse({"error": "Falha de conexão com n8n"}, status=502)


@csrf_exempt
@require_http_methods(["GET"])
def resolver_cliente(request):
    """
    Endpoint para o n8n resolver dados completos de uma empresa
    baseado no instance_name do WhatsApp.

    GET /api/webhooks/whatsapp/resolver/?instance=gestto_empresa_123

    Returns:
        JSON com dados completos da empresa para o n8n processar
    """
    instance_name = request.GET.get("instance")

    if not instance_name:
        return JsonResponse({"error": "Parâmetro 'instance' obrigatório"}, status=400)

    # Buscar empresa
    try:
        config = ConfiguracaoWhatsApp.objects.select_related(
            "empresa"
        ).prefetch_related(
            "empresa__servicos",
            "empresa__profissionais",
            "empresa__horarios_funcionamento"
        ).get(instance_name=instance_name)

        empresa = config.empresa
    except ConfiguracaoWhatsApp.DoesNotExist:
        return JsonResponse({"error": "Instância não encontrada"}, status=404)

    # Verificar assinatura ativa
    assinatura = empresa.assinatura_ativa
    if not assinatura:
        return JsonResponse({
            "error": "Empresa sem assinatura ativa",
            "empresa_id": empresa.id,
            "empresa_nome": empresa.nome
        }, status=403)

    # Montar resposta completa
    servicos = list(empresa.servicos.filter(ativo=True).values(
        'id', 'nome', 'descricao', 'preco', 'duracao_minutos'
    ))

    profissionais = list(empresa.profissionais.filter(ativo=True).values(
        'id', 'nome', 'email', 'telefone'
    ))

    horarios = []
    for h in empresa.horarios_funcionamento.filter(ativo=True):
        horarios.append({
            'dia_semana': h.dia_semana,
            'dia_nome': h.get_dia_semana_display(),
            'abertura': h.hora_abertura.strftime('%H:%M') if h.hora_abertura else None,
            'fechamento': h.hora_fechamento.strftime('%H:%M') if h.hora_fechamento else None,
            'intervalo_inicio': h.intervalo_inicio.strftime('%H:%M') if h.intervalo_inicio else None,
            'intervalo_fim': h.intervalo_fim.strftime('%H:%M') if h.intervalo_fim else None,
        })

    return JsonResponse({
        "success": True,
        "empresa": {
            "id": empresa.id,
            "nome": empresa.nome,
            "slug": empresa.slug,
            "telefone": empresa.telefone,
            "email": empresa.email,
            "endereco": empresa.endereco,
            "cidade": empresa.cidade,
            "estado": empresa.estado,
        },
        "servicos": servicos,
        "profissionais": profissionais,
        "horarios": horarios,
        "assinatura": {
            "plano": assinatura.plano.get_nome_display() if assinatura.plano else None,
            "status": assinatura.status,
            "ativa": assinatura.esta_ativa(),
        },
        "whatsapp": {
            "instance_name": config.instance_name,
            "status": config.status,
            "conectado": config.esta_conectado(),
            "numero": config.numero_conectado,
        }
    })
