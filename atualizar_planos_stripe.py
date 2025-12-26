#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para atualizar os planos com os Price IDs do Stripe
Execute: python atualizar_planos_stripe.py
"""

import os
import sys
import django

# Fix encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assinaturas.models import Plano

def atualizar_planos():
    """Atualiza os stripe_price_id dos planos"""

    # Price IDs do Stripe
    price_ids = {
        'essencial': 'price_1SiaBDEOfuBf9VWtRdF5EG81',
        'profissional': 'price_1SiaBaEOfuBf9VWtGFlixF1Z',
        'empresarial': 'price_1SiaBrEOfuBf9VWt0AmAoR3X',
    }

    print("[*] Atualizando planos com Price IDs do Stripe...\n")

    for nome_plano, price_id in price_ids.items():
        try:
            plano = Plano.objects.get(nome__iexact=nome_plano)
            plano.stripe_price_id = price_id
            plano.save()

            print(f"[OK] Plano '{plano.nome}' atualizado:")
            print(f"   - Preco: R$ {plano.preco_mensal}")
            print(f"   - Price ID: {price_id}\n")

        except Plano.DoesNotExist:
            print(f"[ERRO] Plano '{nome_plano}' nao encontrado no banco!")
            print(f"   Execute: python manage.py loaddata assinaturas/fixtures/planos_iniciais.json\n")

    print("[*] Atualizacao concluida!")
    print("\n[*] Verificacao:")

    for plano in Plano.objects.all():
        status = "[OK]" if plano.stripe_price_id else "[ERRO]"
        print(f"{status} {plano.nome}: {plano.stripe_price_id or 'SEM PRICE ID'}")

if __name__ == '__main__':
    atualizar_planos()
