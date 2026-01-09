"""
Models do app WhatsApp.

NOTA: O model principal WhatsAppInstance está em empresas.models
para manter a coesão com Empresa. Este arquivo importa e re-exporta
para manter compatibilidade com imports existentes.
"""
from empresas.models import WhatsAppInstance, ConfiguracaoWhatsApp

__all__ = ['WhatsAppInstance', 'ConfiguracaoWhatsApp']
