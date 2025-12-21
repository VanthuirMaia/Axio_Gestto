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
        api_key = request.headers.get('X-API-Key')
        empresa_id = request.headers.get('X-Empresa-ID')

        if not api_key:
            raise AuthenticationFailed('X-API-Key não fornecida')

        if not empresa_id:
            raise AuthenticationFailed('X-Empresa-ID não fornecida')

        # Validar API Key
        if api_key != settings.N8N_API_KEY:
            raise AuthenticationFailed('API Key inválida')

        # Buscar empresa
        try:
            empresa = Empresa.objects.get(id=empresa_id)
        except Empresa.DoesNotExist:
            raise AuthenticationFailed('Empresa não encontrada')

        # Anexar empresa ao request (para usar nas views)
        request.empresa = empresa

        # Retornar None como user (não precisa de usuário para bot)
        return (None, None)
