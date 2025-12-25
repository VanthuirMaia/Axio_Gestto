"""
Integração com Asaas para pagamentos recorrentes (Brasil)
"""
import requests
from django.conf import settings
from django.utils.timezone import now, timedelta
from datetime import datetime, date
from .models import Assinatura, HistoricoPagamento, Plano
import logging

logger = logging.getLogger(__name__)


class AsaasClient:
    """Cliente para API do Asaas"""

    def __init__(self):
        self.api_key = getattr(settings, 'ASAAS_API_KEY', '')
        self.sandbox = getattr(settings, 'ASAAS_SANDBOX', True)

        if self.sandbox:
            self.base_url = 'https://sandbox.asaas.com/api/v3'
        else:
            self.base_url = 'https://api.asaas.com/v3'

        self.headers = {
            'access_token': self.api_key,
            'Content-Type': 'application/json',
        }

    def _request(self, method, endpoint, data=None):
        """Faz requisição à API do Asaas"""
        url = f'{self.base_url}/{endpoint}'

        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self.headers,
                json=data,
                timeout=30
            )

            response.raise_for_status()

            return {
                'sucesso': True,
                'data': response.json()
            }

        except requests.RequestException as e:
            logger.error(f'Erro na requisição Asaas: {str(e)}')

            return {
                'sucesso': False,
                'erro': str(e),
                'response': e.response.json() if hasattr(e, 'response') and e.response else None
            }

    def criar_cliente(self, empresa):
        """
        Cria cliente no Asaas

        Args:
            empresa: Instância de Empresa

        Returns:
            dict com customer_id
        """
        data = {
            'name': empresa.nome,
            'email': empresa.email,
            'phone': empresa.telefone.replace(' ', '').replace('-', ''),
            'cpfCnpj': empresa.cnpj.replace('.', '').replace('/', '').replace('-', ''),
            'notificationDisabled': False,
        }

        if empresa.endereco:
            data['address'] = empresa.endereco
            data['province'] = empresa.cidade
            data['postalCode'] = empresa.cep.replace('-', '')

        result = self._request('POST', 'customers', data)

        if result['sucesso']:
            customer_id = result['data']['id']
            logger.info(f'Cliente Asaas criado: {customer_id} para empresa {empresa.nome}')
            return {'sucesso': True, 'customer_id': customer_id}
        else:
            return result

    def criar_assinatura(self, customer_id, plano):
        """
        Cria assinatura recorrente no Asaas

        Args:
            customer_id: ID do cliente no Asaas
            plano: Instância de Plano

        Returns:
            dict com subscription_id
        """
        # Data do próximo vencimento
        if plano.trial_dias > 0:
            next_due_date = (now() + timedelta(days=plano.trial_dias)).date()
        else:
            next_due_date = (now() + timedelta(days=30)).date()

        data = {
            'customer': customer_id,
            'billingType': 'CREDIT_CARD',  # Ou 'BOLETO', 'PIX'
            'value': float(plano.preco_mensal),
            'nextDueDate': next_due_date.isoformat(),
            'cycle': 'MONTHLY',
            'description': f'Gestto - Plano {plano.get_nome_display()}',
        }

        result = self._request('POST', 'subscriptions', data)

        if result['sucesso']:
            subscription_id = result['data']['id']
            logger.info(f'Assinatura Asaas criada: {subscription_id}')
            return {'sucesso': True, 'subscription_id': subscription_id}
        else:
            return result

    def cancelar_assinatura(self, subscription_id):
        """
        Cancela assinatura no Asaas

        Args:
            subscription_id: ID da assinatura no Asaas

        Returns:
            dict com status
        """
        result = self._request('DELETE', f'subscriptions/{subscription_id}')

        if result['sucesso']:
            logger.info(f'Assinatura Asaas cancelada: {subscription_id}')

        return result

    def buscar_pagamentos(self, subscription_id):
        """
        Busca pagamentos de uma assinatura

        Args:
            subscription_id: ID da assinatura

        Returns:
            list de pagamentos
        """
        result = self._request('GET', f'subscriptions/{subscription_id}/payments')

        if result['sucesso']:
            return result['data'].get('data', [])
        else:
            return []


def criar_assinatura_asaas(empresa, plano):
    """
    Cria assinatura completa no Asaas (cliente + assinatura)

    Args:
        empresa: Instância de Empresa
        plano: Instância de Plano

    Returns:
        dict com informações da assinatura
    """
    client = AsaasClient()

    # 1. Criar cliente no Asaas
    result_cliente = client.criar_cliente(empresa)

    if not result_cliente['sucesso']:
        return result_cliente

    customer_id = result_cliente['customer_id']

    # 2. Criar assinatura
    result_assinatura = client.criar_assinatura(customer_id, plano)

    if not result_assinatura['sucesso']:
        return result_assinatura

    subscription_id = result_assinatura['subscription_id']

    # 3. Criar/Atualizar registro local
    try:
        assinatura, created = Assinatura.objects.get_or_create(
            empresa=empresa,
            defaults={
                'plano': plano,
                'status': 'trial' if plano.trial_dias > 0 else 'ativa',
                'data_expiracao': now() + timedelta(days=plano.trial_dias if plano.trial_dias > 0 else 30),
                'trial_ativo': plano.trial_dias > 0,
                'gateway': 'asaas',
                'subscription_id_externo': subscription_id,
                'customer_id_externo': customer_id,
            }
        )

        if not created:
            assinatura.subscription_id_externo = subscription_id
            assinatura.customer_id_externo = customer_id
            assinatura.save()

        logger.info(f'Assinatura Asaas criada no banco: Empresa {empresa.nome}')

        return {
            'sucesso': True,
            'assinatura_id': assinatura.id,
            'customer_id': customer_id,
            'subscription_id': subscription_id,
        }

    except Exception as e:
        logger.error(f'Erro ao salvar assinatura no banco: {str(e)}')
        return {'sucesso': False, 'erro': str(e)}


def processar_webhook_asaas(payload):
    """
    Processa webhook do Asaas

    Eventos possíveis:
    - PAYMENT_CREATED
    - PAYMENT_UPDATED
    - PAYMENT_CONFIRMED
    - PAYMENT_RECEIVED
    - PAYMENT_OVERDUE
    - PAYMENT_DELETED
    - PAYMENT_RESTORED
    - PAYMENT_REFUNDED
    - PAYMENT_RECEIVED_IN_CASH_UNDONE
    - PAYMENT_CHARGEBACK_REQUESTED
    - PAYMENT_CHARGEBACK_DISPUTE
    - PAYMENT_AWAITING_CHARGEBACK_REVERSAL
    - PAYMENT_DUNNING_RECEIVED
    - PAYMENT_DUNNING_REQUESTED
    - PAYMENT_BANK_SLIP_VIEWED
    - PAYMENT_CHECKOUT_VIEWED

    Args:
        payload: dict do webhook

    Returns:
        dict com status
    """
    event_type = payload.get('event')
    payment_data = payload.get('payment', {})

    logger.info(f'Webhook Asaas recebido: {event_type}')

    # Pagamento confirmado/recebido
    if event_type in ['PAYMENT_CONFIRMED', 'PAYMENT_RECEIVED']:
        return _processar_pagamento_confirmado_asaas(payment_data)

    # Pagamento vencido
    elif event_type == 'PAYMENT_OVERDUE':
        return _processar_pagamento_vencido_asaas(payment_data)

    # Pagamento estornado
    elif event_type == 'PAYMENT_REFUNDED':
        return _processar_pagamento_estornado_asaas(payment_data)

    # Outros eventos
    return {'status': 'ignored', 'event': event_type}


def _processar_pagamento_confirmado_asaas(payment):
    """Processa pagamento confirmado no Asaas"""
    subscription_id = payment.get('subscription')

    if not subscription_id:
        return {'status': 'ignored'}

    try:
        assinatura = Assinatura.objects.get(subscription_id_externo=subscription_id)

        # Renovar assinatura
        assinatura.renovar(dias=30)

        # Registrar pagamento
        HistoricoPagamento.objects.create(
            assinatura=assinatura,
            valor=float(payment['value']),
            status='aprovado',
            gateway='asaas',
            transaction_id=payment['id'],
            payment_method=payment.get('billingType', '').lower(),
            data_aprovacao=now(),
            data_vencimento=datetime.strptime(payment['dueDate'], '%Y-%m-%d').date() if payment.get('dueDate') else None,
            webhook_payload=payment
        )

        logger.info(f'Pagamento Asaas confirmado: R$ {payment["value"]} - Empresa {assinatura.empresa.nome}')

        return {'status': 'success', 'assinatura_id': assinatura.id}

    except Assinatura.DoesNotExist:
        logger.warning(f'Assinatura não encontrada para subscription {subscription_id}')
        return {'error': 'Assinatura não encontrada'}


def _processar_pagamento_vencido_asaas(payment):
    """Processa pagamento vencido no Asaas"""
    subscription_id = payment.get('subscription')

    if not subscription_id:
        return {'status': 'ignored'}

    try:
        assinatura = Assinatura.objects.get(subscription_id_externo=subscription_id)

        # Suspender assinatura
        assinatura.suspender(motivo='Pagamento vencido (Asaas)')

        # Registrar tentativa
        HistoricoPagamento.objects.create(
            assinatura=assinatura,
            valor=float(payment['value']),
            status='pendente',
            gateway='asaas',
            transaction_id=payment['id'],
            webhook_payload=payment
        )

        logger.warning(f'Pagamento vencido: Empresa {assinatura.empresa.nome} - Assinatura suspensa')

        return {'status': 'success', 'action': 'suspended'}

    except Assinatura.DoesNotExist:
        return {'error': 'Assinatura não encontrada'}


def _processar_pagamento_estornado_asaas(payment):
    """Processa pagamento estornado no Asaas"""
    subscription_id = payment.get('subscription')

    if not subscription_id:
        return {'status': 'ignored'}

    try:
        assinatura = Assinatura.objects.get(subscription_id_externo=subscription_id)

        # Suspender assinatura
        assinatura.suspender(motivo='Pagamento estornado (Asaas)')

        # Atualizar histórico
        try:
            historico = HistoricoPagamento.objects.get(
                assinatura=assinatura,
                transaction_id=payment['id']
            )
            historico.status = 'estornado'
            historico.save()
        except HistoricoPagamento.DoesNotExist:
            # Criar novo registro
            HistoricoPagamento.objects.create(
                assinatura=assinatura,
                valor=float(payment['value']),
                status='estornado',
                gateway='asaas',
                transaction_id=payment['id'],
                webhook_payload=payment
            )

        logger.warning(f'Pagamento estornado: Empresa {assinatura.empresa.nome}')

        return {'status': 'success', 'action': 'suspended'}

    except Assinatura.DoesNotExist:
        return {'error': 'Assinatura não encontrada'}


def cancelar_assinatura_asaas(assinatura):
    """
    Cancela assinatura no Asaas

    Args:
        assinatura: Instância de Assinatura

    Returns:
        bool: True se cancelou com sucesso
    """
    if not assinatura.subscription_id_externo:
        return False

    client = AsaasClient()
    result = client.cancelar_assinatura(assinatura.subscription_id_externo)

    if result['sucesso']:
        assinatura.cancelar(motivo='Cancelado pelo admin')
        return True
    else:
        return False
