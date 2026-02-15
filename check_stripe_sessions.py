#!/usr/bin/env python
"""Script para verificar checkout sessions no Stripe"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

import stripe
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

print("\n" + "="*60)
print("VERIFICANDO CHECKOUT SESSIONS NO STRIPE")
print("="*60)

try:
    sessions = stripe.checkout.Session.list(limit=50)

    if not sessions.data:
        print("\n❌ NENHUMA CHECKOUT SESSION ENCONTRADA")
        print("   Isso significa que os checkouts NÃO foram criados.")
        print("   Provável erro na criação da session (API key, price_id, etc)")
    else:
        print(f"\n✅ {len(sessions.data)} checkout sessions encontradas:\n")

        for s in sessions.data:
            status_emoji = "✅" if s.status == "complete" else "❌"
            print(f"{status_emoji} Session: {s.id[:20]}...")
            print(f"   Email: {s.customer_email or '(não informado)'}")
            print(f"   Status: {s.status}")
            print(f"   Criado em: {s.created}")
            if s.metadata:
                print(f"   Empresa: {s.metadata.get('empresa_nome', 'N/A')}")
            print()

except stripe.error.AuthenticationError:
    print("\n❌ ERRO DE AUTENTICAÇÃO")
    print("   Verifique se STRIPE_SECRET_KEY está configurada corretamente")

except Exception as e:
    print(f"\n❌ ERRO: {str(e)}")

print("="*60)
