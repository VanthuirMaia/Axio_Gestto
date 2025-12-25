"""
URLs do app assinaturas
"""
from django.urls import path
from . import views

app_name = 'assinaturas'

urlpatterns = [
    # Criação de tenant (auto-provisionamento)
    path('create-tenant/', views.create_tenant, name='create_tenant'),

    # Webhooks de pagamento
    path('webhooks/stripe/', views.stripe_webhook, name='stripe_webhook'),
    path('webhooks/asaas/', views.asaas_webhook, name='asaas_webhook'),
]
