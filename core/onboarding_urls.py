"""
URLs do wizard de onboarding
"""
from django.urls import path
from . import onboarding_views

urlpatterns = [
    path('onboarding/', onboarding_views.onboarding_wizard, name='onboarding'),
    path('onboarding/1/', onboarding_views.onboarding_step_1_servicos, name='onboarding_step_1'),
    path('onboarding/2/', onboarding_views.onboarding_step_2_profissional, name='onboarding_step_2'),
    path('onboarding/3/', onboarding_views.onboarding_step_3_whatsapp, name='onboarding_step_3'),
    path('onboarding/4/', onboarding_views.onboarding_step_4_pronto, name='onboarding_step_4'),
]
