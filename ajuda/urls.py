from django.urls import path
from . import views

urlpatterns = [
    path('', views.ajuda_home, name='ajuda_home'),
    path('categoria/<slug:slug>/', views.ajuda_categoria, name='ajuda_categoria'),
    path('artigo/<slug:slug>/', views.ajuda_artigo, name='ajuda_artigo'),
]
