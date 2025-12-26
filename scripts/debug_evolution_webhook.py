"""
Script de debug para verificar configurações de webhook da Evolution API
"""
import json
import sys
import os

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from django.conf import settings
from empresas.models import ConfiguracaoWhatsApp, Empresa
from empresas.services import EvolutionAPIService


def mostrar_payload_criacao():
    """
    Mostra exatamente o payload que será enviado para criar uma instância
    """
    print("=" * 80)
    print("PAYLOAD DE CRIAÇÃO DE INSTÂNCIA - EVOLUTION API V2")
    print("=" * 80)
    print()

    # Simular dados de criação
    instance_name = "teste_empresa_123"
    webhook_secret = "secret_abc123"
    empresa_id = 1
    webhook_url = f"{settings.SITE_URL}/api/webhooks/whatsapp/{empresa_id}/{webhook_secret}/"

    payload = {
        "instanceName": instance_name,
        "token": webhook_secret,
        "qrcode": True,
        "integration": "WHATSAPP-BAILEYS",

        # Settings
        "rejectCall": True,
        "msgCall": "Não aceitamos chamadas. Por favor, envie mensagem de texto.",
        "groupsIgnore": True,
        "alwaysOnline": False,
        "readMessages": False,
        "readStatus": False,

        # Webhook configuration
        "webhook": {
            "url": webhook_url,
            "byEvents": True,
            "base64": True,
            "events": [
                "QRCODE_UPDATED",
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE",
            ]
        }
    }

    print("Endpoint: POST /instance/create")
    print()
    print("Headers:")
    print(f"  Content-Type: application/json")
    print(f"  apikey: {settings.EVOLUTION_API_KEY}")
    print()
    print("Body (JSON):")
    print(json.dumps(payload, indent=2, ensure_ascii=False))
    print()
    print("=" * 80)
    print("VERIFICAÇÕES")
    print("=" * 80)
    print()
    print("✓ webhook.url está definido:", "url" in payload.get("webhook", {}))
    print("✓ webhook.byEvents está True:", payload.get("webhook", {}).get("byEvents") is True)
    print("✓ webhook.base64 está True:", payload.get("webhook", {}).get("base64") is True)
    print("✓ MESSAGES_UPSERT está nos eventos:", "MESSAGES_UPSERT" in payload.get("webhook", {}).get("events", []))
    print("✓ Quantidade de eventos:", len(payload.get("webhook", {}).get("events", [])))
    print()


def verificar_instancia_existente():
    """
    Verifica as configurações de uma instância existente
    """
    print("=" * 80)
    print("VERIFICANDO INSTÂNCIAS EXISTENTES")
    print("=" * 80)
    print()

    configuracoes = ConfiguracaoWhatsApp.objects.filter(instance_name__isnull=False).exclude(instance_name='')

    if not configuracoes.exists():
        print("❌ Nenhuma instância configurada no sistema")
        return

    for config in configuracoes:
        print(f"Empresa: {config.empresa.nome_fantasia}")
        print(f"Instance Name: {config.instance_name}")
        print(f"Status: {config.status}")
        print(f"Webhook URL: {config.webhook_url}")
        print()

        # Tentar sincronizar
        try:
            service = EvolutionAPIService(config)
            result = service.verificar_existencia_instancia()

            if result['success']:
                if result['exists']:
                    print("✓ Instância existe na Evolution API")
                else:
                    print("❌ Instância NÃO existe na Evolution API (foi deletada?)")
            else:
                print(f"❌ Erro ao verificar: {result.get('error')}")
        except Exception as e:
            print(f"❌ Erro ao conectar com Evolution API: {str(e)}")

        print("-" * 80)
        print()


if __name__ == "__main__":
    mostrar_payload_criacao()
    print()
    verificar_instancia_existente()
