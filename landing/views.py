"""
Views da Landing Page (público)
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from assinaturas.models import Plano
import requests


def home(request):
    """Página inicial da landing page"""
    context = {
        'site_name': 'Gestto',
        'tagline': 'Sistema completo de agendamentos com WhatsApp',
    }
    return render(request, 'landing/home.html', context)


def precos(request):
    """Página de preços com os planos"""
    planos = Plano.objects.filter(ativo=True).order_by('ordem_exibicao')

    context = {
        'planos': planos,
    }
    return render(request, 'landing/precos.html', context)


@require_http_methods(["GET", "POST"])
def cadastro(request):
    """Formulário de cadastro de novo cliente"""
    if request.method == 'POST':
        # Extrair dados do formulário
        nome_empresa = request.POST.get('nome_empresa')
        email_admin = request.POST.get('email_admin')
        telefone = request.POST.get('telefone')
        cnpj = request.POST.get('cnpj')
        plano = request.POST.get('plano', 'essencial')
        gateway = request.POST.get('gateway', 'stripe')

        # Validações básicas
        if not nome_empresa or not email_admin or not telefone or not cnpj:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('landing:cadastro')

        # Chamar API interna de create-tenant
        try:
            payload = {
                'nome_empresa': nome_empresa,
                'email_admin': email_admin,
                'telefone': telefone,
                'cnpj': cnpj,
                'plano': plano,
                'gateway': gateway
            }

            # Debug: log do payload
            import logging
            logger = logging.getLogger(__name__)
            logger.info(f"Enviando para API: {payload}")

            response = requests.post(
                f"{request.scheme}://{request.get_host()}/api/create-tenant/",
                json=payload,
                timeout=10
            )

            # Debug: log da resposta
            logger.info(f"Status Code: {response.status_code}")
            logger.info(f"Resposta: {response.text}")

            data = response.json()

            if data.get('sucesso'):
                # Redirecionar para página de checkout
                checkout_url = data.get('checkout_url')
                if checkout_url:
                    return redirect(checkout_url)
                else:
                    messages.success(request, 'Cadastro realizado! Verifique seu email.')
                    return redirect('landing:home')
            else:
                # Mostrar erro retornado pela API
                erro = data.get('erro') or data.get('mensagem', 'Erro ao processar cadastro.')
                messages.error(request, f'Erro: {erro}')
                return redirect('landing:cadastro')

        except Exception as e:
            messages.error(request, f'Erro ao processar cadastro: {str(e)}')
            return redirect('landing:cadastro')

    # GET - Mostrar formulário
    planos = Plano.objects.filter(ativo=True).order_by('ordem_exibicao')

    context = {
        'planos': planos,
    }
    return render(request, 'landing/cadastro.html', context)


def sobre(request):
    """Página sobre a empresa"""
    return render(request, 'landing/sobre.html')


def contato(request):
    """Página de contato"""
    return render(request, 'landing/contato.html')


def checkout_sucesso(request):
    """Página de sucesso após checkout do Stripe"""
    session_id = request.GET.get('session_id')

    context = {
        'session_id': session_id,
    }
    return render(request, 'landing/checkout_sucesso.html', context)


def checkout_cancelado(request):
    """Página quando usuário cancela o checkout"""
    return render(request, 'landing/checkout_cancelado.html')


def termos_uso(request):
    """Página de Termos de Uso e Política de Cancelamento"""
    return render(request, 'landing/termos_uso.html')


def politica_cancelamento(request):
    """Página de Política de Cancelamento (CDC)"""
    return render(request, 'landing/politica_cancelamento.html')
