"""
Throttling customizado para API do bot n8n.
"""
from rest_framework.throttling import SimpleRateThrottle


class BotAPIThrottle(SimpleRateThrottle):
    """
    Throttle específico para API do bot n8n.
    Limita requisições por empresa (X-Empresa-ID).
    """
    scope = 'bot_api'

    def get_cache_key(self, request, view):
        """
        Identifica a empresa pelo header X-Empresa-ID
        para limitar requests por empresa.
        """
        empresa_id = request.META.get('HTTP_X_EMPRESA_ID')
        if empresa_id:
            return self.cache_format % {
                'scope': self.scope,
                'ident': empresa_id
            }

        # Fallback para IP se não houver empresa_id
        ident = self.get_ident(request)
        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }
