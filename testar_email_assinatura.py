#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script para testar o sistema de emails integrado com assinaturas
Testa se:
1. Email com senha é enviado ao criar tenant via assinatura
2. Email sem senha é enviado ao criar usuário manual
3. Não há duplicação de emails
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

from django.conf import settings
from core.models import Usuario
from empresas.models import Empresa
from assinaturas.models import Plano, Assinatura
from assinaturas.views import _gerar_senha_temporaria, _enviar_email_boas_vindas
from django.utils.timezone import now, timedelta
from django.utils.text import slugify


def limpar_testes():
    """Remove dados de teste anteriores"""
    print("\n🧹 Limpando dados de teste anteriores...")

    Usuario.objects.filter(email__contains='teste_assinatura').delete()
    Empresa.objects.filter(cnpj__contains='99999999').delete()

    print("✓ Dados limpos\n")


def criar_plano_teste():
    """Cria ou obtém plano de teste"""
    plano, created = Plano.objects.get_or_create(
        nome='essencial',
        defaults={
            'preco_mensal': 99.90,
            'trial_dias': 7,
            'max_profissionais': 3,
            'max_agendamentos_mes': 100,
            'ativo': True,
        }
    )

    if created:
        print(f"✓ Plano de teste criado: {plano.nome}")
    else:
        print(f"✓ Plano existente encontrado: {plano.nome}")

    return plano


def teste_1_usuario_via_assinatura():
    """
    TESTE 1: Criar usuário via sistema de assinatura
    ESPERADO: 1 email HTML com senha
    """
    print("\n" + "="*70)
    print("TESTE 1: Usuário criado VIA ASSINATURA")
    print("="*70)
    print("Esperado: 1 email HTML bonito com senha incluída")
    print("-"*70)

    # Criar empresa
    empresa = Empresa.objects.create(
        nome='Salão Teste Assinatura',
        slug='salao-teste-assinatura',
        email='empresa_teste@example.com',
        telefone='(81) 99999-9999',
        cnpj='99.999.999/9999-99',
        ativa=True,
    )
    print(f"✓ Empresa criada: {empresa.nome}")

    # Criar plano
    plano = criar_plano_teste()

    # Criar assinatura
    assinatura = Assinatura.objects.create(
        empresa=empresa,
        plano=plano,
        status='trial',
        data_expiracao=now() + timedelta(days=plano.trial_dias),
        trial_ativo=True,
    )
    print(f"✓ Assinatura criada: Trial de {plano.trial_dias} dias")

    # Criar usuário (isso dispara o signal, mas deve ser ignorado pois tem empresa)
    senha_gerada = _gerar_senha_temporaria()
    usuario = Usuario.objects.create_user(
        username='admin_teste_assinatura',
        email='usuario_teste_assinatura@example.com',
        password=senha_gerada,
        empresa=empresa,
        first_name='Admin',
        last_name='Teste',
    )
    print(f"✓ Usuário criado: {usuario.email}")
    print(f"  Senha gerada: {senha_gerada}")

    # Enviar email via função de assinatura
    print("\n📧 Enviando email de boas-vindas COM SENHA...")
    _enviar_email_boas_vindas(usuario, empresa, senha_gerada, plano)

    print("\n" + "="*70)
    print("RESULTADO ESPERADO:")
    print("  ✅ 1 email HTML com:")
    print(f"     - Email: {usuario.email}")
    print(f"     - Senha: {senha_gerada}")
    print(f"     - Plano: {plano.nome}")
    print(f"     - Trial: {plano.trial_dias} dias")
    print("  ❌ SEM email duplicado (signal foi ignorado)")
    print("="*70)


def teste_2_usuario_manual():
    """
    TESTE 2: Criar usuário manual (sem empresa)
    ESPERADO: 1 email HTML SEM senha (via signal)
    """
    print("\n" + "="*70)
    print("TESTE 2: Usuário criado MANUALMENTE (sem empresa)")
    print("="*70)
    print("Esperado: 1 email HTML simples SEM senha (via signal)")
    print("-"*70)

    # Criar usuário SEM empresa (dispara signal)
    usuario = Usuario.objects.create_user(
        username='usuario_manual_teste',
        email='usuario_manual_teste@example.com',
        password='senha123',
        first_name='Usuário',
        last_name='Manual',
        # SEM empresa!
    )
    print(f"✓ Usuário criado: {usuario.email}")
    print(f"  Tem empresa? {usuario.empresa is not None}")

    print("\n" + "="*70)
    print("RESULTADO ESPERADO:")
    print("  ✅ 1 email HTML simples via signal (SEM senha)")
    print(f"     - Email: {usuario.email}")
    print("  ❌ Senha NÃO incluída no email (signal não tem acesso)")
    print("="*70)


def teste_3_verificar_templates():
    """
    TESTE 3: Verificar se os templates existem
    """
    print("\n" + "="*70)
    print("TESTE 3: Verificando templates de email")
    print("="*70)

    templates = [
        'templates/emails/boas_vindas_com_senha.html',
        'templates/emails/usuario_boas_vindas.html',
        'templates/emails/empresa_criada.html',
        'templates/emails/password_reset_email.html',
    ]

    from pathlib import Path
    base_dir = Path(__file__).resolve().parent

    for template in templates:
        path = base_dir / template
        exists = path.exists()
        status = "✓" if exists else "✗"
        print(f"{status} {template}")

    print("="*70)


def main():
    print("\n" + "="*70)
    print("TESTADOR DE SISTEMA DE EMAILS INTEGRADO - AXIO GESTTO")
    print("="*70)

    print(f"\nConfiguração atual:")
    print(f"  EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"  DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"  SITE_URL: {settings.SITE_URL}")

    # Limpar dados anteriores
    limpar_testes()

    # Executar testes
    teste_3_verificar_templates()
    teste_1_usuario_via_assinatura()
    teste_2_usuario_manual()

    print("\n" + "="*70)
    print("TESTES CONCLUÍDOS")
    print("="*70)

    print("\n📋 RESUMO:")
    print("  1. Email VIA ASSINATURA: HTML bonito com senha")
    print("  2. Email MANUAL: HTML simples sem senha (via signal)")
    print("  3. SEM duplicação: Signal ignora usuários com empresa")

    print("\n💡 DICA:")
    print("  Se EMAIL_BACKEND = console, os emails aparecem no terminal acima")
    print("  Se EMAIL_BACKEND = smtp, verifique sua caixa de entrada")

    print("\n🧹 LIMPEZA:")
    try:
        resposta = input("Deseja remover os dados de teste? (s/N): ").strip().lower()
        if resposta == 's':
            limpar_testes()
            print("✓ Dados de teste removidos")
        else:
            print("⚠ Dados de teste mantidos no banco")
    except (EOFError, KeyboardInterrupt):
        print("\n⚠ Dados de teste mantidos no banco (execução automática)")

    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠ Operação cancelada pelo usuário.\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Erro: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
