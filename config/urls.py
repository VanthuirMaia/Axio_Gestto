from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import login_view, logout_view, dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('agendamentos/', include('agendamentos.urls')),
    path('clientes/', include('clientes.urls')),
    path('', dashboard_view, name='home'),
    path('clientes/', include('clientes.urls')),
    path('financeiro/', include('financeiro.urls')),  # ← ADICIONE ESTA LINHA


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
