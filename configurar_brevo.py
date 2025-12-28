#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script auxiliar para configurar Brevo no projeto
Ajuda a validar as credenciais e testar o envio
"""
import os
import sys

# Cores para terminal (compatível com Windows)
try:
    from colorama import init, Fore, Style
    init()
    GREEN = Fore.GREEN
    RED = Fore.RED
    YELLOW = Fore.YELLOW
    BLUE = Fore.BLUE
    RESET = Style.RESET_ALL
except ImportError:
    GREEN = RED = YELLOW = BLUE = RESET = ""


def print_header():
    """Exibe cabeçalho do script"""
    print("\n" + "="*70)
    print(f"{BLUE}CONFIGURADOR DE EMAIL BREVO - AXIO GESTTO{RESET}")
    print("="*70 + "\n")


def print_step(number, title):
    """Exibe número do passo"""
    print(f"\n{GREEN}[PASSO {number}]{RESET} {title}")
    print("-" * 70)


def check_env_file():
    """Verifica se existe arquivo .env"""
    print_step(1, "Verificando arquivo .env")

    if os.path.exists('.env'):
        print(f"{GREEN}✓{RESET} Arquivo .env encontrado")
        return True
    else:
        print(f"{YELLOW}⚠{RESET} Arquivo .env não encontrado")
        print(f"\nCrie um arquivo .env baseado no .env.brevo.example:")
        print(f"{BLUE}cp .env.brevo.example .env{RESET}")
        return False


def get_env_value(key):
    """Pega valor do .env"""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, '')
    except ImportError:
        print(f"{YELLOW}⚠{RESET} Módulo python-dotenv não instalado")
        print("Instalando: pip install python-dotenv")
        os.system(f"{sys.executable} -m pip install python-dotenv")
        from dotenv import load_dotenv
        load_dotenv()
        return os.getenv(key, '')


def check_brevo_config():
    """Verifica configuração da Brevo"""
    print_step(2, "Verificando configuração da Brevo")

    config = {
        'EMAIL_BACKEND': get_env_value('EMAIL_BACKEND'),
        'EMAIL_HOST': get_env_value('EMAIL_HOST'),
        'EMAIL_PORT': get_env_value('EMAIL_PORT'),
        'EMAIL_USE_TLS': get_env_value('EMAIL_USE_TLS'),
        'EMAIL_HOST_USER': get_env_value('EMAIL_HOST_USER'),
        'EMAIL_HOST_PASSWORD': get_env_value('EMAIL_HOST_PASSWORD'),
        'DEFAULT_FROM_EMAIL': get_env_value('DEFAULT_FROM_EMAIL'),
    }

    all_ok = True

    # Verifica EMAIL_HOST
    if 'brevo' in config['EMAIL_HOST'] or 'sendinblue' in config['EMAIL_HOST']:
        print(f"{GREEN}✓{RESET} EMAIL_HOST configurado para Brevo: {config['EMAIL_HOST']}")
    else:
        print(f"{RED}✗{RESET} EMAIL_HOST não está configurado para Brevo")
        print(f"  Valor atual: {config['EMAIL_HOST']}")
        print(f"  Configure: EMAIL_HOST=smtp-relay.brevo.com")
        all_ok = False

    # Verifica EMAIL_PORT
    if config['EMAIL_PORT'] == '587':
        print(f"{GREEN}✓{RESET} EMAIL_PORT correto: 587")
    else:
        print(f"{YELLOW}⚠{RESET} EMAIL_PORT deveria ser 587, está: {config['EMAIL_PORT']}")

    # Verifica EMAIL_HOST_USER
    if config['EMAIL_HOST_USER'] and '@' in config['EMAIL_HOST_USER']:
        print(f"{GREEN}✓{RESET} EMAIL_HOST_USER configurado: {config['EMAIL_HOST_USER']}")
    else:
        print(f"{RED}✗{RESET} EMAIL_HOST_USER não configurado ou inválido")
        print(f"  Configure com o email da sua conta Brevo")
        all_ok = False

    # Verifica EMAIL_HOST_PASSWORD
    if config['EMAIL_HOST_PASSWORD'] and len(config['EMAIL_HOST_PASSWORD']) > 20:
        print(f"{GREEN}✓{RESET} EMAIL_HOST_PASSWORD configurado (SMTP Key)")
    else:
        print(f"{RED}✗{RESET} EMAIL_HOST_PASSWORD não configurado ou muito curto")
        print(f"  Configure com a SMTP Key gerada na Brevo")
        all_ok = False

    # Verifica DEFAULT_FROM_EMAIL
    if config['DEFAULT_FROM_EMAIL'] and '@' in config['DEFAULT_FROM_EMAIL']:
        print(f"{GREEN}✓{RESET} DEFAULT_FROM_EMAIL configurado: {config['DEFAULT_FROM_EMAIL']}")
        print(f"{YELLOW}⚠{RESET} IMPORTANTE: Verifique se este email foi autorizado na Brevo")
        print(f"  Brevo → Settings → Senders & IP → Add a sender")
    else:
        print(f"{RED}✗{RESET} DEFAULT_FROM_EMAIL não configurado")
        all_ok = False

    return all_ok


def test_smtp_connection():
    """Testa conexão SMTP com Brevo"""
    print_step(3, "Testando conexão SMTP")

    try:
        import smtplib
        from email.mime.text import MIMEText

        host = get_env_value('EMAIL_HOST')
        port = int(get_env_value('EMAIL_PORT') or 587)
        user = get_env_value('EMAIL_HOST_USER')
        password = get_env_value('EMAIL_HOST_PASSWORD')

        print(f"Conectando em {host}:{port}...")

        server = smtplib.SMTP(host, port, timeout=10)
        server.starttls()
        server.login(user, password)

        print(f"{GREEN}✓{RESET} Conexão SMTP estabelecida com sucesso!")
        print(f"{GREEN}✓{RESET} Autenticação realizada com sucesso!")

        server.quit()
        return True

    except smtplib.SMTPAuthenticationError:
        print(f"{RED}✗{RESET} Erro de autenticação!")
        print(f"  Verifique EMAIL_HOST_USER e EMAIL_HOST_PASSWORD")
        print(f"  Gere uma nova SMTP Key na Brevo se necessário")
        return False
    except Exception as e:
        print(f"{RED}✗{RESET} Erro ao conectar: {e}")
        return False


def test_email_send():
    """Envia email de teste"""
    print_step(4, "Enviando email de teste")

    test_email = input(f"\n{BLUE}Digite um email para teste (ou Enter para pular):{RESET} ").strip()

    if not test_email or '@' not in test_email:
        print(f"{YELLOW}⚠{RESET} Teste de envio pulado")
        return

    try:
        import django
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
        django.setup()

        from django.core.mail import send_mail
        from django.conf import settings

        print(f"\nEnviando email de teste para {test_email}...")

        send_mail(
            subject='[TESTE] Configuração Brevo - Axio Gestto',
            message='Este é um email de teste da configuração do Brevo no Axio Gestto.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=False,
        )

        print(f"{GREEN}✓{RESET} Email enviado com sucesso!")
        print(f"\n{YELLOW}Verifique:{RESET}")
        print(f"  1. Caixa de entrada do email {test_email}")
        print(f"  2. Pasta de Spam/Lixo eletrônico")
        print(f"  3. Dashboard da Brevo: https://app.brevo.com/statistics/email")

    except Exception as e:
        print(f"{RED}✗{RESET} Erro ao enviar email: {e}")


def show_help():
    """Exibe informações úteis"""
    print_step(5, "Informações Úteis")

    print(f"\n{BLUE}Links importantes:{RESET}")
    print(f"  • Dashboard Brevo: https://app.brevo.com/")
    print(f"  • SMTP Settings: https://app.brevo.com/settings/keys/smtp")
    print(f"  • Senders: https://app.brevo.com/settings/senders")
    print(f"  • Documentação: https://developers.brevo.com/docs")

    print(f"\n{BLUE}Comandos úteis:{RESET}")
    print(f"  • Testar sistema de emails: python testar_emails.py")
    print(f"  • Ver documentação completa: cat docs/CONFIGURACAO_EMAIL_BREVO.md")

    print(f"\n{BLUE}Limites do plano gratuito:{RESET}")
    print(f"  • 300 emails por dia")
    print(f"  • 9.000 emails por mês")
    print(f"  • Sem limite de remetentes autorizados")


def main():
    """Função principal"""
    print_header()

    # Passo 1: Verificar .env
    if not check_env_file():
        print(f"\n{RED}Corrija os problemas acima e execute novamente.{RESET}\n")
        return

    # Passo 2: Verificar configuração
    config_ok = check_brevo_config()

    if not config_ok:
        print(f"\n{RED}Corrija as configurações no arquivo .env e execute novamente.{RESET}\n")
        return

    # Passo 3: Testar conexão
    connection_ok = test_smtp_connection()

    if not connection_ok:
        print(f"\n{RED}Não foi possível conectar ao servidor Brevo.{RESET}\n")
        return

    # Passo 4: Teste de envio (opcional)
    test_email_send()

    # Passo 5: Informações
    show_help()

    print("\n" + "="*70)
    print(f"{GREEN}CONFIGURAÇÃO CONCLUÍDA COM SUCESSO!{RESET}")
    print("="*70 + "\n")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{YELLOW}Operação cancelada pelo usuário.{RESET}\n")
        sys.exit(0)
