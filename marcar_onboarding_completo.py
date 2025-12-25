#!/usr/bin/env python
"""
Script para marcar empresas existentes como onboarding completo
Execute: python marcar_onboarding_completo.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from empresas.models import Empresa

# Pegar todas as empresas
empresas = Empresa.objects.all()

print(f"\n=== EMPRESAS NO BANCO: {empresas.count()} ===\n")

if empresas.count() == 0:
    print("❌ Nenhuma empresa encontrada!")
else:
    atualizadas = 0
    for empresa in empresas:
        if not empresa.onboarding_completo:
            empresa.onboarding_completo = True
            empresa.save()
            print(f"✅ {empresa.nome} → onboarding marcado como completo")
            atualizadas += 1
        else:
            print(f"⏭️  {empresa.nome} → já estava completo")

    print(f"\n📊 Total: {empresas.count()} empresas")
    print(f"✅ Atualizadas: {atualizadas}")
    print(f"⏭️  Já completas: {empresas.count() - atualizadas}")
    print("\n✅ Pronto! Agora você pode fazer login normalmente.\n")
