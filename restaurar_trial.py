#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Restaurar trial de 7 dias no plano Essencial"""
import os, sys, django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from assinaturas.models import Plano

plano = Plano.objects.get(nome='essencial')
plano.trial_dias = 7
plano.save()

print('[OK] Trial de 7 dias restaurado!')
print(f'Plano: {plano.nome}')
print(f'Trial: {plano.trial_dias} dias')
