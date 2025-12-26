"""
Script para listar todos os usuários e suas empresas
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from empresas.models import Empresa

User = get_user_model()

print('[*] Listando todos os usuarios...\n')

usuarios = User.objects.all()

if not usuarios:
    print('[AVISO] Nenhum usuario encontrado no banco!')
else:
    for user in usuarios:
        print(f'Usuario: {user.username} (ID: {user.id})')
        print(f'  Email: {user.email}')
        print(f'  Nome: {user.first_name} {user.last_name}')
        print(f'  Staff: {user.is_staff}')
        print(f'  Superuser: {user.is_superuser}')

        if hasattr(user, 'empresa'):
            empresa = user.empresa
            print(f'  Empresa: {empresa.nome} (ID: {empresa.id})')

            if hasattr(empresa, 'assinatura'):
                assinatura = empresa.assinatura
                print(f'  Assinatura: {assinatura.plano.get_nome_display()} - {assinatura.get_status_display()}')
            else:
                print(f'  Assinatura: SEM ASSINATURA!')
        else:
            print(f'  Empresa: SEM EMPRESA!')

        print()
