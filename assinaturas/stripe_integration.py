"""
Integração com Stripe para pagamentos recorrentes
"""
import stripe
from django.conf import settings
from django.utils.timezone import now, timedelta
from .models import Assinatura, HistoricoPagamento, Plano
import logging

logger = logging.getLogger(__name__)

# Configurar Stripe
stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')


def criar_checkout_session(empresa, plano):
    """
    Cria sessão de checkout do Stripe para assinatura

    Args:
        empresa: Instância de Empresa
        plano: Instância de Plano

    Returns:
        dict com url e session_id
    """
    try:
        # Validar se plano tem stripe_price_id configurado
        if not plano.stripe_price_id:
            logger.error(f'Plano {plano.nome} sem stripe_price_id configurado!')
            return {
                'sucesso': False,
                'erro': 'Plano sem preço configurado no Stripe. Contate o suporte.'
            }

        # Criar sessão de checkout usando Price ID pre-configurado
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': plano.stripe_price_id,  # Usar Price ID pre-cadastrado
                'quantity': 1,
            }],
            mode='subscription',
            success_url=f'{settings.SITE_URL}/assinatura/sucesso?session_id={{CHECKOUT_SESSION_ID}}',
            cancel_url=f'{settings.SITE_URL}/assinatura/cancelado',
            client_reference_id=str(empresa.id),
            customer_email=empresa.email,  # Pre-preencher email do cliente
            metadata={
                'empresa_id': empresa.id,
                'empresa_nome': empresa.nome,
                'plano_id': plano.id,
                'plano_nome': plano.nome,
            },
            subscription_data={
                'trial_period_days': plano.trial_dias if plano.trial_dias > 0 else None,
                'metadata': {
                    'empresa_id': empresa.id,
                },
            },
        )

        logger.info(f'Checkout Stripe criado: {session.id} para empresa {empresa.nome}')

        return {
            'url': session.url,
            'session_id': session.id,
            'sucesso': True
        }

    except stripe.error.StripeError as e:
        logger.error(f'Erro ao criar checkout Stripe: {str(e)}')
        return {
            'sucesso': False,
            'erro': str(e)
        }


def processar_webhook_stripe(payload, sig_header):
    """
    Processa eventos do webhook Stripe

    Args:
        payload: Body da requisição (bytes)
        sig_header: Header Stripe-Signature

    Returns:
        dict com status do processamento
    """
    webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        logger.error('Webhook Stripe: payload inválido')
        return {'error': 'Invalid payload'}
    except stripe.error.SignatureVerificationError:
        logger.error('Webhook Stripe: assinatura inválida')
        return {'error': 'Invalid signature'}

    event_type = event['type']
    data = event['data']['object']

    logger.info(f'Webhook Stripe recebido: {event_type}')

    # Checkout completado (primeira cobrança ou trial iniciado)
    if event_type == 'checkout.session.completed':
        return _processar_checkout_completo(data)

    # Assinatura criada
    elif event_type == 'customer.subscription.created':
        return _processar_assinatura_criada(data)

    # Pagamento de invoice bem-sucedido
    elif event_type == 'invoice.payment_succeeded':
        return _processar_pagamento_sucesso(data)

    # Pagamento de invoice falhou
    elif event_type == 'invoice.payment_failed':
        return _processar_pagamento_falha(data)

    # Assinatura deletada/cancelada
    elif event_type == 'customer.subscription.deleted':
        return _processar_assinatura_cancelada(data)

    # Assinatura atualizada
    elif event_type == 'customer.subscription.updated':
        return _processar_assinatura_atualizada(data)

    return {'status': 'ignored', 'event_type': event_type}


def _processar_checkout_completo(session):
    """Processa checkout.session.completed"""
    empresa_id = session['metadata'].get('empresa_id')
    plano_id = session['metadata'].get('plano_id')

    if not empresa_id or not plano_id:
        logger.error('Checkout sem empresa_id ou plano_id nos metadados')
        return {'error': 'Missing metadata'}

    try:
        from empresas.models import Empresa

        empresa = Empresa.objects.get(id=empresa_id)
        plano = Plano.objects.get(id=plano_id)

        # Verificar se já tem assinatura
        assinatura, created = Assinatura.objects.get_or_create(
            empresa=empresa,
            defaults={
                'plano': plano,
                'status': 'trial' if plano.trial_dias > 0 else 'ativa',
                'data_expiracao': now() + timedelta(days=plano.trial_dias if plano.trial_dias > 0 else 30),
                'trial_ativo': plano.trial_dias > 0,
                'gateway': 'stripe',
                'subscription_id_externo': session.get('subscription', ''),
                'customer_id_externo': session.get('customer', ''),
            }
        )

        if not created:
            # Atualizar assinatura existente
            assinatura.subscription_id_externo = session.get('subscription', '')
            assinatura.customer_id_externo = session.get('customer', '')
            assinatura.save()

        logger.info(f'Checkout processado: Empresa {empresa.nome} - Plano {plano.nome}')

        return {'status': 'success', 'assinatura_id': assinatura.id}

    except Exception as e:
        logger.error(f'Erro ao processar checkout: {str(e)}')
        return {'error': str(e)}


def _processar_assinatura_criada(subscription):
    """Processa customer.subscription.created"""
    empresa_id = subscription['metadata'].get('empresa_id')

    if not empresa_id:
        return {'error': 'Missing empresa_id'}

    try:
        assinatura = Assinatura.objects.get(
            empresa_id=empresa_id,
            subscription_id_externo=subscription['id']
        )

        # Verificar se está em trial
        if subscription.get('trial_end'):
            assinatura.trial_ativo = True
            assinatura.data_expiracao = timedelta(seconds=subscription['trial_end'])

        assinatura.save()

        return {'status': 'success'}

    except Assinatura.DoesNotExist:
        logger.warning(f'Assinatura não encontrada para subscription {subscription["id"]}')
        return {'error': 'Assinatura não encontrada'}


def _processar_pagamento_sucesso(invoice):
    """Processa invoice.payment_succeeded"""
    subscription_id = invoice.get('subscription')

    if not subscription_id:
        return {'status': 'ignored'}

    try:
        assinatura = Assinatura.objects.get(subscription_id_externo=subscription_id)

        # Renovar assinatura por 30 dias
        assinatura.renovar(dias=30)

        # Registrar pagamento
        HistoricoPagamento.objects.create(
            assinatura=assinatura,
            valor=invoice['amount_paid'] / 100,  # Converter de centavos
            status='aprovado',
            gateway='stripe',
            transaction_id=invoice['id'],
            payment_method=invoice.get('payment_method_types', [''])[0] if invoice.get('payment_method_types') else '',
            data_aprovacao=now(),
            webhook_payload=invoice
        )

        logger.info(f'Pagamento aprovado: R$ {invoice["amount_paid"]/100} - Empresa {assinatura.empresa.nome}')

        return {'status': 'success', 'assinatura_id': assinatura.id}

    except Assinatura.DoesNotExist:
        logger.warning(f'Assinatura não encontrada para subscription {subscription_id}')
        return {'error': 'Assinatura não encontrada'}


def _processar_pagamento_falha(invoice):
    """Processa invoice.payment_failed"""
    subscription_id = invoice.get('subscription')

    if not subscription_id:
        return {'status': 'ignored'}

    try:
        assinatura = Assinatura.objects.get(subscription_id_externo=subscription_id)

        # Suspender assinatura
        assinatura.suspender(motivo='Pagamento recusado pelo Stripe')

        # Registrar tentativa de pagamento
        HistoricoPagamento.objects.create(
            assinatura=assinatura,
            valor=invoice['amount_due'] / 100,
            status='recusado',
            gateway='stripe',
            transaction_id=invoice['id'],
            webhook_payload=invoice
        )

        logger.warning(f'Pagamento falhou: Empresa {assinatura.empresa.nome} - Assinatura suspensa')

        return {'status': 'success', 'action': 'suspended'}

    except Assinatura.DoesNotExist:
        return {'error': 'Assinatura não encontrada'}


def _processar_assinatura_cancelada(subscription):
    """Processa customer.subscription.deleted"""
    subscription_id = subscription['id']

    try:
        assinatura = Assinatura.objects.get(subscription_id_externo=subscription_id)

        # Cancelar assinatura
        motivo = subscription.get('cancellation_details', {}).get('reason', 'Cancelado pelo cliente no Stripe')
        assinatura.cancelar(motivo=motivo)

        logger.info(f'Assinatura cancelada: Empresa {assinatura.empresa.nome}')

        return {'status': 'success', 'action': 'cancelled'}

    except Assinatura.DoesNotExist:
        return {'error': 'Assinatura não encontrada'}


def _processar_assinatura_atualizada(subscription):
    """Processa customer.subscription.updated"""
    # Pode ser usado para detectar upgrades/downgrades
    # Por enquanto apenas logamos
    logger.info(f'Assinatura atualizada: {subscription["id"]}')
    return {'status': 'acknowledged'}


def cancelar_assinatura_stripe(assinatura):
    """
    Cancela assinatura no Stripe

    Args:
        assinatura: Instância de Assinatura

    Returns:
        bool: True se cancelou com sucesso
    """
    if not assinatura.subscription_id_externo:
        return False

    try:
        stripe.Subscription.delete(assinatura.subscription_id_externo)

        assinatura.cancelar(motivo='Cancelado pelo admin')

        logger.info(f'Assinatura cancelada no Stripe: {assinatura.subscription_id_externo}')

        return True

    except stripe.error.StripeError as e:
        logger.error(f'Erro ao cancelar assinatura no Stripe: {str(e)}')
        return False
