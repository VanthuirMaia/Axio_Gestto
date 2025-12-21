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
from agendamentos.bot_api import processar_comando_bot

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
