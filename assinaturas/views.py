"""
Views e endpoints para assinaturas
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.views.decorators.csrf import csrf_exempt
from django.utils.text import slugify
from django.utils.timezone import now, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import secrets
import string
import logging

from empresas.models import Empresa
from core.models import Usuario
from .models import Plano, Assinatura
from .stripe_integration import processar_webhook_stripe, criar_checkout_session
from .asaas_integration import processar_webhook_asaas
from .validators import validar_cpf_cnpj

logger = logging.getLogger(__name__)


@api_view(['POST'])
@permission_classes([AllowAny])
def create_tenant(request):
    """
    Cria empresa + assinatura + usuário admin automaticamente

    Endpoint chamado após checkout ou manualmente

    POST /api/create-tenant/

    Body:
    {
        "company_name": "Salão Bela Vida",
        "email": "contato@belavida.com",
        "telefone": "11999999999",
        "cnpj": "12345678000199",
        "plano": "essencial"  // opcional, padrão: essencial
    }

    Returns:
    {
        "sucesso": true,
        "empresa_id": 1,
        "slug": "salao-bela-vida",
        "login_url": "https://gestto.com.br/onboarding",
        "trial_expira_em": "2026-01-07T...",
        "credenciais": {
            "email": "contato@belavida.com",
            "senha_temporaria": "Abc123..."
        }
    }
    """

    # 1. Normalizar campos (aceitar tanto company_name quanto nome_empresa)
    company_name = request.data.get('company_name') or request.data.get('nome_empresa')
    email = request.data.get('email') or request.data.get('email_admin')
    telefone = request.data.get('telefone')
    cnpj_informado = request.data.get('cnpj', '').strip()

    # 2. Validar dados obrigatórios
    if not company_name or not email or not telefone or not cnpj_informado:
        return Response({
            'sucesso': False,
            'erro': 'Todos os campos são obrigatórios: nome_empresa, email, telefone, CPF/CNPJ'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 3. Validar CPF/CNPJ
    valido, tipo_doc, cnpj, mensagem_erro = validar_cpf_cnpj(cnpj_informado)

    if not valido:
        return Response({
            'sucesso': False,
            'erro': mensagem_erro
        }, status=status.HTTP_400_BAD_REQUEST)

    # 4. Verificar se CPF/CNPJ já está cadastrado
    if Empresa.objects.filter(cnpj=cnpj).exists():
        return Response({
            'sucesso': False,
            'erro': f'{tipo_doc.upper()} já cadastrado. Entre em contato com o suporte.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 5. Gerar slug único
    slug = slugify(company_name)
    base_slug = slug
    counter = 1

    while Empresa.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # 5. Criar Empresa
    try:
        empresa = Empresa.objects.create(
            nome=company_name,
            slug=slug,
            email=email,
            telefone=telefone,
            cnpj=cnpj,
            ativa=True,
            onboarding_completo=False,
            onboarding_etapa=0,
            # Campos opcionais (preencher no onboarding)
            descricao='',
            endereco='',
            cidade='',
            estado='',
            cep='',
            origem_cadastro=request.data.get('origem', 'checkout')
        )

        logger.info(f'Empresa criada: {empresa.nome} (ID: {empresa.id}, Slug: {empresa.slug})')

    except Exception as e:
        logger.error(f'Erro ao criar empresa: {str(e)}')
        return Response({
            'sucesso': False,
            'erro': f'Erro ao criar empresa: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 6. Buscar plano
    plano_nome = request.data.get('plano', 'essencial')
    try:
        plano = Plano.objects.get(nome=plano_nome, ativo=True)
    except Plano.DoesNotExist:
        # Fallback para plano essencial
        plano = Plano.objects.filter(ativo=True).order_by('preco_mensal').first()

        if not plano:
            logger.error('Nenhum plano ativo encontrado!')
            return Response({
                'sucesso': False,
                'erro': 'Nenhum plano disponível no momento'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 7. Criar Assinatura (trial)
    try:
        assinatura = Assinatura.objects.create(
            empresa=empresa,
            plano=plano,
            status='trial',
            data_expiracao=now() + timedelta(days=plano.trial_dias),
            trial_ativo=True,
            gateway=request.data.get('gateway', 'manual')
        )

        logger.info(f'Assinatura criada: Empresa {empresa.nome} - Plano {plano.nome} - Trial {plano.trial_dias} dias')

    except Exception as e:
        logger.error(f'Erro ao criar assinatura: {str(e)}')
        # Rollback: deletar empresa
        empresa.delete()
        return Response({
            'sucesso': False,
            'erro': f'Erro ao criar assinatura: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 8. Criar usuário admin
    try:
        from core.utils import gerar_token_ativacao
        
        activation_token = gerar_token_ativacao()

        usuario = Usuario.objects.create_user(
            username=f"admin_{empresa.id}",
            email=email,
            password=None,  # Senha será definida na ativação
            empresa=empresa,
            is_staff=False,  # Não é staff do Django admin
            ativo=True,
            is_activated=False,  # Conta não ativada ainda
            activation_token=activation_token,
            activation_token_created=now(),
            first_name='Admin',
            last_name=empresa.nome
        )

        logger.info(f'Usuário criado: {usuario.username} para empresa {empresa.nome}')

    except Exception as e:
        logger.error(f'Erro ao criar usuário: {str(e)}')
        # Rollback
        assinatura.delete()
        empresa.delete()
        return Response({
            'sucesso': False,
            'erro': f'Erro ao criar usuário: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # 9. Criar sessão de checkout do Stripe
    checkout_url = None
    gateway = request.data.get('gateway', 'stripe')

    if gateway == 'stripe':
        try:
            checkout_result = criar_checkout_session(empresa, plano)

            if checkout_result.get('sucesso'):
                checkout_url = checkout_result.get('url')
                logger.info(f'Checkout URL criada para empresa {empresa.nome}: {checkout_url}')
            else:
                logger.error(f'Erro ao criar checkout: {checkout_result.get("erro")}')
                # Não fazer rollback - empresa já foi criada
                # Apenas loga o erro e continua

        except Exception as e:
            logger.error(f'Erro ao criar checkout Stripe: {str(e)}')
            # Não fazer rollback - empresa já foi criada

    # 10. Email de boas-vindas com link de ativação
    # Sempre envia email, independente do gateway
    try:
        _enviar_email_boas_vindas(usuario, empresa, activation_token, plano)
    except Exception as e:
        logger.error(f'Erro ao enviar email: {str(e)}')

    # 11. Retornar resposta de sucesso
    response_data = {
        'sucesso': True,
        'empresa_id': empresa.id,
        'slug': empresa.slug,
        'login_url': f'{settings.SITE_URL}/onboarding/' if hasattr(settings, 'SITE_URL') else '/onboarding/',
        'trial_expira_em': assinatura.data_expiracao.isoformat(),
        'trial_dias': plano.trial_dias,
        'plano': plano.get_nome_display(),
        'mensagem': 'Email de ativação enviado! Verifique sua caixa de entrada.'
    }

    # Adicionar checkout_url se houver
    if checkout_url:
        response_data['checkout_url'] = checkout_url

    return Response(response_data, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def stripe_webhook(request):
    """
    Webhook do Stripe

    POST /api/webhooks/stripe/

    Headers:
    - Stripe-Signature: <assinatura>

    Body: evento Stripe (JSON)
    """
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

    if not sig_header:
        logger.error('Webhook Stripe sem header Stripe-Signature')
        return Response({'error': 'Missing signature'}, status=status.HTTP_400_BAD_REQUEST)

    resultado = processar_webhook_stripe(payload, sig_header)

    if 'error' in resultado:
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

    return Response(resultado, status=status.HTTP_200_OK)


@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def asaas_webhook(request):
    """
    Webhook do Asaas

    POST /api/webhooks/asaas/

    Body: evento Asaas (JSON)
    """
    payload = request.data

    if not payload:
        logger.error('Webhook Asaas sem payload')
        return Response({'error': 'Empty payload'}, status=status.HTTP_400_BAD_REQUEST)

    resultado = processar_webhook_asaas(payload)

    if 'error' in resultado:
        return Response(resultado, status=status.HTTP_400_BAD_REQUEST)

    return Response(resultado, status=status.HTTP_200_OK)


# ============================================
# FUNÇÕES AUXILIARES
# ============================================

def _gerar_senha_temporaria(length=12):
    """
    Gera senha aleatória forte

    Returns:
        str: senha com letras maiúsculas, minúsculas, números e símbolos
    """
    chars = string.ascii_letters + string.digits + '!@#$%'
    senha = ''.join(secrets.choice(chars) for _ in range(length))

    # Garantir que tem pelo menos 1 de cada tipo
    if not any(c.isupper() for c in senha):
        senha = senha[:-1] + secrets.choice(string.ascii_uppercase)
    if not any(c.isdigit() for c in senha):
        senha = senha[:-1] + secrets.choice(string.digits)

    return senha


def _enviar_email_boas_vindas(usuario, empresa, activation_token, plano):
    """
    Envia email HTML com link de ativação de conta
    
    Args:
        usuario: Instância de Usuario
        empresa: Instância de Empresa
        activation_token: Token de ativação gerado
        plano: Instância de Plano
    """
    try:
        # Validar configurações de email antes de tentar enviar
        if not hasattr(settings, 'EMAIL_HOST') or not settings.EMAIL_HOST:
            logger.error('EMAIL_HOST não configurado. Não é possível enviar email.')
            raise ValueError('Configuração de email incompleta: EMAIL_HOST não definido')
        
        if not hasattr(settings, 'DEFAULT_FROM_EMAIL') or not settings.DEFAULT_FROM_EMAIL:
            logger.error('DEFAULT_FROM_EMAIL não configurado. Não é possível enviar email.')
            raise ValueError('Configuração de email incompleta: DEFAULT_FROM_EMAIL não definido')
        
        # Log antes de tentar enviar
        logger.info(f'Preparando email de boas-vindas para {usuario.email}')
        logger.info(f'  Empresa: {empresa.nome}')
        logger.info(f'  Plano: {plano.nome}')
        logger.info(f'  Token de ativação: {activation_token[:10]}...')
        
        # Contexto para o template
        context = {
            'usuario': usuario,
            'empresa': empresa,
            'activation_token': activation_token,
            'plano': plano,
            'trial_expira_em': empresa.assinatura.data_expiracao if hasattr(empresa, 'assinatura') else None,
            'site_url': settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000',
        }

        # Renderiza o template HTML
        logger.info('Renderizando template de email...')
        html_message = render_to_string('emails/boas_vindas_com_senha.html', context)
        # Versão texto puro (fallback)
        plain_message = strip_tags(html_message)

        # Configurações do email
        from_email = settings.DEFAULT_FROM_EMAIL
        subject = f'Ative sua conta - {empresa.nome} | Gestto 🎉'
        
        logger.info(f'Enviando email via SMTP...')
        logger.info(f'  De: {from_email}')
        logger.info(f'  Para: {usuario.email}')
        logger.info(f'  Assunto: {subject}')
        logger.info(f'  Host SMTP: {settings.EMAIL_HOST}')
        
        # Envia o email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[usuario.email],
            html_message=html_message,
            fail_silently=False,  # Lança exceção se falhar
        )

        logger.info(f'✓ Email de boas-vindas enviado com sucesso para {usuario.email}')

    except ValueError as e:
        # Erro de configuração
        logger.error(f'Erro de configuração ao enviar email: {str(e)}')
        raise
    except Exception as e:
        # Captura informações detalhadas do erro
        logger.error(f'Erro ao enviar email de boas-vindas para {usuario.email}')
        logger.error(f'  Tipo de erro: {type(e).__name__}')
        logger.error(f'  Mensagem: {str(e)}')
        
        # Log adicional para erros SMTP
        if hasattr(e, 'smtp_code'):
            logger.error(f'  Código SMTP: {e.smtp_code}')
        if hasattr(e, 'smtp_error'):
            logger.error(f'  Erro SMTP: {e.smtp_error}')
        
        # Re-lança a exceção para que o chamador saiba que falhou
        raise
