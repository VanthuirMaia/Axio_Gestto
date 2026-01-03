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

        if not api_key:
            raise AuthenticationFailed('API Key não fornecida (use header apikey ou X-API-Key)')

        # Validar API Key
        if api_key != settings.GESTTO_API_KEY:
            raise AuthenticationFailed('API Key inválida')

        # 🔍 IDENTIFICAÇÃO MULTI-TENANT DA EMPRESA
        # Ordem de prioridade:
        # 1. X-Empresa-ID (header explícito)
        # 2. X-Telefone-WhatsApp (busca empresa pelo número conectado)
        # 3. Primeira empresa ativa (fallback)

        empresa_id = request.headers.get('X-Empresa-ID') or request.headers.get('empresa_id')
        telefone_whatsapp = request.headers.get('X-Telefone-WhatsApp') or request.headers.get('telefone_whatsapp')

        empresa = None

        # 1. Tentar por ID direto
        if empresa_id:
            try:
                empresa = Empresa.objects.get(id=empresa_id, ativa=True)
            except Empresa.DoesNotExist:
                raise AuthenticationFailed(f'Empresa ID {empresa_id} não encontrada')

        # 2. Tentar identificar pelo número do WhatsApp conectado
        elif telefone_whatsapp:
            # Limpar telefone (remover caracteres especiais)
            import re
            telefone_limpo = re.sub(r'\D', '', telefone_whatsapp)

            # Buscar empresa com esse número de WhatsApp
            empresa = Empresa.objects.filter(
                whatsapp_numero__contains=telefone_limpo,
                ativa=True
            ).first()

            if not empresa:
                raise AuthenticationFailed(f'Nenhuma empresa encontrada com WhatsApp {telefone_whatsapp}')

        # 3. Fallback: primeira empresa ativa
        else:
            empresa = Empresa.objects.filter(ativa=True).first()
            if not empresa:
                raise AuthenticationFailed('Nenhuma empresa ativa encontrada')

        # Anexar empresa ao request (para usar nas views)
        request.empresa = empresa

        # Retornar None como user (não precisa de usuário para bot)
        return (None, None)
