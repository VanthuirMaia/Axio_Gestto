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
from django.conf import settings
import secrets
import string
import logging

from empresas.models import Empresa
from core.models import Usuario
from .models import Plano, Assinatura
from .stripe_integration import processar_webhook_stripe
from .asaas_integration import processar_webhook_asaas

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

    # 1. Validar dados obrigatórios
    required_fields = ['company_name', 'email', 'telefone', 'cnpj']
    for field in required_fields:
        if not request.data.get(field):
            return Response({
                'sucesso': False,
                'erro': f'Campo obrigatório: {field}'
            }, status=status.HTTP_400_BAD_REQUEST)

    # 2. Validar CNPJ único
    cnpj = request.data['cnpj'].replace('.', '').replace('/', '').replace('-', '')
    if Empresa.objects.filter(cnpj=cnpj).exists():
        return Response({
            'sucesso': False,
            'erro': 'CNPJ já cadastrado. Entre em contato com o suporte.'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 3. Gerar slug único
    slug = slugify(request.data['company_name'])
    base_slug = slug
    counter = 1

    while Empresa.objects.filter(slug=slug).exists():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # 4. Criar Empresa
    try:
        empresa = Empresa.objects.create(
            nome=request.data['company_name'],
            slug=slug,
            email=request.data['email'],
            telefone=request.data['telefone'],
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

    # 5. Buscar plano
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

    # 6. Criar Assinatura (trial)
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

    # 7. Criar usuário admin
    try:
        senha_temporaria = _gerar_senha_temporaria()

        usuario = Usuario.objects.create_user(
            username=f"admin_{empresa.id}",
            email=request.data['email'],
            password=senha_temporaria,
            empresa=empresa,
            is_staff=False,  # Não é staff do Django admin
            ativo=True,
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

    # 8. Enviar email de boas-vindas
    try:
        _enviar_email_boas_vindas(usuario, empresa, senha_temporaria, plano)
    except Exception as e:
        logger.error(f'Erro ao enviar email: {str(e)}')
        # Não fazer rollback por causa de email (tenant já foi criado)

    # 9. Retornar resposta de sucesso
    return Response({
        'sucesso': True,
        'empresa_id': empresa.id,
        'slug': empresa.slug,
        'login_url': f'{settings.SITE_URL}/onboarding/' if hasattr(settings, 'SITE_URL') else '/onboarding/',
        'trial_expira_em': assinatura.data_expiracao.isoformat(),
        'trial_dias': plano.trial_dias,
        'plano': plano.get_nome_display(),
        'credenciais': {
            'email': request.data['email'],
            'senha_temporaria': senha_temporaria if settings.DEBUG else '***ENVIADA_POR_EMAIL***'
        }
    }, status=status.HTTP_201_CREATED)


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


def _enviar_email_boas_vindas(usuario, empresa, senha, plano):
    """
    Envia email com credenciais de acesso ao novo tenant

    Args:
        usuario: Instância de Usuario
        empresa: Instância de Empresa
        senha: Senha temporária gerada
        plano: Instância de Plano
    """
    assunto = f'Bem-vindo ao Gestto - {empresa.nome}! 🎉'

    mensagem = f"""
Olá, {empresa.nome}!

Sua conta no Gestto foi criada com sucesso! 🎉

╔══════════════════════════════════════════╗
║        INFORMAÇÕES DA SUA CONTA          ║
╚══════════════════════════════════════════╝

Empresa: {empresa.nome}
Plano: {plano.get_nome_display()}
Trial: {plano.trial_dias} dias grátis (até {empresa.assinatura.data_expiracao.strftime('%d/%m/%Y')})

╔══════════════════════════════════════════╗
║           ACESSE AGORA MESMO             ║
╚══════════════════════════════════════════╝

URL: {settings.SITE_URL if hasattr(settings, 'SITE_URL') else 'http://localhost:8000'}/onboarding/

📧 Email: {usuario.email}
🔑 Senha temporária: {senha}

⚠️ IMPORTANTE: Altere sua senha no primeiro acesso!

╔══════════════════════════════════════════╗
║         PRÓXIMOS PASSOS (5 MIN)          ║
╚══════════════════════════════════════════╝

1️⃣ Faça login com as credenciais acima
2️⃣ Configure seus serviços (corte, barba, etc)
3️⃣ Cadastre seus profissionais
4️⃣ Conecte seu WhatsApp
5️⃣ Pronto! Comece a receber agendamentos automáticos 🚀

╔══════════════════════════════════════════╗
║          O QUE ESTÁ INCLUÍDO             ║
╚══════════════════════════════════════════╝

✅ Agendamentos via WhatsApp (bot com IA)
✅ Calendário interativo
✅ Gestão de clientes
✅ Relatórios de faturamento
✅ {plano.max_profissionais} profissional(is)
✅ Até {plano.max_agendamentos_mes} agendamentos/mês
✅ {plano.trial_dias} dias grátis para testar

╔══════════════════════════════════════════╗
║            PRECISA DE AJUDA?             ║
╚══════════════════════════════════════════╝

📧 Email: suporte@gestto.com.br
📱 WhatsApp: (11) 99999-9999
📚 Central de Ajuda: gestto.com.br/ajuda

Estamos aqui para ajudar você a crescer! 💪

---
Equipe Gestto
Transformando agendamentos em experiências! ✨
    """

    try:
        send_mail(
            assunto,
            mensagem,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'noreply@gestto.com.br',
            [usuario.email],
            fail_silently=False,
        )

        logger.info(f'Email de boas-vindas enviado para {usuario.email}')

    except Exception as e:
        logger.error(f'Erro ao enviar email de boas-vindas: {str(e)}')
        raise
