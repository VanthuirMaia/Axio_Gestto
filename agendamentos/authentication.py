"""
Autenticação por API Key para n8n
"""

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.conf import settings
from empresas.models import Empresa


class APIKeyAuthentication(BaseAuthentication):
    """
    Autenticação simples por API Key no header

    n8n envia:
    X-API-Key: sua-chave-secreta-aqui
    X-Empresa-ID: 1
    """

    def authenticate(self, request):
        # Aceitar tanto X-API-Key quanto apikey (compatibilidade)
        api_key = request.headers.get('X-API-Key') or request.headers.get('apikey')
        # Aceitar tanto X-Empresa-ID quanto empresa_id
        empresa_id = request.headers.get('X-Empresa-ID') or request.headers.get('empresa_id')

        if not api_key:
            raise AuthenticationFailed('API Key não fornecida (use header apikey ou X-API-Key)')

        # Se não informou empresa_id, usar a primeira empresa ativa (para simplificar)
        if not empresa_id:
            empresa = Empresa.objects.filter(ativa=True).first()
            if not empresa:
                raise AuthenticationFailed('Nenhuma empresa ativa encontrada')
        else:
            # Buscar empresa específica
            try:
                empresa = Empresa.objects.get(id=empresa_id, ativa=True)
            except Empresa.DoesNotExist:
                raise AuthenticationFailed('Empresa não encontrada')

        # Validar API Key
        if api_key != settings.GESTTO_API_KEY:
            raise AuthenticationFailed('API Key inválida')

        # Anexar empresa ao request (para usar nas views)
        request.empresa = empresa

        # Retornar None como user (não precisa de usuário para bot)
        return (None, None)
