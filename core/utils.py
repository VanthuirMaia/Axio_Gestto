"""
Funções utilitárias do core
"""
import secrets
from datetime import timedelta
from django.utils.timezone import now


def gerar_token_ativacao():
    """
    Gera token único de 32 caracteres para ativação de conta
    
    Returns:
        str: Token URL-safe de 32 caracteres
    """
    return secrets.token_urlsafe(32)


def token_ativacao_valido(usuario):
    """
    Verifica se o token de ativação ainda é válido (48 horas)
    
    Args:
        usuario: Instância de Usuario
        
    Returns:
        bool: True se token ainda é válido, False caso contrário
    """
    if not usuario.activation_token_created:
        return False
    
    expiracao = usuario.activation_token_created + timedelta(hours=48)
    return now() < expiracao
