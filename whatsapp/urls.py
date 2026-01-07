from django.urls import path
from . import views

urlpatterns = [
    path('', views.webhook_whatsapp_global, name='webhook_whatsapp_global'),
]
