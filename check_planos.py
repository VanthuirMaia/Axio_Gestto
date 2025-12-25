#!/usr/bin/env python
"""Script para verificar planos no banco"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assinaturas.models import Plano

planos = Plano.objects.all()
print(f'\n=== PLANOS NO BANCO: {planos.count()} ===\n')

if planos.count() == 0:
    print('❌ NENHUM PLANO ENCONTRADO!')
    print('Execute: python manage.py loaddata assinaturas/fixtures/planos_iniciais.json')
else:
    for p in planos:
        print(f'✅ {p.get_nome_display()}')
        print(f'   - ID: {p.id}')
        print(f'   - Nome: {p.nome}')
        print(f'   - Preço: R$ {p.preco_mensal}')
        print(f'   - Profissionais: {p.max_profissionais}')
        print(f'   - Agendamentos: {p.max_agendamentos_mes}')
        print(f'   - Ativo: {p.ativo}')
        print()
