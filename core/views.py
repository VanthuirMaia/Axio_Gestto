from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Count, Avg, Q, Max
from datetime import timedelta

from .models import Usuario
from empresas.models import Empresa
from agendamentos.models import Agendamento
from clientes.models import Cliente


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
    
    agora = now()
    hoje = agora.date()
    limite_ativos = agora - timedelta(days=30)

    agendamentos_hoje = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__date=hoje
    ).exclude(
        status__in=["cancelado", "nao_compareceu"]
    ).count()

    proximos_agendamentos = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__gte=agora
    ).exclude(
        status__in=["cancelado", "nao_compareceu"]
    ).select_related('cliente', 'servico').order_by('data_hora_inicio')[:5]

    clientes_metricas = Cliente.objects.filter(
        empresa=empresa,
        ativo=True
    ).annotate(
        total_visitas=Count(
            'agendamentos',
            filter=Q(agendamentos__status="concluido")
        ),
        ultima_visita=Max(
            'agendamentos__data_hora_inicio',
            filter=Q(agendamentos__status="concluido")
        )
    )

    clientes_ativos = clientes_metricas.filter(
        ultima_visita__gte=limite_ativos
    ).count()

    clientes_inativos = clientes_metricas.exclude(
        ultima_visita__gte=limite_ativos
    ).count()

    ticket_medio = Agendamento.objects.filter(
        empresa=empresa,
        status="concluido"
    ).aggregate(
        media=Avg('valor_cobrado')
    )['media'] or 0

    context = {
        'empresa': empresa,
        'agendamentos_hoje': agendamentos_hoje,
        'clientes_ativos': clientes_ativos,
        'clientes_inativos': clientes_inativos,
        'ticket_medio': ticket_medio,
        'proximos_agendamentos': proximos_agendamentos,
    }
    
    return render(request, 'dashboard.html', context)