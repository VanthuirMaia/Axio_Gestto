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
        plano = request.POST.get('plano', 'essencial')
        gateway = request.POST.get('gateway', 'stripe')

        # Validações básicas
        if not nome_empresa or not email_admin or not telefone:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            return redirect('landing:cadastro')

        # Chamar API interna de create-tenant
        try:
            response = requests.post(
                f"{request.scheme}://{request.get_host()}/api/create-tenant/",
                json={
                    'nome_empresa': nome_empresa,
                    'email_admin': email_admin,
                    'telefone': telefone,
                    'plano': plano,
                    'gateway': gateway
                },
                timeout=10
            )

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
                messages.error(request, data.get('mensagem', 'Erro ao processar cadastro.'))
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
