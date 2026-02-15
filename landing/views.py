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
    """Formulário de cadastro na lista de espera"""
    if request.method == 'POST':
        from .models import Waitlist
        from django.db import IntegrityError
        
        # Extrair dados do formulário
        nome = request.POST.get('nome', '').strip()
        email = request.POST.get('email', '').strip().lower()
        whatsapp = request.POST.get('whatsapp', '').strip()
        nome_negocio = request.POST.get('nome_negocio', '').strip()
        cidade = request.POST.get('cidade', '').strip()

        # Log de tentativa de cadastro na waitlist
        logger.info(f"Tentativa de cadastro na waitlist - IP: {request.META.get('REMOTE_ADDR')}, Email: {email}, Nome: {nome}")

        # Validações básicas
        if not nome or not email or not whatsapp or not nome_negocio:
            messages.error(request, 'Por favor, preencha todos os campos obrigatórios.')
            logger.warning(f"Cadastro waitlist incompleto - IP: {request.META.get('REMOTE_ADDR')}")
            return redirect('landing:cadastro')

        # Tentar salvar na waitlist
        try:
            waitlist_entry = Waitlist.objects.create(
                nome=nome,
                email=email,
                whatsapp=whatsapp,
                nome_negocio=nome_negocio,
                cidade=cidade
            )
            
            logger.info(f"Cadastro na waitlist bem-sucedido - Email: {email}, Nome: {nome}")
            
            # Redirecionar para página de sucesso
            return redirect('landing:waitlist_sucesso')
            
        except IntegrityError:
            # Email já existe na waitlist
            messages.error(request, 'Este email já está na lista de espera.')
            logger.warning(f"Email duplicado na waitlist - Email: {email}")
            return redirect('landing:cadastro')
            
        except Exception as e:
            logger.error(f"Erro ao cadastrar na waitlist - Email: {email}, Erro: {str(e)}")
            messages.error(request, 'Erro ao processar seu cadastro. Por favor, tente novamente.')
            return redirect('landing:cadastro')

    # GET - Mostrar formulário de waitlist
    context = {
        'site_name': 'Gestto',
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


def waitlist_sucesso(request):
    """Página de sucesso após cadastro na waitlist"""
    context = {
        'site_name': 'Gestto',
    }
    return render(request, 'landing/waitlist_sucesso.html', context)


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
