"""
Service Layer para integração com Evolution API
Documentação: https://doc.evolution-api.com/v2/pt/
"""
from unittest import result
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
        Cria uma nova instância no Evolution API (modo self-service)

        Returns:
            dict: {'success': bool, 'data': {...} ou 'error': str}
        """
        # Gerar nome da instância se não existir
        instance_name = self.config.gerar_instance_name()

        # Gerar webhook secret
        webhook_secret = self.config.gerar_webhook_secret()

        # Configurar webhook URL (global)
        webhook_url = f"{settings.SITE_URL}/api/webhooks/whatsapp/"

        data = {
            "instanceName": instance_name,
            "token": webhook_secret,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",

            # Settings padrão
            "rejectCall": True,
            "msgCall": "Não aceitamos chamadas. Por favor, envie mensagem de texto.",
            "groupsIgnore": True,
            "alwaysOnline": False,
            "readMessages": False,
            "readStatus": False,

            # Webhook config
            "webhook": {
                "url": webhook_url,
                "byEvents": True,
                "base64": True,
                "events": [
                    "QRCODE_UPDATED",
                    "MESSAGES_UPSERT",
                    "MESSAGES_UPDATE",
                    "SEND_MESSAGE",
                    "CONNECTION_UPDATE",
                ]
            }
        }

        logger.info(f"Criando instância {instance_name} com webhook: {webhook_url}")

        # 🔧 Buscar sempre da ENV (para empresas novas, self-service)
        api_url = getattr(settings, 'EVOLUTION_API_URL', 'http://localhost:8080')
        api_key = getattr(settings, 'EVOLUTION_API_KEY', 'dev-evolution-key')

        endpoint = f"{api_url.rstrip('/')}/instance/create"
        headers = {
            'Content-Type': 'application/json',
            'apikey': api_key,
        }

        try:
            response = requests.post(endpoint, headers=headers, json=data, timeout=30)
            response.raise_for_status()
            result = {'success': True, 'data': response.json()}
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro na requisição Evolution API: {e}")
            result = {'success': False, 'error': str(e)}

        if result['success']:
            instance_data = result['data'].get('instance', {})

            # Atualiza a configuração local
            self.config.instance_name = instance_name
            self.config.instance_token = instance_data.get('token', webhook_secret)
            self.config.webhook_url = webhook_url
            self.config.status = 'aguardando_qr'
            self.config.metadados = instance_data
            self.config.save()

            logger.info(f"Instância criada com sucesso: {instance_name}")

            # ✅ Salva registro da instância vinculada à empresa
            from whatsapp.models import WhatsAppInstance

            try:
                WhatsAppInstance.objects.update_or_create(
                    empresa=self.config.empresa,  # <-- Corrigido: vincula à empresa
                    defaults={
                        "instance_name": instance_name,
                        "evolution_instance_id": instance_data.get("instanceId", ""),
                        "status": "pending",
                        "webhook_token": webhook_secret,
                    }
                )
                logger.info(f"Instância registrada no banco: {instance_name}")
            except Exception as e:
                logger.error(f"Erro ao salvar WhatsAppInstance: {e}")

            # ✅ Configura Webhook e Settings usando Evolution v2
            webhook_config_result = self._request(
                'POST', f"webhook/{instance_name}/update",
                data={
                    "enabled": True,
                    "url": webhook_url,
                    "byEvents": True,
                    "base64": True,
                    "events": [
                        "QRCODE_UPDATED",
                        "MESSAGES_UPSERT",
                        "MESSAGES_UPDATE",
                        "SEND_MESSAGE",
                        "CONNECTION_UPDATE"
                    ]
                }
            )

            if not webhook_config_result['success']:
                logger.warning(f"Erro ao configurar webhook: {webhook_config_result.get('error')}")

            settings_result = self._request(
                'POST', f"instance/{instance_name}/settings",
                data={
                    "rejectCall": True,
                    "msgCall": "Não aceitamos chamadas. Por favor, envie mensagem de texto.",
                    "groupsIgnore": True,
                    "alwaysOnline": False,
                    "readMessages": False,
                    "readStatus": False
                }
            )

            if not settings_result['success']:
                logger.warning(f"Erro ao configurar settings: {settings_result.get('error')}")

            # ✅ (Opcional) Buscar QR Code logo após criação
            qr_result = self._request('GET', f"instance/qr/{instance_name}")
            if qr_result['success']:
                qr_data = qr_result['data']
                qr_base64 = qr_data.get('base64', '')
                if qr_base64:
                    self.config.qr_code = qr_base64
                    self.config.qr_code_expira_em = now() + timedelta(minutes=2)
                    self.config.save()
                    logger.info("QR Code recebido e salvo com sucesso.")

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

    def configurar_webhook(self):
        """
        Configura webhook da instância (chamado após criar)

        Returns:
            dict: {'success': bool}
        """
        if not self.config.instance_name:
            return {'success': False, 'error': 'Instância não configurada'}

        endpoint = f"webhook/set/{self.config.instance_name}"

        data = {
            "enabled": True,  # Habilitar webhook
            "url": self.config.webhook_url,
            "webhook_by_events": True,  # Webhook por eventos (snake_case para este endpoint)
            "webhook_base64": True,  # Retornar base64 (snake_case para este endpoint)
            "events": [
                "QRCODE_UPDATED",
                "MESSAGES_UPSERT",
                "MESSAGES_UPDATE",
                "SEND_MESSAGE",
                "CONNECTION_UPDATE"
            ]
        }

        result = self._request('POST', endpoint, data=data)

        if result['success']:
            logger.info(f"Webhook configurado para: {self.config.instance_name}")
        else:
            logger.warning(f"Erro ao configurar webhook: {result.get('error')}")

        return result

    def configurar_settings(self):
        """
        Configura settings da instância (rejeitar chamadas, ignorar grupos)

        Returns:
            dict: {'success': bool}
        """
        if not self.config.instance_name:
            return {'success': False, 'error': 'Instância não configurada'}

        endpoint = f"settings/set/{self.config.instance_name}"

        data = {
            "rejectCall": True,
            "msgCall": "Não aceitamos chamadas. Por favor, envie mensagem de texto.",
            "groupsIgnore": True,
            "alwaysOnline": False,
            "readMessages": False,
            "readStatus": False
        }

        result = self._request('POST', endpoint, data=data)

        if result['success']:
            logger.info(f"Settings configurados para: {self.config.instance_name}")
        else:
            logger.warning(f"Erro ao configurar settings: {result.get('error')}")

        return result

    def verificar_existencia_instancia(self):
        """
        Verifica se a instância ainda existe na Evolution API.
        Útil para detectar se foi deletada externamente ou se há erro de comunicação.

        Returns:
            dict: {
                'success': bool,
                'exists': bool | None,
                'data': list | None,
                'error': str | None
            }
        """
        # ⚙️ Caso ainda não haja instância configurada
        if not self.config.instance_name:
            logger.info("ℹ️ Nenhuma instância configurada localmente para esta empresa.")
            return {
                'success': True,
                'exists': False,
                'error': 'Instância não configurada'
            }

        endpoint = "instance/fetchInstances"
        result = self._request('GET', endpoint)

        # ⚠️ Verifica se o resultado é válido
        if not result or not isinstance(result, dict):
            logger.warning("⚠️ Falha na comunicação com Evolution API ao verificar instância (resposta inválida).")
            return {
                'success': False,
                'exists': None,
                'data': None,
                'error': 'Resposta inválida da Evolution API'
            }

        # ✅ Caso a API tenha retornado sucesso
        if result.get('success'):
            data = result.get('data', [])

            # Algumas versões da Evolution retornam dict em vez de list
            if isinstance(data, dict):
                data = [data]

            instance_exists = any(
                isinstance(inst, dict)
                and inst.get('instance', {}).get('instanceName') == self.config.instance_name
                for inst in data
            )

            logger.info(f"🔍 Instância '{self.config.instance_name}' encontrada? {instance_exists}")
            return {
                'success': True,
                'exists': instance_exists,
                'data': data
            }

        # ❌ Caso a requisição tenha falhado
        logger.error(f"❌ Erro ao verificar existência da instância: {result.get('error')}")
        return {
            'success': False,
            'exists': None,
            'data': None,
            'error': result.get('error', 'Erro desconhecido ao verificar instância')
        }

    def sincronizar_status(self):
        """
        Sincroniza o status local com a Evolution API
        - Verifica se instância ainda existe
        - Atualiza status de conexão
        - Detecta se foi deletada externamente

        Returns:
            dict: {'success': bool, 'action': str, 'message': str}
        """
        # Verificar se instância existe
        existe_result = self.verificar_existencia_instancia()

        # Se a instância não existe mais na Evolution API
        if existe_result['success'] and existe_result['exists'] is False:
            logger.warning(f"Instância {self.config.instance_name} foi deletada externamente")

            # Resetar configuração local
            self.config.instance_name = ''
            self.config.instance_token = ''
            self.config.status = 'nao_configurado'
            self.config.qr_code = ''
            self.config.numero_conectado = ''
            self.config.nome_perfil = ''
            self.config.foto_perfil_url = ''
            self.config.webhook_url = ''
            self.config.ultimo_erro = 'Instância foi deletada externamente'
            self.config.save()

            return {
                'success': True,
                'action': 'deleted_externally',
                'message': 'Instância foi deletada externamente e configuração foi resetada'
            }

        # Se instância existe, atualizar status de conexão
        elif existe_result['success'] and existe_result['exists'] is True:
            status_result = self.obter_status_conexao()

            return {
                'success': True,
                'action': 'status_updated',
                'message': f'Status atualizado para: {self.config.status}',
                'status': self.config.status
            }

        # Se não conseguiu verificar
        else:
            return {
                'success': False,
                'action': 'error',
                'message': existe_result.get('error', 'Não foi possível sincronizar'),
                'error': existe_result.get('error')
            }

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

    
    def _request(self, method, endpoint, data=None, instance_token=None):
        base_url = self.base_url or getattr(settings, 'EVOLUTION_API_URL', '')
        url = f"{base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        ...

    def resetar_instancia(self):
        """
        Reseta completamente a configuração WhatsApp local,
        permitindo criar uma nova instância do zero.
        """
        logger.warning(f"🔄 Resetando configuração WhatsApp da empresa: {self.config.empresa.nome}")

        self.config.instance_name = ""
        self.config.instance_token = ""
        self.config.status = "nao_configurado"
        self.config.qr_code = ""
        self.config.qr_code_expira_em = None
        self.config.webhook_url = ""
        self.config.webhook_secret = ""
        self.config.numero_conectado = ""
        self.config.nome_perfil = ""
        self.config.foto_perfil_url = ""
        self.config.metadados = {}
        self.config.ultimo_erro = ""
        self.config.save()

        logger.info(f"✅ Configuração WhatsApp resetada para empresa {self.config.empresa.nome}")
        return {"success": True, "message": "Configuração resetada com sucesso"}
