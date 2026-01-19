"""
Middleware para validação de tenant em requisições de API
"""
import logging
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class TenantValidationMiddleware:
    """
    Middleware que valida isolamento multi-tenant em todas as requisições de API
    Previne cruzamento de dados entre empresas
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Validar apenas APIs de bot
        if request.path.startswith('/api/bot/'):
            # Verificar se empresa foi identificada
            if hasattr(request, 'empresa'):
                if not request.empresa:
                    logger.error(f"[SECURITY] Tentativa de acesso à API sem tenant identificado | Path: {request.path}")
                    return JsonResponse({
                        'sucesso': False,
                        'erro': 'Tenant não identificado',
                        'hint': 'Envie X-Instance-Name, X-Empresa-ID ou X-Telefone-WhatsApp no header'
                    }, status=400)
                else:
                    # Log de auditoria
                    logger.info(f"[AUDIT] API Request | Empresa: {request.empresa.nome} (ID: {request.empresa.id}) | Path: {request.path}")
        
        response = self.get_response(request)
        return response
