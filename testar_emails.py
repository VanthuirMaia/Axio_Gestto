#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar o sistema de envio de emails
"""
import os
import sys
import django

# Configura encoding para Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
from core.models import Usuario
from empresas.models import Empresa


def testar_email_direto():
    """Testa envio de email direto"""
    print("\n=== Testando envio de email direto ===")
    try:
        send_mail(
            subject='Teste de Email - Axio Gestto',
            message='Este é um email de teste do sistema Axio Gestto.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=['teste@example.com'],
            fail_silently=False,
        )
        print("✓ Email de teste enviado com sucesso!")
    except Exception as e:
        print(f"✗ Erro ao enviar email: {e}")


def testar_template_usuario():
    """Testa template de boas-vindas do usuário"""
    print("\n=== Testando template de boas-vindas do usuário ===")
    try:
        # Cria um usuário de teste (ou pega um existente)
        usuario, created = Usuario.objects.get_or_create(
            username='teste_email',
            defaults={
                'email': 'usuario_teste@example.com',
                'first_name': 'Teste',
                'last_name': 'Email',
            }
        )

        if not created:
            print(f"Usuário já existe: {usuario.username}")

        # Renderiza o template
        context = {
            'usuario': usuario,
            'site_url': settings.SITE_URL,
        }
        html_message = render_to_string('emails/usuario_boas_vindas.html', context)
        plain_message = strip_tags(html_message)

        # Envia o email
        send_mail(
            subject='Bem-vindo ao Axio Gestto!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[usuario.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✓ Email de boas-vindas enviado para {usuario.email}")

        if created:
            # Limpa o usuário de teste
            usuario.delete()
            print("✓ Usuário de teste removido")

    except Exception as e:
        print(f"✗ Erro ao testar template de usuário: {e}")


def testar_template_empresa():
    """Testa template de empresa criada"""
    print("\n=== Testando template de empresa criada ===")
    try:
        # Cria uma empresa de teste (ou pega uma existente)
        empresa, created = Empresa.objects.get_or_create(
            cnpj='00.000.000/0000-99',
            defaults={
                'nome': 'Empresa Teste Email',
                'slug': 'empresa-teste-email',
                'email': 'empresa_teste@example.com',
                'telefone': '(81) 99999-9999',
            }
        )

        if not created:
            print(f"Empresa já existe: {empresa.nome}")

        # Renderiza o template
        context = {
            'empresa': empresa,
            'site_url': settings.SITE_URL,
        }
        html_message = render_to_string('emails/empresa_criada.html', context)
        plain_message = strip_tags(html_message)

        # Envia o email
        send_mail(
            subject=f'Empresa {empresa.nome} cadastrada com sucesso!',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[empresa.email],
            html_message=html_message,
            fail_silently=False,
        )
        print(f"✓ Email de empresa criada enviado para {empresa.email}")

        if created:
            # Limpa a empresa de teste
            empresa.delete()
            print("✓ Empresa de teste removida")

    except Exception as e:
        print(f"✗ Erro ao testar template de empresa: {e}")


def testar_signals():
    """Testa se os signals estão disparando corretamente"""
    print("\n=== Testando signals ===")

    # Testa signal de usuário
    print("\n--- Signal de Usuário ---")
    try:
        usuario = Usuario.objects.create_user(
            username='teste_signal_usuario',
            email='signal_usuario@example.com',
            first_name='Signal',
            last_name='Usuario',
            password='senha123'
        )
        print(f"✓ Usuário criado: {usuario.username}")
        print("✓ Se configurado corretamente, o signal deve ter enviado um email")

        # Limpa
        usuario.delete()
        print("✓ Usuário de teste removido")
    except Exception as e:
        print(f"✗ Erro ao testar signal de usuário: {e}")

    # Testa signal de empresa
    print("\n--- Signal de Empresa ---")
    try:
        empresa = Empresa.objects.create(
            nome='Empresa Signal Teste',
            slug='empresa-signal-teste',
            cnpj='11.111.111/1111-11',
            email='signal_empresa@example.com',
            telefone='(81) 88888-8888',
        )
        print(f"✓ Empresa criada: {empresa.nome}")
        print("✓ Se configurado corretamente, o signal deve ter enviado um email")

        # Limpa
        empresa.delete()
        print("✓ Empresa de teste removida")
    except Exception as e:
        print(f"✗ Erro ao testar signal de empresa: {e}")


def main():
    print("\n" + "="*60)
    print("TESTADOR DE SISTEMA DE EMAILS - AXIO GESTTO")
    print("="*60)

    print(f"\nConfiguração atual:")
    print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"  SITE_URL: {settings.SITE_URL}")

    # Executa os testes
    testar_email_direto()
    testar_template_usuario()
    testar_template_empresa()
    testar_signals()

    print("\n" + "="*60)
    print("TESTES CONCLUÍDOS")
    print("="*60)
    print("\nOBSERVAÇÕES:")
    print("- Se EMAIL_BACKEND = console, os emails aparecem no terminal")
    print("- Para enviar emails reais, configure SMTP no .env:")
    print("    EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend")
    print("    EMAIL_HOST=smtp.gmail.com")
    print("    EMAIL_PORT=587")
    print("    EMAIL_USE_TLS=True")
    print("    EMAIL_HOST_USER=seu_email@gmail.com")
    print("    EMAIL_HOST_PASSWORD=sua_senha_app")
    print("="*60 + "\n")


if __name__ == '__main__':
    main()
