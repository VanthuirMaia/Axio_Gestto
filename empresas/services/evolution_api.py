"""
Service Layer para integração com Evolution API
Documentação: https://doc.evolution-api.com/v2/pt/
"""
import requests
import logging
import time
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

    def _buscar_instancia_na_api(self, instance_name):
        """
        Busca uma instância específica na Evolution API pelo nome.

        Returns:
            dict: {'exists': bool, 'instance': dict|None, 'status': str|None}
        """
        api_url = getattr(settings, 'EVOLUTION_API_URL', '')
        api_key = getattr(settings, 'EVOLUTION_API_KEY', '')

        if not api_url or not api_key:
            return {'exists': False, 'instance': None, 'status': None, 'error': 'API não configurada'}

        try:
            response = requests.get(
                f"{api_url.rstrip('/')}/instance/fetchInstances",
                headers={'Content-Type': 'application/json', 'apikey': api_key},
                timeout=15
            )
            response.raise_for_status()
            instances = response.json()

            # Buscar instância pelo nome
            for inst in instances:
                if inst.get('name') == instance_name:
                    return {
                        'exists': True,
                        'instance': inst,
                        'status': inst.get('connectionStatus', 'unknown')
                    }

            return {'exists': False, 'instance': None, 'status': None}

        except Exception as e:
            logger.error(f"Erro ao buscar instância na API: {e}")
            return {'exists': False, 'instance': None, 'status': None, 'error': str(e)}

    def _buscar_dados_perfil(self):
        """
        Busca o número e nome do perfil conectado na Evolution API.
        Atualiza self.config com os dados encontrados.
        """
        if not self.config.instance_name:
            logger.warning("_buscar_dados_perfil: instance_name vazio")
            return

        api_url = getattr(settings, 'EVOLUTION_API_URL', '')
        api_key = getattr(settings, 'EVOLUTION_API_KEY', '')

        if not api_url or not api_key:
            logger.warning("_buscar_dados_perfil: API URL ou KEY não configuradas")
            return

        try:
            # Buscar informações da instância
            response = requests.get(
                f"{api_url.rstrip('/')}/instance/fetchInstances",
                headers={'Content-Type': 'application/json', 'apikey': api_key},
                params={'instanceName': self.config.instance_name},
                timeout=15
            )
            response.raise_for_status()
            instances = response.json()

            logger.info(f"_buscar_dados_perfil: Resposta da API: {instances}")

            # Procurar a instância correta
            for inst in instances:
                logger.info(f"_buscar_dados_perfil: Analisando instância: {inst}")

                inst_name = inst.get('name') or inst.get('instance', {}).get('instanceName')
                if inst_name == self.config.instance_name:
                    # Tentar extrair owner de diferentes locais na estrutura
                    owner = (
                        inst.get('owner', '') or
                        inst.get('instance', {}).get('owner', '') or
                        inst.get('ownerJid', '') or
                        inst.get('instance', {}).get('ownerJid', '')
                    )

                    logger.info(f"_buscar_dados_perfil: owner encontrado: {owner}")

                    if owner:
                        # owner geralmente vem como "5511999999999@s.whatsapp.net"
                        numero = owner.split('@')[0] if '@' in owner else owner
                        # Formatar número para exibição
                        if len(numero) >= 12:
                            # Formato: +55 (11) 99999-9999
                            self.config.numero_conectado = f"+{numero[:2]} ({numero[2:4]}) {numero[4:9]}-{numero[9:]}"
                        else:
                            self.config.numero_conectado = numero

                    # Tentar extrair nome do perfil de diferentes locais
                    profile_name = (
                        inst.get('profileName', '') or
                        inst.get('instance', {}).get('profileName', '') or
                        inst.get('pushName', '') or
                        inst.get('instance', {}).get('pushName', '') or
                        inst.get('profileStatus', '') or
                        inst.get('instance', {}).get('profileStatus', '')
                    )

                    logger.info(f"_buscar_dados_perfil: profileName encontrado: {profile_name}")

                    if profile_name:
                        self.config.nome_perfil = profile_name
                    elif owner:
                        # Se não tem nome do perfil, usar o número como fallback
                        self.config.nome_perfil = self.config.numero_conectado

                    # Extrair foto do perfil
                    profile_pic = (
                        inst.get('profilePictureUrl', '') or
                        inst.get('instance', {}).get('profilePictureUrl', '') or
                        inst.get('profilePicUrl', '') or
                        inst.get('instance', {}).get('profilePicUrl', '')
                    )

                    if profile_pic:
                        self.config.foto_perfil_url = profile_pic

                    logger.info(f"Dados do perfil atualizados: {self.config.numero_conectado} - {self.config.nome_perfil}")
                    break

            # Se não encontrou o nome do perfil, tentar endpoint específico
            if not self.config.nome_perfil or self.config.nome_perfil == self.config.numero_conectado:
                self._buscar_nome_perfil_alternativo(api_url, api_key)

        except Exception as e:
            logger.warning(f"Erro ao buscar dados do perfil: {e}")

    def _buscar_nome_perfil_alternativo(self, api_url, api_key):
        """Tenta buscar o nome do perfil via endpoint alternativo"""
        try:
            # Tentar endpoint de fetch profile
            response = requests.get(
                f"{api_url.rstrip('/')}/chat/fetchProfile/{self.config.instance_name}",
                headers={'Content-Type': 'application/json', 'apikey': api_key},
                params={'number': self.config.numero_conectado.replace('+', '').replace(' ', '').replace('(', '').replace(')', '').replace('-', '')},
                timeout=10
            )
            if response.status_code == 200:
                data = response.json()
                logger.info(f"_buscar_nome_perfil_alternativo: Resposta: {data}")
                name = data.get('name') or data.get('pushName') or data.get('profileName', '')
                if name:
                    self.config.nome_perfil = name
                    logger.info(f"Nome do perfil encontrado via endpoint alternativo: {name}")
        except Exception as e:
            logger.debug(f"Endpoint alternativo de perfil não disponível: {e}")

    def _obter_qrcode_com_retry(self, instance_name, max_tentativas=5, intervalo=2):
        """
        Tenta obter o QR Code com retry.

        Args:
            instance_name: Nome da instância
            max_tentativas: Número máximo de tentativas
            intervalo: Segundos entre tentativas

        Returns:
            dict: {'success': bool, 'qrcode': str|None, 'error': str|None}
        """
        api_url = getattr(settings, 'EVOLUTION_API_URL', '')
        api_key = getattr(settings, 'EVOLUTION_API_KEY', '')

        for tentativa in range(1, max_tentativas + 1):
            logger.info(f"Tentativa {tentativa}/{max_tentativas} de obter QR Code para {instance_name}")

            try:
                # Tenta endpoint /instance/connect primeiro (gera QR se necessário)
                response = requests.get(
                    f"{api_url.rstrip('/')}/instance/connect/{instance_name}",
                    headers={'Content-Type': 'application/json', 'apikey': api_key},
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    qr_base64 = data.get('base64', '')

                    if qr_base64:
                        logger.info(f"QR Code obtido com sucesso na tentativa {tentativa}")
                        return {'success': True, 'qrcode': qr_base64}

                # Se não veio no connect, tenta endpoint específico de QR
                response = requests.get(
                    f"{api_url.rstrip('/')}/instance/qr/{instance_name}",
                    headers={'Content-Type': 'application/json', 'apikey': api_key},
                    timeout=15
                )

                if response.status_code == 200:
                    data = response.json()
                    qr_base64 = data.get('base64', '')

                    if qr_base64:
                        logger.info(f"QR Code obtido via /qr na tentativa {tentativa}")
                        return {'success': True, 'qrcode': qr_base64}

            except Exception as e:
                logger.warning(f"Erro na tentativa {tentativa}: {e}")

            # Aguardar antes da próxima tentativa
            if tentativa < max_tentativas:
                time.sleep(intervalo)

        return {
            'success': False,
            'qrcode': None,
            'error': f'QR Code não disponível após {max_tentativas} tentativas'
        }

    def conectar_whatsapp(self):
        """
        Método principal e robusto para conectar WhatsApp.

        Fluxo:
        1. Verifica se instância já existe na Evolution API
        2. Se existe e está conectada -> retorna sucesso
        3. Se existe mas não conectada -> obtém QR Code
        4. Se não existe -> cria instância e obtém QR Code

        Returns:
            dict: {
                'success': bool,
                'qrcode': str|None,
                'status': str,
                'message': str,
                'action': str  # 'already_connected', 'qrcode_ready', 'created', 'error'
            }
        """
        # Gerar nome da instância
        instance_name = self.config.gerar_instance_name()
        logger.info(f"Iniciando conexão WhatsApp para instância: {instance_name}")

        # 1. Verificar se instância já existe na Evolution API
        busca = self._buscar_instancia_na_api(instance_name)

        if busca.get('exists'):
            status_api = busca.get('status', 'unknown')
            logger.info(f"Instância {instance_name} já existe na API com status: {status_api}")

            # Se já está conectada
            if status_api == 'open':
                self.config.status = 'conectado'
                self.config.save()
                return {
                    'success': True,
                    'qrcode': None,
                    'status': 'conectado',
                    'message': 'WhatsApp já está conectado!',
                    'action': 'already_connected'
                }

            # Se está em outro status, tentar obter QR Code
            qr_result = self._obter_qrcode_com_retry(instance_name)

            if qr_result['success']:
                self.config.qr_code = qr_result['qrcode']
                self.config.qr_code_expira_em = now() + timedelta(minutes=2)
                self.config.status = 'aguardando_qr'
                self.config.save()

                return {
                    'success': True,
                    'qrcode': qr_result['qrcode'],
                    'status': 'aguardando_qr',
                    'message': 'QR Code pronto! Escaneie com seu WhatsApp.',
                    'action': 'qrcode_ready'
                }
            else:
                # Instância existe mas não conseguiu QR - tentar deletar e recriar
                logger.warning(f"Instância existe mas QR não disponível. Tentando deletar para recriar...")
                
                # Tentar deletar
                deletou = self._deletar_instancia_na_api(instance_name)
                
                if not deletou:
                    # Deleção falhou - retornar erro ao invés de criar duplicata
                    logger.error(f"Falha ao deletar instância {instance_name}. Abortando para evitar duplicação.")
                    self.config.status = 'erro'
                    self.config.ultimo_erro = 'Erro ao resetar instância. Tente novamente em alguns minutos.'
                    self.config.save()
                    
                    return {
                        'success': False,
                        'qrcode': None,
                        'status': 'erro',
                        'message': 'Erro ao resetar instância. Tente novamente em alguns minutos ou contate o suporte.',
                        'action': 'error'
                    }
                
                # Aguardar para garantir que API processou a deleção
                logger.info(f"Aguardando 2 segundos para API processar deleção...")
                time.sleep(2)
                
                # Verificar se realmente foi deletada
                busca_confirmacao = self._buscar_instancia_na_api(instance_name)
                if busca_confirmacao.get('exists'):
                    logger.error(f"Instância {instance_name} ainda existe após deleção! Abortando para evitar duplicação.")
                    self.config.status = 'erro'
                    self.config.ultimo_erro = 'A instância antiga não pôde ser removida.'
                    self.config.save()
                    
                    return {
                        'success': False,
                        'qrcode': None,
                        'status': 'erro',
                        'message': 'Erro ao resetar instância. A instância antiga não pôde ser removida. Contate o suporte.',
                        'action': 'error'
                    }
                
                logger.info(f"Instância {instance_name} deletada com sucesso. Prosseguindo com criação...")
                # Continua para criar nova instância

        # 2. Criar nova instância
        logger.info(f"Criando nova instância: {instance_name}")
        criar_result = self._criar_instancia_na_api(instance_name)

        if not criar_result['success']:
            self.config.status = 'erro'
            self.config.ultimo_erro = criar_result.get('error', 'Erro ao criar instância')
            self.config.save()
            return {
                'success': False,
                'qrcode': None,
                'status': 'erro',
                'message': criar_result.get('error', 'Erro ao criar instância'),
                'action': 'error'
            }

        # Salvar dados da instância criada
        instance_data = criar_result.get('data', {}).get('instance', {})
        self.config.instance_name = instance_name
        self.config.instance_token = instance_data.get('token', '')

        # Salvar URL do webhook (URL única - identificação por instance_name)
        self.config.webhook_url = getattr(settings, 'N8N_WEBHOOK_URL', '') or f"{settings.SITE_URL}/api/webhooks/whatsapp/"

        self.config.status = 'aguardando_qr'
        self.config.save()

        # Registrar no banco
        from empresas.models import WhatsAppInstance
        try:
            WhatsAppInstance.objects.update_or_create(
                empresa=self.config.empresa,
                defaults={
                    "instance_name": instance_name,
                    "evolution_instance_id": instance_data.get("instanceId", ""),
                    "status": "pending",
                    "webhook_token": self.config.webhook_secret,
                }
            )
        except Exception as e:
            logger.error(f"Erro ao salvar WhatsAppInstance: {e}")

        # 3. Obter QR Code com retry
        # Aguardar um pouco para a instância ficar pronta
        time.sleep(1)

        qr_result = self._obter_qrcode_com_retry(instance_name)

        if qr_result['success']:
            self.config.qr_code = qr_result['qrcode']
            self.config.qr_code_expira_em = now() + timedelta(minutes=2)
            self.config.save()

            return {
                'success': True,
                'qrcode': qr_result['qrcode'],
                'status': 'aguardando_qr',
                'message': 'Instância criada! Escaneie o QR Code.',
                'action': 'created'
            }
        else:
            # Criou mas não conseguiu QR
            return {
                'success': False,
                'qrcode': None,
                'status': 'aguardando_qr',
                'message': 'Instância criada mas QR Code ainda não disponível. Atualize a página em alguns segundos.',
                'action': 'created_no_qr'
            }

    def _criar_instancia_na_api(self, instance_name):
        """
        Cria uma instância na Evolution API (método interno).
        """
        api_url = getattr(settings, 'EVOLUTION_API_URL', '')
        api_key = getattr(settings, 'EVOLUTION_API_KEY', '')

        if not api_url or not api_key:
            return {'success': False, 'error': 'Evolution API não configurada'}

        webhook_secret = self.config.gerar_webhook_secret()

        # Usar N8N_WEBHOOK_URL diretamente (URL única para todas as empresas)
        # A identificação da empresa é feita pelo instance_name no payload
        webhook_url = getattr(settings, 'N8N_WEBHOOK_URL', '') or f"{settings.SITE_URL}/api/webhooks/whatsapp/"

        logger.info(f"Webhook configurado: {webhook_url}")

        data = {
            "instanceName": instance_name,
            "token": webhook_secret,
            "qrcode": True,
            "integration": "WHATSAPP-BAILEYS",
            "rejectCall": True,
            "msgCall": "Não aceitamos chamadas. Por favor, envie mensagem de texto.",
            "groupsIgnore": True,
            "alwaysOnline": False,
            "readMessages": False,
            "readStatus": False,
            "webhook": {
                "url": webhook_url,
                "byEvents": False,  # IMPORTANTE: False para enviar apikey e server_url no payload
                "base64": True,
                "events": [
                    "MESSAGES_UPSERT",
                ]
            }
        }

        try:
            response = requests.post(
                f"{api_url.rstrip('/')}/instance/create",
                headers={'Content-Type': 'application/json', 'apikey': api_key},
                json=data,
                timeout=30
            )
            response.raise_for_status()
            logger.info(f"Instância {instance_name} criada com sucesso")
            return {'success': True, 'data': response.json()}

        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 403:
                error_msg = "Acesso negado. Verifique a EVOLUTION_API_KEY."
            elif e.response.status_code == 400:
                # Pode ser que a instância já existe
                error_msg = f"Erro 400: {e.response.text}"
            else:
                error_msg = f"Erro HTTP {e.response.status_code}"
            logger.error(f"Erro ao criar instância: {error_msg}")
            return {'success': False, 'error': error_msg}

        except Exception as e:
            logger.error(f"Erro ao criar instância: {e}")
            return {'success': False, 'error': str(e)}

    def _deletar_instancia_na_api(self, instance_name):
        """
        Deleta uma instância na Evolution API (método interno).
        """
        api_url = getattr(settings, 'EVOLUTION_API_URL', '')
        api_key = getattr(settings, 'EVOLUTION_API_KEY', '')

        try:
            response = requests.delete(
                f"{api_url.rstrip('/')}/instance/delete/{instance_name}",
                headers={'Content-Type': 'application/json', 'apikey': api_key},
                timeout=15
            )
            logger.info(f"Instância {instance_name} deletada: {response.status_code}")
            return response.status_code in [200, 404]  # 404 = já não existia
        except Exception as e:
            logger.error(f"Erro ao deletar instância: {e}")
            return False

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
        except requests.exceptions.HTTPError as e:
            # Tratamento específico para erro 403 (Forbidden)
            if e.response.status_code == 403:
                error_msg = (
                    f"Erro 403: Acesso negado pela Evolution API. "
                    f"Verifique se a EVOLUTION_API_KEY está correta no arquivo .env. "
                    f"API Key atual: {'***' + api_key[-4:] if len(api_key) > 4 else '(vazia)'}"
                )
                logger.error(error_msg)
                logger.error(f"URL tentada: {endpoint}")
                logger.error(f"Headers enviados: {{'Content-Type': 'application/json', 'apikey': '***'}}")
                result = {'success': False, 'error': error_msg}
            else:
                logger.error(f"Erro HTTP {e.response.status_code} na requisição Evolution API: {e}")
                result = {'success': False, 'error': str(e)}
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
            from empresas.models import WhatsAppInstance

            try:
                WhatsAppInstance.objects.update_or_create(
                    empresa=self.config.empresa,
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

            # Tentar extrair estado de conexão em diferentes formatos possíveis da API
            # Formato 1: {'instance': {'state': 'open'}}
            # Formato 2: {'state': 'open'}
            # Formato 3: {'connectionStatus': 'open'}
            connection_state = None
            instance_state = {}

            if isinstance(state_data, dict):
                instance_state = state_data.get('instance', {})
                if isinstance(instance_state, dict):
                    connection_state = instance_state.get('state')

                # Fallback para outros formatos
                if not connection_state:
                    connection_state = state_data.get('state')
                if not connection_state:
                    connection_state = state_data.get('connectionStatus')

            connection_state = connection_state or 'unknown'
            logger.info(f"Status de conexão obtido para {self.config.instance_name}: {connection_state}")

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
                profile_data = instance_state.get('profilePictureUrl', '') if isinstance(instance_state, dict) else ''
                self.config.foto_perfil_url = profile_data

                # Buscar número e nome do perfil
                self._buscar_dados_perfil()

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

            # Verificar em ambos os formatos possíveis da API:
            # Formato 1: {'name': 'instance_name', 'connectionStatus': '...'}
            # Formato 2: {'instance': {'instanceName': 'instance_name'}}
            instance_exists = any(
                isinstance(inst, dict)
                and (
                    inst.get('name') == self.config.instance_name
                    or inst.get('instance', {}).get('instanceName') == self.config.instance_name
                )
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

            # Se conectou, limpar QR Code e buscar dados do perfil
            if novo_status == 'conectado':
                self.config.qr_code = ''
                self._buscar_dados_perfil()

            self.config.save()

            return {'success': True, 'processed': True, 'type': 'connection_update'}

        # Nova mensagem recebida
        elif event_type in ['MESSAGES_UPSERT', 'NEW_MESSAGE']:
            message_data = payload.get('data', {})

            # Aqui você pode processar a mensagem recebida
            # Exemplo: criar registro no banco, responder automaticamente, etc.

            return {'success': True, 'processed': True, 'type': 'new_message'}

        return {'success': True, 'processed': False, 'type': 'unknown_event'}

    
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
