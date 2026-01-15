from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from whatsapp import views as whatsapp_views
from core.views import (
    login_view, logout_view, dashboard_view,
    password_reset_request, password_reset_sent,
    password_reset_confirm, password_reset_complete,
    service_worker, offline_view, ativar_conta
)
from core.health import health_check
from agendamentos.bot_api import processar_comando_bot, whatsapp_webhook_saas, consultar_informacoes_empresa
from agendamentos.api_n8n import (
    listar_servicos,
    listar_profissionais,
    consultar_horarios_funcionamento,
    consultar_datas_especiais,
    consultar_horarios_disponiveis,
    buscar_empresa_por_instancia
)
from empresas.api_views import whatsapp_webhook
from configuracoes.views import whatsapp_webhook_n8n
from agendamentos.public_views import (
    agendamento_publico,
    api_profissionais_por_servico,
    api_horarios_disponiveis,
    confirmar_agendamento
)

from django.http import JsonResponse, FileResponse
from django.shortcuts import render
import os

def manifest_view(request):
    """Serve manifest.json com Content-Type correto"""
    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')
    response = FileResponse(open(manifest_path, 'rb'), content_type='application/manifest+json')
    response['Cache-Control'] = 'no-cache'
    return response

def pwa_test_view(request):
    """Página de teste PWA"""
    return render(request, 'pwa_test.html')

urlpatterns = [
    # ==========================================
    # PWA - Service Worker e Manifest
    # ==========================================
    path('manifest.json', manifest_view, name='manifest'),
    path('service-worker.js', service_worker, name='service_worker'),
    path('offline/', offline_view, name='offline'),
    path('pwa-test/', pwa_test_view, name='pwa_test'),

    # ==========================================
    # PÚBLICO - Landing Page
    # ==========================================
    path('', include('landing.urls')),  # Landing na raiz

    # ==========================================
    # PÚBLICO - Agendamento Online
    # ==========================================
    path('agendar/<slug:slug>/', agendamento_publico, name='agendamento_publico'),
    path('agendar/<slug:slug>/api/profissionais/', api_profissionais_por_servico, name='api_profissionais_servico'),
    path('agendar/<slug:slug>/api/horarios-disponiveis/', api_horarios_disponiveis, name='api_horarios_disponiveis_public'),
    path('agendar/<slug:slug>/confirmar/', confirmar_agendamento, name='confirmar_agendamento_publico'),

    # ==========================================
    # PÚBLICO - APIs (webhooks, create-tenant)
    # ==========================================
    path('health/', health_check, name='health_check'),
    path('api/', include('assinaturas.urls')),  # create-tenant, webhooks
    path('api/whatsapp-webhook/', whatsapp_webhook_saas, name='whatsapp_webhook_saas'),
    path('api/bot/processar/', processar_comando_bot, name='api_bot_processar'),

    # Evolution API - Webhook WhatsApp (antigo - direto do bot_api.py)
    path('api/webhooks/whatsapp/<int:empresa_id>/<str:secret>/', whatsapp_webhook, name='whatsapp_webhook_evolution'),

    # Evolution API → Django → n8n (NOVO - webhook intermediário)
    path('api/webhooks/whatsapp-n8n/<int:empresa_id>/<str:secret>/', whatsapp_webhook_n8n, name='whatsapp_webhook_n8n'),

    # Novo webhook global — todas as instâncias do WhatsApp passam por aqui
    path('api/webhooks/teste/', lambda request: JsonResponse({'ok': True}), name='teste_whatsapp'),
    path('api/webhooks/whatsapp/', include('whatsapp.urls')),

    # APIs n8n - Consultas
    path('api/bot/empresa/info/', consultar_informacoes_empresa, name='api_bot_info_empresa'),
    path('api/n8n/servicos/', listar_servicos, name='api_n8n_servicos'),
    path('api/n8n/profissionais/', listar_profissionais, name='api_n8n_profissionais'),
    path('api/n8n/horarios-funcionamento/', consultar_horarios_funcionamento, name='api_n8n_horarios_funcionamento'),
    path('api/n8n/datas-especiais/', consultar_datas_especiais, name='api_n8n_datas_especiais'),
    path('api/n8n/horarios-disponiveis/', consultar_horarios_disponiveis, name='api_n8n_horarios_disponiveis'),

    # API n8n - Buscar empresa por instance_name (usado para identificar empresa no webhook)
    path('api/n8n/empresa-por-instancia/<str:instance_name>/', buscar_empresa_por_instancia, name='api_n8n_empresa_por_instancia'),
    path('api/n8n/empresa-por-instancia/', buscar_empresa_por_instancia, name='api_n8n_empresa_por_instancia_post'),

    # ==========================================
    # PRIVADO - Sistema (só clientes autenticados)
    # ==========================================
    # Admin (protegido por login do Django)
    path('app/admin/', admin.site.urls),

    # Login/Logout
    path('app/login/', login_view, name='login'),
    path('app/logout/', logout_view, name='logout'),

    # Password Reset
    path('app/password-reset/', password_reset_request, name='password_reset_request'),
    path('app/password-reset/sent/', password_reset_sent, name='password_reset_sent'),
    path('app/password-reset/confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('app/password-reset/complete/', password_reset_complete, name='password_reset_complete'),

    # Account Activation
    path('ativar-conta/<str:token>/', ativar_conta, name='ativar_conta'),

    # Onboarding wizard
    path('app/', include('core.onboarding_urls')),

    # Sistema principal
    path('app/dashboard/', dashboard_view, name='dashboard'),
    path('app/agendamentos/', include('agendamentos.urls')),
    path('app/clientes/', include('clientes.urls')),
    path('app/financeiro/', include('financeiro.urls')),
    path('app/configuracoes/', include('configuracoes.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
