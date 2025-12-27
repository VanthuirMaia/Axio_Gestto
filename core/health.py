"""
Health check endpoint para monitoramento de infraestrutura.
"""
from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.views.decorators.csrf import csrf_exempt
import redis
from django.conf import settings


@csrf_exempt
def health_check(request):
    """
    Endpoint de health check para Docker healthcheck e monitoramento.

    Verifica:
    - Conexão com banco de dados
    - Conexão com Redis
    - Status geral da aplicação

    Retorna 200 OK se tudo estiver funcionando.
    Retorna 503 Service Unavailable se houver problemas.
    """
    health_status = {
        'status': 'healthy',
        'checks': {}
    }

    is_healthy = True

    # Verificar conexão com banco de dados
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        health_status['checks']['database'] = 'ok'
    except Exception as e:
        health_status['checks']['database'] = f'error: {str(e)}'
        is_healthy = False

    # Verificar conexão com Redis
    try:
        # Testa set/get no Redis
        cache.set('health_check', 'ok', 10)
        if cache.get('health_check') == 'ok':
            health_status['checks']['redis'] = 'ok'
        else:
            health_status['checks']['redis'] = 'error: cache test failed'
            is_healthy = False
    except Exception as e:
        health_status['checks']['redis'] = f'error: {str(e)}'
        is_healthy = False

    if not is_healthy:
        health_status['status'] = 'unhealthy'
        return JsonResponse(health_status, status=503)

    return JsonResponse(health_status, status=200)
