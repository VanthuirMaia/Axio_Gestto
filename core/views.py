from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, password_validation
from django.contrib.auth.decorators import login_required
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.timezone import now
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.db.models import Count, Avg, Q, Max, Sum
from django.core.mail import send_mail
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.conf import settings
from datetime import timedelta
from django.utils.timezone import now, localtime
from axes.helpers import get_client_ip_address, get_client_cache_keys
from axes.models import AccessAttempt
from .models import Usuario
from empresas.models import Empresa
from agendamentos.models import Agendamento
from clientes.models import Cliente
from financeiro.models import LancamentoFinanceiro


@require_http_methods(["GET", "POST"])
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        email_ou_usuario = request.POST.get('email_ou_usuario')
        senha = request.POST.get('senha')

        # Verificar se o IP/usuário está bloqueado pelo django-axes
        ip_address = get_client_ip_address(request)
        cache_keys = get_client_cache_keys(request, credentials={'username': email_ou_usuario})

        # Buscar tentativas de acesso bloqueadas
        attempts = AccessAttempt.objects.filter(
            ip_address=ip_address
        ).filter(
            failures_since_start__gte=settings.AXES_FAILURE_LIMIT
        )

        if attempts.exists():
            messages.error(
                request,
                f'Muitas tentativas de login falhas. Sua conta foi temporariamente bloqueada. '
                f'Aguarde alguns minutos ou entre em contato com o suporte.'
            )
            return render(request, 'login.html')

        # Tentar autenticar
        try:
            usuario = Usuario.objects.get(email=email_ou_usuario)
            user = authenticate(request, username=usuario.username, password=senha)
        except Usuario.DoesNotExist:
            user = authenticate(request, username=email_ou_usuario, password=senha)

        if user is not None:
            if not user.ativo:
                messages.error(request, 'Sua conta está inativa. Entre em contato com o suporte.')
                return render(request, 'login.html')

            login(request, user)

            # Redirecionar para onboarding se não completado
            if hasattr(user, 'empresa') and user.empresa:
                if not user.empresa.onboarding_completo:
                    return redirect('onboarding')

            return redirect('dashboard')
        else:
            # Verificar se o usuário existe mas a senha está incorreta
            try:
                usuario_existe = Usuario.objects.get(email=email_ou_usuario)
                messages.error(request, 'Senha incorreta. Tente novamente.')
            except Usuario.DoesNotExist:
                # Verificar se existe pelo username
                try:
                    usuario_existe = Usuario.objects.get(username=email_ou_usuario)
                    messages.error(request, 'Senha incorreta. Tente novamente.')
                except Usuario.DoesNotExist:
                    messages.error(request, 'Email/Usuário não encontrado. Verifique seus dados ou cadastre-se.')

    return render(request, 'login.html')


@login_required
def logout_view(request):
    logout(request)
    messages.success(request, 'Você foi desconectado com sucesso.')
    return redirect('login')


@login_required
def dashboard_view(request):
    """Dashboard principal - Command Center do negócio"""
    empresa = request.user.empresa
    if not empresa:
        messages.error(request, 'Usuário não associado a nenhuma empresa.')
        return redirect('logout')

    # Redirecionar para onboarding se não completado
    if not empresa.onboarding_completo:
        return redirect('onboarding')
    
    agora = now()
    agora_local = localtime(agora)  # Converte para timezone local (America/Recife)
    hoje = agora_local.date()  # Data local, não UTC
    inicio_mes = hoje.replace(day=1)
    inicio_semana = hoje - timedelta(days=hoje.weekday())
    limite_ativos = agora - timedelta(days=30)

    # ============================================
    # SAUDAÇÃO PERSONALIZADA
    # ============================================
    # agora_local já foi definido acima
    hora = agora_local.hour

    if hora < 12:
        saudacao = "Bom dia"
    elif hora < 18:
        saudacao = "Boa tarde"
    else:
        saudacao = "Boa noite"

    # ============================================
    # AGENDAMENTOS (MANTIDO + MELHORADO)
    # ============================================
    
    # Agendamentos hoje (contagem)
    agendamentos_hoje = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__date=hoje
    ).exclude(
        status__in=["cancelado", "nao_compareceu"]
    ).count()

    # Agendamentos hoje (lista completa para mostrar no dashboard)
    agendamentos_hoje_lista = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__date=hoje
    ).exclude(
        status__in=["cancelado", "nao_compareceu"]
    ).select_related('cliente', 'servico', 'profissional').order_by('data_hora_inicio')

    # Próximos agendamentos (futuros, para outra seção se necessário)
    proximos_agendamentos = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__gte=agora
    ).exclude(
        status__in=["cancelado", "nao_compareceu"]
    ).select_related('cliente', 'servico', 'profissional').order_by('data_hora_inicio')[:5]
    
    # Agendamentos da semana (NOVO)
    agendamentos_semana = Agendamento.objects.filter(
        empresa=empresa,
        data_hora_inicio__gte=inicio_semana,
        data_hora_inicio__lt=inicio_semana + timedelta(days=7)
    ).exclude(status='cancelado').count()
    
    # Agendamentos pendentes de confirmação (NOVO)
    agendamentos_pendentes = Agendamento.objects.filter(
        empresa=empresa,
        status='pendente',
        data_hora_inicio__gte=agora
    ).count()

    # ============================================
    # CLIENTES (MANTIDO + MELHORADO)
    # ============================================
    
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
        ),
        total_gasto=Sum(
            'agendamentos__valor_cobrado',
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
    
    # Total de clientes (NOVO)
    total_clientes = Cliente.objects.filter(empresa=empresa, ativo=True).count()
    
    # Novos clientes este mês (NOVO)
    novos_clientes_mes = Cliente.objects.filter(
        empresa=empresa,
        criado_em__gte=inicio_mes
    ).count()
    
    # Top 5 Clientes VIP (NOVO)
    top_clientes = clientes_metricas.filter(
        total_gasto__isnull=False
    ).order_by('-total_gasto')[:5]
    
    # Clientes em risco (NOVO)
    clientes_risco = clientes_metricas.filter(
        ultima_visita__lt=hoje - timedelta(days=30)
    ).count()

    # ============================================
    # FINANCEIRO (NOVO)
    # ============================================
    
    # Faturamento do mês
    faturamento_mes = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo='receita',
        status='pago',
        data_pagamento__gte=inicio_mes,
        data_pagamento__lte=hoje
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Receitas pendentes do mês
    receitas_pendentes = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo='receita',
        status='pendente',
        data_vencimento__month=hoje.month,
        data_vencimento__year=hoje.year
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Despesas do mês
    despesas_mes = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        tipo='despesa',
        status='pago',
        data_pagamento__gte=inicio_mes,
        data_pagamento__lte=hoje
    ).aggregate(total=Sum('valor'))['total'] or 0
    
    # Saldo do mês
    saldo_mes = faturamento_mes - despesas_mes
    
    # Contas vencidas
    contas_vencidas = LancamentoFinanceiro.objects.filter(
        empresa=empresa,
        status='pendente',
        data_vencimento__lt=hoje
    ).count()
    
    # ============================================
    # GRÁFICO: Faturamento últimos 7 dias (NOVO)
    # ============================================
    
    dias_labels = []
    dias_valores = []
    
    for i in range(6, -1, -1):
        dia = hoje - timedelta(days=i)
        
        faturamento_dia = LancamentoFinanceiro.objects.filter(
            empresa=empresa,
            tipo='receita',
            status='pago',
            data_pagamento=dia
        ).aggregate(total=Sum('valor'))['total'] or 0
        
        # Dia da semana em português
        dias_semana = ['Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb', 'Dom']
        dia_nome = dias_semana[dia.weekday()]
        
        dias_labels.append(f"{dia_nome} {dia.day}")
        dias_valores.append(float(faturamento_dia))

    # ============================================
    # ONBOARDING (NOVO)
    # ============================================
    from .onboarding import calcular_progresso_onboarding
    
    onboarding = calcular_progresso_onboarding(empresa)
    
    # ============================================
    # CONTEXTO
    # ============================================
    
    context = {
        'empresa': empresa,
        'usuario': request.user,
        'saudacao': saudacao,
        'hoje': hoje,
        'agora': agora,
        
        # Onboarding
        'onboarding': onboarding,

        # Agendamentos
        'agendamentos_hoje': agendamentos_hoje,
        'agendamentos_hoje_lista': agendamentos_hoje_lista,
        'agendamentos_semana': agendamentos_semana,
        'agendamentos_pendentes': agendamentos_pendentes,
        'proximos_agendamentos': proximos_agendamentos,

        # Clientes
        'total_clientes': total_clientes,
        'clientes_ativos': clientes_ativos,
        'clientes_inativos': clientes_inativos,
        'novos_clientes_mes': novos_clientes_mes,
        'ticket_medio': ticket_medio,
        'top_clientes': top_clientes,
        'clientes_risco': clientes_risco,

        # Financeiro
        'faturamento_mes': faturamento_mes,
        'receitas_pendentes': receitas_pendentes,
        'despesas_mes': despesas_mes,
        'saldo_mes': saldo_mes,
        'contas_vencidas': contas_vencidas,

        # Gráfico
        'dias_labels': dias_labels,
        'dias_valores': dias_valores,
    }

    return render(request, 'dashboard.html', context)


# ============================================
# PASSWORD RESET VIEWS
# ============================================

@require_http_methods(["GET", "POST"])
def password_reset_request(request):
    """Formulário para solicitar recuperação de senha"""
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            usuario = Usuario.objects.get(email=email, ativo=True)

            # Gerar token
            token = default_token_generator.make_token(usuario)
            uid = urlsafe_base64_encode(force_bytes(usuario.pk))

            # Preparar email
            current_site = get_current_site(request)
            context = {
                'usuario': usuario,
                'domain': current_site.domain,
                'uid': uid,
                'token': token,
                'protocol': 'https' if request.is_secure() else 'http',
            }

            # Enviar email (HTML + texto)
            subject = 'Recuperação de Senha - Axio Gestto'
            html_message = render_to_string('emails/password_reset_email.html', context)
            plain_message = render_to_string('emails/password_reset_email.txt', context)

            send_mail(
                subject,
                plain_message,
                settings.DEFAULT_FROM_EMAIL,
                [usuario.email],
                html_message=html_message,
                fail_silently=False,
            )

            messages.success(request, 'Instruções de recuperação foram enviadas para seu email.')
            return redirect('password_reset_sent')

        except Usuario.DoesNotExist:
            # Não revelar se email existe ou não (segurança)
            messages.success(request, 'Se o email existir, você receberá instruções de recuperação.')
            return redirect('password_reset_sent')

    return render(request, 'password_reset_request.html')


@require_http_methods(["GET"])
def password_reset_sent(request):
    """Página confirmando que email foi enviado"""
    return render(request, 'password_reset_sent.html')


@require_http_methods(["GET", "POST"])
def password_reset_confirm(request, uidb64, token):
    """Formulário para definir nova senha (via link do email)"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        usuario = Usuario.objects.get(pk=uid, ativo=True)
    except (TypeError, ValueError, OverflowError, Usuario.DoesNotExist):
        usuario = None

    if usuario is not None and default_token_generator.check_token(usuario, token):
        if request.method == 'POST':
            nova_senha = request.POST.get('nova_senha')
            confirmar_senha = request.POST.get('confirmar_senha')

            if nova_senha != confirmar_senha:
                messages.error(request, 'As senhas não coincidem.')
                return render(request, 'password_reset_confirm.html', {'validlink': True})

            # Validar senha usando validators do Django
            try:
                password_validation.validate_password(nova_senha, usuario)
            except ValidationError as e:
                for error in e.messages:
                    messages.error(request, error)
                return render(request, 'password_reset_confirm.html', {'validlink': True})

            # Definir nova senha
            usuario.set_password(nova_senha)
            usuario.save()

            messages.success(request, 'Senha alterada com sucesso! Você já pode fazer login.')
            return redirect('password_reset_complete')

        return render(request, 'password_reset_confirm.html', {'validlink': True})
    else:
        # Token inválido ou expirado
        return render(request, 'password_reset_confirm.html', {'validlink': False})


@require_http_methods(["GET"])
def password_reset_complete(request):
    """Pagina final confirmando sucesso"""
    return render(request, 'password_reset_complete.html')


# ==========================================
# ALTERAR SENHA (USUARIO LOGADO)
# ==========================================

@login_required
@require_http_methods(["GET", "POST"])
def alterar_senha(request):
    """
    Permite que o usuario logado altere sua propria senha.
    Requer a senha atual para confirmacao.
    """
    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        nova_senha = request.POST.get('nova_senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        usuario = request.user

        # Verificar senha atual
        if not usuario.check_password(senha_atual):
            messages.error(request, 'Senha atual incorreta.')
            return render(request, 'alterar_senha.html')

        # Verificar se as novas senhas coincidem
        if nova_senha != confirmar_senha:
            messages.error(request, 'As novas senhas nao coincidem.')
            return render(request, 'alterar_senha.html')

        # Validar a nova senha
        try:
            password_validation.validate_password(nova_senha, usuario)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'alterar_senha.html')

        # Verificar se a nova senha e diferente da atual
        if usuario.check_password(nova_senha):
            messages.error(request, 'A nova senha deve ser diferente da senha atual.')
            return render(request, 'alterar_senha.html')

        # Alterar senha
        usuario.set_password(nova_senha)
        usuario.save()

        # Reautenticar o usuario para nao deslogar
        from django.contrib.auth import update_session_auth_hash
        update_session_auth_hash(request, usuario)

        messages.success(request, 'Senha alterada com sucesso!')
        return redirect('configuracoes_dashboard')

    return render(request, 'alterar_senha.html')


# ==========================================
# ATIVAÇÃO DE CONTA VIA EMAIL
# ==========================================

@require_http_methods(["GET", "POST"])
def ativar_conta(request, token):
    """
    Ativa conta de usuário via link de email
    
    GET: Mostra formulário para definir senha
    POST: Ativa conta e define senha
    """
    from .utils import token_ativacao_valido
    
    # Fazer logout se houver sessão ativa para evitar conflitos
    # (ex: admin logado clicando no link de ativação de outro usuário)
    if request.user.is_authenticated:
        logout(request)
    
    # Buscar usuário pelo token
    try:
        usuario = Usuario.objects.get(activation_token=token, is_activated=False)
    except Usuario.DoesNotExist:
        messages.error(request, 'Link de ativação inválido ou já utilizado.')
        return render(request, 'ativar_conta.html', {'token_valido': False})
    
    # Verificar se token ainda é válido (48h)
    if not token_ativacao_valido(usuario):
        messages.error(request, 'Este link de ativação expirou. Entre em contato com o suporte.')
        return render(request, 'ativar_conta.html', {'token_valido': False})
    
    if request.method == 'POST':
        password = request.POST.get('password')
        password_confirm = request.POST.get('password_confirm')
        
        # Validar senhas
        if password != password_confirm:
            messages.error(request, 'As senhas não coincidem.')
            return render(request, 'ativar_conta.html', {'token_valido': True})
        
        # Validar força da senha
        try:
            password_validation.validate_password(password, usuario)
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'ativar_conta.html', {'token_valido': True})
        
        # Ativar conta e definir senha
        usuario.set_password(password)
        usuario.is_activated = True
        usuario.activation_token = None  # Invalidar token
        usuario.activation_token_created = None
        usuario.save()
        
        messages.success(request, 'Conta ativada com sucesso! Você já pode fazer login.')
        return redirect('login')
    
    # GET: Mostrar formulário
    return render(request, 'ativar_conta.html', {'token_valido': True})


# ==========================================
# PWA - Service Worker e Offline
# ==========================================

from django.http import HttpResponse
from django.views.decorators.cache import cache_control
from django.views.decorators.http import require_GET
import os


@require_GET
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def service_worker(request):
    """Serve o service worker com headers corretos"""
    sw_path = os.path.join(settings.BASE_DIR, 'static', 'service-worker.js')

    try:
        with open(sw_path, 'r', encoding='utf-8') as f:
            content = f.read()

        return HttpResponse(
            content,
            content_type='application/javascript; charset=utf-8',
            headers={
                'Service-Worker-Allowed': '/',
                'Cache-Control': 'no-cache, no-store, must-revalidate',
            }
        )
    except FileNotFoundError:
        return HttpResponse(
            '// Service worker file not found',
            content_type='application/javascript',
            status=404
        )


@require_GET
def offline_view(request):
    """Página exibida quando o usuário está offline"""
    return render(request, 'offline.html')


@require_GET
@cache_control(max_age=0, no_cache=True, no_store=True, must_revalidate=True)
def manifest_json(request):
    """Serve o manifest.json com headers corretos"""
    import json

    manifest_path = os.path.join(settings.BASE_DIR, 'static', 'manifest.json')

    try:
        with open(manifest_path, 'r', encoding='utf-8') as f:
            manifest_data = json.load(f)

        return HttpResponse(
            json.dumps(manifest_data, indent=2),
            content_type='application/manifest+json',
            headers={
                'Cache-Control': 'no-cache, no-store, must-revalidate',
            }
        )
    except FileNotFoundError:
        return HttpResponse(
            json.dumps({"name": "Gestto", "short_name": "Gestto"}),
            content_type='application/manifest+json',
            status=404
        )


@login_required
def upgrade_required(request):
    """
    Página de upgrade mostrada quando usuário tenta acessar feature bloqueada
    """
    feature_name = request.GET.get('feature', 'Este recurso')
    plano_atual = request.GET.get('plano_atual', 'basico')
    
    # Mapear nomes de planos
    planos_display = {
        'basico': 'Básico',
        'essencial': 'Essencial',
        'profissional': 'Profissional'
    }
    
    # Preços dos planos
    precos = {
        'basico': '19,99',
        'essencial': '79,99',
        'profissional': '199,99'
    }
    
    context = {
        'feature_name': feature_name,
        'plano_atual': plano_atual,
        'plano_atual_display': planos_display.get(plano_atual, plano_atual.title()),
        'preco_atual': precos.get(plano_atual, '0,00')
    }
    
    return render(request, 'core/upgrade_required.html', context)