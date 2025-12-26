"""
Service Layer para integração com Evolution API
Documentação: https://doc.evolution-api.com/v2/pt/
"""
import requests
import logging
from django.conf import settings
from django.utils.timezone import now
from datetime import timedelta

logger = logging.getLogger(__name__)


class EvolutionAPIService:
    """
    Classe para interagir com Evolution API v2
    """

    def __init__(self, config_whatsapp):
        """
        Inicializa o service com a configuração do WhatsApp

        Args:
            config_whatsapp: Instância de ConfiguracaoWhatsApp
        """
        self.config = config_whatsapp

        # URL base da API
        self.base_url = config_whatsapp.evolution_api_url or getattr(
            settings, 'EVOLUTION_API_URL', ''
        )

        # API Key global
        self.api_key = config_whatsapp.evolution_api_key or getattr(
            settings, 'EVOLUTION_API_KEY', ''
        )

        # Headers padrão
        self.headers = {
            'Content-Type': 'application/json',
            'apikey': self.api_key
        }

    def _request(self, method, endpoint, data=None, instance_token=None):
        """
        Método genérico para fazer requisições à API

        Args:
            method: GET, POST, PUT, DELETE
            endpoint: Endpoint da API
            data: Dados para enviar (opcional)
            instance_token: Token específico da instância (opcional)

        Returns:
            dict: Resposta da API
        """
        url = f"{self.base_url}/{endpoint}"

        headers = self.headers.copy()
        if instance_token:
            headers['Authorization'] = f'Bearer {instance_token}'

        try:
            response = requests.request(
                method=method,
                url=url,
                json=data,
                headers=headers,
                timeout=30
            )

            response.raise_for_status()

            # Tentar fazer parse do JSON
            try:
                return {'success': True, 'data': response.json()}
            except ValueError:
                return {'success': True, 'data': response.text}

        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição Evolution API: {str(e)}")
            error_message = str(e)

            # Tentar extrair mensagem de erro da resposta
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', error_message)
                except:
                    error_message = e.response.text or error_message

            return {
                'success': False,
                'error': error_message
            }

    # ==========================================
    # GERENCIAMENTO DE INSTÂNCIAS
    # ==========================================

    def criar_instancia(self):
        """
        Cria uma nova instância no Evolution API

        Returns:
            dict: {'success': bool, 'data': {...} ou 'error': str}
        """
        # Gerar nome da instância se não existir
        instance_name = self.config.gerar_instance_name()

        # Gerar webhook secret
        webhook_secret = self.config.gerar_webhook_secret()

        # Configurar webhook URL
        webhook_url = f"{settings.SITE_URL}/api/webhooks/whatsapp/{self.config.empresa.id}/{webhook_secret}/"

        data = {
            "instanceName": instance_name,
            "token": webhook_secret,  # Token para autenticação de webhooks
            "qrcode": True,  # Retornar QR code
            "integration": "WHATSAPP-BAILEYS",  # Tipo de integração
            "webhookUrl": webhook_url,  # URL do webhook
            "webhookByEvents": True,  # Receber webhooks por evento
            "webhookBase64": True,  # QR Code em base64
            "events": [
                "QRCODE_UPDATED",
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "CONNECTION_UPDATE",
                "CALL",
                "NEW_MESSAGE",
            ]
        }

        result = self._request('POST', 'instance/create', data=data)

        if result['success']:
            # Salvar dados da instância
            instance_data = result['data'].get('instance', {})

            self.config.instance_name = instance_name
            self.config.instance_token = instance_data.get('token', webhook_secret)
            self.config.webhook_url = webhook_url
            self.config.status = 'aguardando_qr'
            self.config.metadados = instance_data
            self.config.save()

            logger.info(f"Instância criada: {instance_name}")
        else:
            self.config.status = 'erro'
            self.config.ultimo_erro = result.get('error', 'Erro desconhecido')
            self.config.save()
            logger.error(f"Erro ao criar instância: {result.get('error')}")

        return result

    def obter_qrcode(self):
        """
        Obtém o QR Code atual da instância

        Returns:
            dict: {'success': bool, 'qrcode': str (base64), 'error': str}
        """
        if not self.config.instance_name:
            return {'success': False, 'error': 'Instância não configurada'}

        endpoint = f"instance/connect/{self.config.instance_name}"
        result = self._request('GET', endpoint)

        if result['success']:
            data = result['data']
            qr_base64 = data.get('base64', '')

            if qr_base64:
                # Salvar QR Code
                self.config.qr_code = qr_base64
                self.config.qr_code_expira_em = now() + timedelta(minutes=2)
                self.config.status = 'aguardando_qr'
                self.config.save()

                logger.info(f"QR Code obtido para {self.config.instance_name}")
                return {'success': True, 'qrcode': qr_base64}
            else:
                return {'success': False, 'error': 'QR Code não disponível'}

        return result

    def obter_status_conexao(self):
        """
        Verifica o status da conexão da instância

        Returns:
            dict: {'success': bool, 'status': str, 'data': {...}}
        """
        if not self.config.instance_name:
            return {'success': False, 'error': 'Instância não configurada'}

        endpoint = f"instance/connectionState/{self.config.instance_name}"
        result = self._request('GET', endpoint)

        if result['success']:
            state_data = result['data']
            instance_state = state_data.get('instance', {})
            connection_state = instance_state.get('state', 'unknown')

            # Mapear estados da Evolution para nossos estados
            status_map = {
                'open': 'conectado',
                'connecting': 'conectando',
                'close': 'desconectado',
                'refused': 'erro',
            }

            novo_status = status_map.get(connection_state, 'desconectado')

            # Atualizar config
            self.config.status = novo_status
            self.config.ultima_sincronizacao = now()

            # Se conectado, buscar dados do perfil
            if novo_status == 'conectado':
                profile_data = instance_state.get('profilePictureUrl', '')
                self.config.foto_perfil_url = profile_data

            self.config.save()

            return {
                'success': True,
                'status': novo_status,
                'data': state_data
            }

        return result

    def desconectar_instancia(self):
        """
        Desconecta e logout da instância

        Returns:
            dict: {'success': bool, 'message': str}
        """
        if not self.config.instance_name:
            return {'success': False, 'error': 'Instância não configurada'}

        endpoint = f"instance/logout/{self.config.instance_name}"
        result = self._request('DELETE', endpoint)

        if result['success']:
            # Atualizar status
            self.config.status = 'desconectado'
            self.config.numero_conectado = ''
            self.config.nome_perfil = ''
            self.config.foto_perfil_url = ''
            self.config.qr_code = ''
            self.config.save()

            logger.info(f"Instância desconectada: {self.config.instance_name}")

        return result

    def deletar_instancia(self):
        """
        Deleta completamente a instância (irreversível)

        Returns:
            dict: {'success': bool}
        """
        if not self.config.instance_name:
            return {'success': False, 'error': 'Instância não configurada'}

        endpoint = f"instance/delete/{self.config.instance_name}"
        result = self._request('DELETE', endpoint)

        if result['success']:
            # Resetar configuração
            self.config.instance_name = ''
            self.config.instance_token = ''
            self.config.status = 'nao_configurado'
            self.config.qr_code = ''
            self.config.numero_conectado = ''
            self.config.nome_perfil = ''
            self.config.foto_perfil_url = ''
            self.config.webhook_url = ''
            self.config.save()

            logger.info(f"Instância deletada")

        return result

    # ==========================================
    # ENVIO DE MENSAGENS
    # ==========================================

    def enviar_mensagem_texto(self, numero, mensagem):
        """
        Envia mensagem de texto

        Args:
            numero: Número com DDI (ex: 5511999999999)
            mensagem: Texto da mensagem

        Returns:
            dict: {'success': bool, 'message_id': str}
        """
        if not self.config.esta_conectado():
            return {'success': False, 'error': 'WhatsApp não conectado'}

        data = {
            "number": numero,
            "text": mensagem
        }

        endpoint = f"message/sendText/{self.config.instance_name}"
        result = self._request('POST', endpoint, data=data)

        if result['success']:
            message_data = result['data']
            message_id = message_data.get('key', {}).get('id', '')

            logger.info(f"Mensagem enviada para {numero}")
            return {'success': True, 'message_id': message_id, 'data': message_data}

        return result

    def enviar_mensagem_imagem(self, numero, url_imagem, legenda=''):
        """
        Envia imagem via URL

        Args:
            numero: Número com DDI
            url_imagem: URL pública da imagem
            legenda: Texto da legenda (opcional)

        Returns:
            dict: {'success': bool, 'message_id': str}
        """
        if not self.config.esta_conectado():
            return {'success': False, 'error': 'WhatsApp não conectado'}

        data = {
            "number": numero,
            "mediatype": "image",
            "media": url_imagem,
            "caption": legenda
        }

        endpoint = f"message/sendMedia/{self.config.instance_name}"
        return self._request('POST', endpoint, data=data)

    # ==========================================
    # WEBHOOKS (RECEBIMENTO DE MENSAGENS)
    # ==========================================

    def processar_webhook(self, payload):
        """
        Processa webhook recebido da Evolution API

        Args:
            payload: Dados do webhook

        Returns:
            dict: {'success': bool, 'processed': bool}
        """
        event_type = payload.get('event')

        logger.info(f"Webhook recebido: {event_type}")

        # QR Code atualizado
        if event_type == 'QRCODE_UPDATED':
            qrcode_data = payload.get('data', {})
            qr_base64 = qrcode_data.get('qrcode', {}).get('base64', '')

            if qr_base64:
                self.config.qr_code = qr_base64
                self.config.qr_code_expira_em = now() + timedelta(minutes=2)
                self.config.status = 'aguardando_qr'
                self.config.save()

                return {'success': True, 'processed': True, 'type': 'qrcode_updated'}

        # Status de conexão
        elif event_type == 'CONNECTION_UPDATE':
            connection_data = payload.get('data', {})
            state = connection_data.get('state', 'unknown')

            status_map = {
                'open': 'conectado',
                'connecting': 'conectando',
                'close': 'desconectado',
            }

            novo_status = status_map.get(state, self.config.status)
            self.config.status = novo_status
            self.config.ultima_sincronizacao = now()

            # Se conectou, limpar QR Code
            if novo_status == 'conectado':
                self.config.qr_code = ''

            self.config.save()

            return {'success': True, 'processed': True, 'type': 'connection_update'}

        # Nova mensagem recebida
        elif event_type in ['MESSAGES_UPSERT', 'NEW_MESSAGE']:
            message_data = payload.get('data', {})

            # Aqui você pode processar a mensagem recebida
            # Exemplo: criar registro no banco, responder automaticamente, etc.

            return {'success': True, 'processed': True, 'type': 'new_message'}

        return {'success': True, 'processed': False, 'type': 'unknown_event'}
