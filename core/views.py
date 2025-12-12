from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from .models import Usuario
from empresas.models import Empresa

@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        email_ou_usuario = request.POST.get('email_ou_usuario')
        senha = request.POST.get('senha')
        
        try:
            usuario = Usuario.objects.get(email=email_ou_usuario)
            user = authenticate(request, username=usuario.username, password=senha)
        except Usuario.DoesNotExist:
            user = authenticate(request, username=email_ou_usuario, password=senha)
        
        if user is not None and user.ativo:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Email/Usuario ou senha incorretos.')
    
    return render(request, 'login.html')

@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('login')

@login_required
def dashboard_view(request):
    empresa = request.user.empresa
    if not empresa:
        messages.error(request, 'Usuario nao associado a nenhuma empresa.')
        return redirect('logout')
    
    context = {
        'empresa': empresa,
        'total_agendamentos': empresa.agendamentos.count(),
        'total_clientes': empresa.clientes.count(),
        'total_servicos': empresa.servicos.count(),
    }
    return render(request, 'dashboard.html', context)
