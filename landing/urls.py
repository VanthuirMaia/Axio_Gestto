from django.urls import path
from . import views

app_name = 'landing'

urlpatterns = [
    path('', views.home, name='home'),
    path('precos/', views.precos, name='precos'),
    path('cadastro/', views.cadastro, name='cadastro'),
    path('waitlist/sucesso/', views.waitlist_sucesso, name='waitlist_sucesso'),
    path('sobre/', views.sobre, name='sobre'),
    path('contato/', views.contato, name='contato'),
    path('termos/', views.termos_uso, name='termos_uso'),
    path('politica-cancelamento/', views.politica_cancelamento, name='politica_cancelamento'),
    path('assinatura/sucesso/', views.checkout_sucesso, name='checkout_sucesso'),
    path('assinatura/cancelado/', views.checkout_cancelado, name='checkout_cancelado'),
    
    # Analytics API
    path('api/track-event/', views.track_event, name='track_event'),
]
