"""
Views da Landing Page (público)
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit
from assinaturas.models import Plano
import requests
import logging

# Logger específico para landing page
logger = logging.getLogger('landing')


@ratelimit(key='ip', rate='60/m', method='GET', block=True)
def home(request):
    """Página inicial da landing page"""
    logger.info(f"Acesso à home - IP: {request.META.get('REMOTE_ADDR')}")
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
@ratelimit(key='ip', rate='10/h', method='POST', block=True)  # Máximo 10 cadastros por hora por IP
@ratelimit(key='ip', rate='30/m', method='GET', block=True)
def cadastro(request):
    """Formulário de cadastro de novo cliente"""
    if request.method == 'POST':
        # Extrair dados do formulário
        nome_empresa = request.POST.get('nome_empresa')
        email_admin = request.POST.get('email_admin')
        telefone = request.POST.get('telefone')
        cnpj = request.POST.get('cnpj')
        plano = request.POST.get('plano', 'essencial')
        gateway = request.POST.get('gateway', 'manual')

        # Log de tentativa de cadastro
        logger.warning(f"Tentativa de cadastro - IP: {request.META.get('REMOTE_ADDR')}, Email: {email_admin}, Empresa: {nome_empresa}")

        # Validações básicas
        if not nome_empresa or not email_admin or not telefone or not cnpj:
            messages.error(request, 'Preencha todos os campos obrigatórios.')
            logger.warning(f"Cadastro incompleto - IP: {request.META.get('REMOTE_ADDR')}")
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
                logger.info(f"Cadastro bem-sucedido - Email: {email_admin}, Empresa: {nome_empresa}")
                if checkout_url:
                    return redirect(checkout_url)
                else:
                    messages.success(request, 'Cadastro realizado! Verifique seu email.')
                    return redirect('landing:home')
            else:
                # Mostrar erro retornado pela API
                erro = data.get('erro') or data.get('mensagem', 'Erro ao processar cadastro.')
                logger.error(f"Erro na API de cadastro - Email: {email_admin}, Erro: {erro}")
                messages.error(request, f'Erro: {erro}')
                return redirect('landing:cadastro')

        except Exception as e:
            logger.error(f"Exceção no cadastro - Email: {email_admin}, Erro: {str(e)}")
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
    """Página de Política de Cancelamento"""
    return render(request, 'landing/politica_cancelamento.html')


@require_http_methods(["POST"])
@ratelimit(key='ip', rate='100/m', method='POST', block=True)
def track_event(request):
    """Endpoint para receber eventos de analytics do frontend"""
    try:
        import json
        from .models import UserEvent
        
        # Parse do JSON
        data = json.loads(request.body)
        
        event_type = data.get('event_type')
        event_data = data.get('event_data', {})
        page_url = data.get('page_url', request.META.get('HTTP_REFERER', ''))
        
        # Validar tipo de evento
        valid_types = ['click_cta', 'section_view', 'faq_open', 'scroll_depth', 
                      'time_on_section', 'plan_click', 'whatsapp_click', 
                      'contact_click', 'menu_click']
        
        if event_type not in valid_types:
            return JsonResponse({'error': 'Tipo de evento inválido'}, status=400)
        
        # Obter session_id
        session_id = request.session.get('analytics_session', '')
        
        # Obter IP
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0].strip()
        else:
            ip_address = request.META.get('REMOTE_ADDR', '127.0.0.1')
        
        # Criar evento
        UserEvent.objects.create(
            event_type=event_type,
            event_data=event_data,
            page_url=page_url,
            session_id=session_id,
            ip_address=ip_address
        )
        
        return JsonResponse({'success': True})
        
    except Exception as e:
        logger.error(f"Erro ao registrar evento: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
