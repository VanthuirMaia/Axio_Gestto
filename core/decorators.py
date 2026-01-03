"""
Decorators customizados para controle de acesso baseado em planos
"""
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse


def plano_required(feature_name='relatórios avançados', redirect_to='dashboard'):
    """
    Decorator para proteger views que requerem plano Profissional ou superior.

    Verifica se o usuário tem um plano com permite_relatorios_avancados=True.
    Caso contrário, exibe mensagem e redireciona.

    Args:
        feature_name: Nome do recurso bloqueado (para mensagem)
        redirect_to: URL name para redirecionar caso bloqueado

    Uso:
        @login_required
        @plano_required(feature_name='Dashboard Financeiro')
        def dashboard_financeiro(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar se usuário está autenticado
            if not request.user.is_authenticated:
                return redirect('login')

            # Verificar se tem empresa
            if not hasattr(request.user, 'empresa') or not request.user.empresa:
                messages.error(request, 'Você precisa estar vinculado a uma empresa.')
                return redirect('dashboard')

            empresa = request.user.empresa

            # Verificar se tem assinatura ativa
            assinatura = getattr(empresa, 'assinatura_ativa', None)
            if not assinatura:
                messages.error(request, 'Sua empresa não possui uma assinatura ativa.')
                return redirect('dashboard')

            # Verificar se o plano permite relatórios avançados
            plano = assinatura.plano
            if not plano.permite_relatorios_avancados:
                messages.warning(
                    request,
                    f'🔒 {feature_name} está disponível apenas no <strong>Plano Profissional</strong> ou superior. '
                    f'<a href="{reverse("configuracoes_assinatura")}" class="alert-link">Faça upgrade agora</a> '
                    f'para ter acesso completo.',
                    extra_tags='safe'
                )
                return redirect(redirect_to)

            # Plano OK, executar view normalmente
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


def plano_profissional_required(view_func):
    """
    Atalho para @plano_required() com configurações padrão.

    Uso:
        @login_required
        @plano_profissional_required
        def minha_view(request):
            ...
    """
    return plano_required()(view_func)
