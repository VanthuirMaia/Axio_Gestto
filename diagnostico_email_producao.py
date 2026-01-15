#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script de Diagnóstico de Email para Produção
Executa verificações completas do sistema de envio de emails
"""
import os
import sys
import django
import socket
import smtplib
from datetime import datetime

# Configura o Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
from django.core.mail import send_mail

# Cores para output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'


def print_header(text):
    """Imprime cabeçalho formatado"""
    print(f"\n{BLUE}{'='*70}{RESET}")
    print(f"{BLUE}{text.center(70)}{RESET}")
    print(f"{BLUE}{'='*70}{RESET}\n")


def print_success(text):
    """Imprime mensagem de sucesso"""
    print(f"{GREEN}✓{RESET} {text}")


def print_error(text):
    """Imprime mensagem de erro"""
    print(f"{RED}✗{RESET} {text}")


def print_warning(text):
    """Imprime mensagem de aviso"""
    print(f"{YELLOW}⚠{RESET} {text}")


def print_info(text):
    """Imprime informação"""
    print(f"  {text}")


def verificar_variaveis_ambiente():
    """Verifica se todas as variáveis de ambiente necessárias estão configuradas"""
    print_header("1. VERIFICAÇÃO DE VARIÁVEIS DE AMBIENTE")
    
    variaveis = {
        'EMAIL_BACKEND': getattr(settings, 'EMAIL_BACKEND', None),
        'EMAIL_HOST': getattr(settings, 'EMAIL_HOST', None),
        'EMAIL_PORT': getattr(settings, 'EMAIL_PORT', None),
        'EMAIL_USE_TLS': getattr(settings, 'EMAIL_USE_TLS', None),
        'EMAIL_HOST_USER': getattr(settings, 'EMAIL_HOST_USER', None),
        'EMAIL_HOST_PASSWORD': getattr(settings, 'EMAIL_HOST_PASSWORD', None),
        'DEFAULT_FROM_EMAIL': getattr(settings, 'DEFAULT_FROM_EMAIL', None),
        'SITE_URL': getattr(settings, 'SITE_URL', None),
    }
    
    todas_ok = True
    
    for var, valor in variaveis.items():
        if valor is None or valor == '':
            print_error(f"{var}: NÃO CONFIGURADA")
            todas_ok = False
        else:
            # Oculta senhas
            if 'PASSWORD' in var:
                valor_exibir = f"{valor[:4]}...{valor[-4:]}" if len(valor) > 8 else "***"
            else:
                valor_exibir = valor
            print_success(f"{var}: {valor_exibir}")
    
    print()
    if todas_ok:
        print_success("Todas as variáveis de ambiente estão configuradas!")
    else:
        print_error("Algumas variáveis estão faltando. Configure-as no .env.prod")
    
    return todas_ok


def testar_conexao_smtp():
    """Testa a conexão com o servidor SMTP"""
    print_header("2. TESTE DE CONEXÃO SMTP")
    
    host = getattr(settings, 'EMAIL_HOST', None)
    port = getattr(settings, 'EMAIL_PORT', None)
    use_tls = getattr(settings, 'EMAIL_USE_TLS', False)
    user = getattr(settings, 'EMAIL_HOST_USER', None)
    password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
    
    if not all([host, port, user, password]):
        print_error("Configurações SMTP incompletas. Não é possível testar conexão.")
        return False
    
    try:
        print_info(f"Conectando a {host}:{port}...")
        
        # Testa resolução DNS
        try:
            ip = socket.gethostbyname(host)
            print_success(f"DNS resolvido: {host} -> {ip}")
        except socket.gaierror as e:
            print_error(f"Erro ao resolver DNS: {e}")
            return False
        
        # Testa conexão SMTP
        if use_tls:
            smtp = smtplib.SMTP(host, port, timeout=10)
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
        else:
            smtp = smtplib.SMTP(host, port, timeout=10)
        
        print_success(f"Conexão estabelecida com {host}:{port}")
        
        # Testa autenticação
        try:
            smtp.login(user, password)
            print_success(f"Autenticação bem-sucedida com usuário: {user}")
        except smtplib.SMTPAuthenticationError as e:
            print_error(f"Falha na autenticação: {e}")
            smtp.quit()
            return False
        
        smtp.quit()
        print_success("Conexão SMTP OK!")
        return True
        
    except smtplib.SMTPException as e:
        print_error(f"Erro SMTP: {e}")
        return False
    except socket.timeout:
        print_error("Timeout ao conectar ao servidor SMTP")
        return False
    except Exception as e:
        print_error(f"Erro inesperado: {type(e).__name__}: {e}")
        return False


def testar_envio_email(email_destino):
    """Testa o envio de um email real"""
    print_header("3. TESTE DE ENVIO DE EMAIL")
    
    if not email_destino:
        print_warning("Email de destino não fornecido. Pulando teste de envio.")
        return False
    
    try:
        print_info(f"Enviando email de teste para: {email_destino}")
        
        assunto = f"[TESTE] Diagnóstico de Email - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}"
        mensagem = f"""
Este é um email de teste do sistema de diagnóstico.

Informações do servidor:
- Host SMTP: {settings.EMAIL_HOST}
- Porta: {settings.EMAIL_PORT}
- TLS: {settings.EMAIL_USE_TLS}
- Remetente: {settings.DEFAULT_FROM_EMAIL}

Se você recebeu este email, o sistema de envio está funcionando corretamente!

Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}
"""
        
        send_mail(
            subject=assunto,
            message=mensagem,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email_destino],
            fail_silently=False,
        )
        
        print_success(f"Email enviado com sucesso para {email_destino}!")
        print_info("Verifique a caixa de entrada (e spam) do destinatário.")
        return True
        
    except Exception as e:
        print_error(f"Erro ao enviar email: {type(e).__name__}: {e}")
        import traceback
        print_info("Traceback completo:")
        traceback.print_exc()
        return False


def verificar_logs():
    """Verifica logs recentes de erros"""
    print_header("4. VERIFICAÇÃO DE LOGS")
    
    log_file = settings.BASE_DIR / 'logs' / 'django.log'
    
    if not log_file.exists():
        print_warning(f"Arquivo de log não encontrado: {log_file}")
        print_info("Logs podem estar sendo enviados apenas para console.")
        return
    
    try:
        print_info(f"Lendo últimas 50 linhas de: {log_file}")
        
        with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
            linhas = f.readlines()
            ultimas_linhas = linhas[-50:] if len(linhas) > 50 else linhas
        
        # Filtra linhas relacionadas a email
        linhas_email = [l for l in ultimas_linhas if 'email' in l.lower() or 'smtp' in l.lower()]
        
        if linhas_email:
            print_warning(f"Encontradas {len(linhas_email)} linhas relacionadas a email:")
            for linha in linhas_email[-10:]:  # Mostra últimas 10
                print_info(linha.strip())
        else:
            print_success("Nenhum erro relacionado a email nos logs recentes.")
            
    except Exception as e:
        print_error(f"Erro ao ler logs: {e}")


def gerar_relatorio():
    """Gera relatório de configuração"""
    print_header("5. RELATÓRIO DE CONFIGURAÇÃO")
    
    print_info(f"Django Settings Module: {os.environ.get('DJANGO_SETTINGS_MODULE')}")
    print_info(f"DEBUG: {settings.DEBUG}")
    print_info(f"ALLOWED_HOSTS: {settings.ALLOWED_HOSTS}")
    print_info(f"BASE_DIR: {settings.BASE_DIR}")
    print()
    
    print_info("Configuração de Email:")
    print_info(f"  Backend: {settings.EMAIL_BACKEND}")
    print_info(f"  Host: {settings.EMAIL_HOST}")
    print_info(f"  Port: {settings.EMAIL_PORT}")
    print_info(f"  TLS: {settings.EMAIL_USE_TLS}")
    print_info(f"  User: {settings.EMAIL_HOST_USER}")
    print_info(f"  From: {settings.DEFAULT_FROM_EMAIL}")
    print_info(f"  Site URL: {getattr(settings, 'SITE_URL', 'NÃO CONFIGURADO')}")


def main():
    """Função principal"""
    print_header("DIAGNÓSTICO DE EMAIL - AXIO GESTTO")
    print_info(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print_info(f"Ambiente: {'PRODUÇÃO' if not settings.DEBUG else 'DESENVOLVIMENTO'}")
    
    # Executa verificações
    variaveis_ok = verificar_variaveis_ambiente()
    
    if variaveis_ok:
        smtp_ok = testar_conexao_smtp()
        
        if smtp_ok:
            # Solicita email de teste
            print()
            email_teste = input(f"{YELLOW}Digite um email para teste (ou Enter para pular): {RESET}").strip()
            if email_teste:
                testar_envio_email(email_teste)
    
    verificar_logs()
    gerar_relatorio()
    
    # Resumo final
    print_header("RESUMO DO DIAGNÓSTICO")
    
    if not variaveis_ok:
        print_error("PROBLEMA: Variáveis de ambiente não configuradas corretamente")
        print_info("SOLUÇÃO: Configure todas as variáveis no arquivo .env.prod")
    elif not smtp_ok:
        print_error("PROBLEMA: Não foi possível conectar ao servidor SMTP")
        print_info("SOLUÇÃO: Verifique credenciais do Brevo e firewall do servidor")
    else:
        print_success("Configuração parece estar correta!")
        print_info("Se emails ainda não estão sendo enviados, verifique:")
        print_info("  1. Logs da aplicação durante tentativa de envio")
        print_info("  2. Dashboard do Brevo (https://app.brevo.com)")
        print_info("  3. Limite de envios do Brevo (300/dia no plano gratuito)")
    
    print()


if __name__ == '__main__':
    main()
