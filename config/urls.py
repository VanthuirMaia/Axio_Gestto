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
    # ==========================================
    # PÚBLICO - Landing Page
    # ==========================================
    path('', include('landing.urls')),  # Landing na raiz

    # ==========================================
    # PÚBLICO - APIs (webhooks, create-tenant)
    # ==========================================
    path('health/', health_check, name='health_check'),
    path('api/', include('assinaturas.urls')),  # create-tenant, webhooks
    path('api/whatsapp-webhook/', whatsapp_webhook_saas, name='whatsapp_webhook_saas'),
    path('api/bot/processar/', processar_comando_bot, name='api_bot_processar'),

    # APIs n8n - Consultas
    path('api/n8n/servicos/', listar_servicos, name='api_n8n_servicos'),
    path('api/n8n/profissionais/', listar_profissionais, name='api_n8n_profissionais'),
    path('api/n8n/horarios-funcionamento/', consultar_horarios_funcionamento, name='api_n8n_horarios_funcionamento'),
    path('api/n8n/datas-especiais/', consultar_datas_especiais, name='api_n8n_datas_especiais'),
    path('api/n8n/horarios-disponiveis/', consultar_horarios_disponiveis, name='api_n8n_horarios_disponiveis'),

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
