from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import (
    login_view, logout_view, dashboard_view,
    password_reset_request, password_reset_sent,
    password_reset_confirm, password_reset_complete
)
from core.health import health_check
from agendamentos.bot_api import processar_comando_bot, whatsapp_webhook_saas
from agendamentos.api_n8n import (
    listar_servicos,
    listar_profissionais,
    consultar_horarios_funcionamento,
    consultar_datas_especiais,
    consultar_horarios_disponiveis
)

urlpatterns = [
    # Health Check (sem autenticação para Docker)
    path('health/', health_check, name='health_check'),

    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    # Password Reset URLs
    path('password-reset/', password_reset_request, name='password_reset_request'),
    path('password-reset/sent/', password_reset_sent, name='password_reset_sent'),
    path('password-reset/confirm/<uidb64>/<token>/', password_reset_confirm, name='password_reset_confirm'),
    path('password-reset/complete/', password_reset_complete, name='password_reset_complete'),

    # API Bot WhatsApp (n8n)
    path('api/bot/processar/', processar_comando_bot, name='api_bot_processar'),

    # WEBHOOK MULTI-TENANT SAAS (sem autenticação - auto-detect tenant)
    path('api/whatsapp-webhook/', whatsapp_webhook_saas, name='whatsapp_webhook_saas'),

    # APIs n8n - Consultas (substituem Google Sheets)
    path('api/n8n/servicos/', listar_servicos, name='api_n8n_servicos'),
    path('api/n8n/profissionais/', listar_profissionais, name='api_n8n_profissionais'),
    path('api/n8n/horarios-funcionamento/', consultar_horarios_funcionamento, name='api_n8n_horarios_funcionamento'),
    path('api/n8n/datas-especiais/', consultar_datas_especiais, name='api_n8n_datas_especiais'),
    path('api/n8n/horarios-disponiveis/', consultar_horarios_disponiveis, name='api_n8n_horarios_disponiveis'),

    # APIs SaaS - Assinaturas e Pagamentos
    path('api/', include('assinaturas.urls')),

    # Onboarding wizard
    path('', include('core.onboarding_urls')),

    path('dashboard/', dashboard_view, name='dashboard'),
    path('agendamentos/', include('agendamentos.urls')),
    path('clientes/', include('clientes.urls')),
    path('', dashboard_view, name='home'),
    path('clientes/', include('clientes.urls')),
    path('financeiro/', include('financeiro.urls')),
    path('configuracoes/', include('configuracoes.urls')),



]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
