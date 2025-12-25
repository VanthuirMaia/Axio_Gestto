#!/bin/bash

###############################################################################
# Script de Deploy Automatizado - Axio Gestto
# Para Ubuntu Server (VPS Hostinger)
###############################################################################

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║     AXIO GESTTO - DEPLOY AUTOMATIZADO                ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se está rodando como root ou com sudo
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}Por favor, execute com sudo: sudo bash deploy.sh${NC}"
    exit 1
fi

###############################################################################
# PASSO 1: Verificar sistema operacional
###############################################################################
echo -e "${YELLOW}[1/10] Verificando sistema operacional...${NC}"
if ! command -v lsb_release &> /dev/null; then
    echo -e "${RED}Este script é para Ubuntu. Sistema não identificado.${NC}"
    exit 1
fi

OS_NAME=$(lsb_release -si)
if [ "$OS_NAME" != "Ubuntu" ]; then
    echo -e "${RED}Este script é otimizado para Ubuntu. Detectado: $OS_NAME${NC}"
    read -p "Deseja continuar mesmo assim? (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
fi
echo -e "${GREEN}✓ Sistema: $OS_NAME $(lsb_release -sr)${NC}"

###############################################################################
# PASSO 2: Atualizar sistema
###############################################################################
echo -e "${YELLOW}[2/10] Atualizando sistema...${NC}"
apt update -qq
apt upgrade -y -qq
echo -e "${GREEN}✓ Sistema atualizado${NC}"

###############################################################################
# PASSO 3: Instalar Docker
###############################################################################
echo -e "${YELLOW}[3/10] Verificando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    echo "Docker não encontrado. Instalando..."

    # Remover versões antigas
    apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    # Instalar dependências
    apt install -y apt-transport-https ca-certificates curl software-properties-common gnupg lsb-release

    # Adicionar chave GPG
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    # Adicionar repositório
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null

    # Instalar Docker
    apt update -qq
    apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Iniciar Docker
    systemctl enable docker
    systemctl start docker

    echo -e "${GREEN}✓ Docker instalado: $(docker --version)${NC}"
else
    echo -e "${GREEN}✓ Docker já instalado: $(docker --version)${NC}"
fi

###############################################################################
# PASSO 4: Instalar Docker Compose
###############################################################################
echo -e "${YELLOW}[4/10] Verificando Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    echo "Docker Compose não encontrado. Instalando..."

    DOCKER_COMPOSE_VERSION="v2.24.5"
    curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose

    echo -e "${GREEN}✓ Docker Compose instalado: $(docker-compose --version)${NC}"
else
    echo -e "${GREEN}✓ Docker Compose já instalado: $(docker-compose --version)${NC}"
fi

###############################################################################
# PASSO 5: Verificar arquivo .env
###############################################################################
echo -e "${YELLOW}[5/10] Verificando arquivo .env...${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}Arquivo .env não encontrado!${NC}"
    echo "Criando .env de exemplo..."

    cat > .env << 'EOL'
# DJANGO CORE
SECRET_KEY=TROCAR_ESTE_VALOR_POR_TOKEN_SEGURO_50_CARACTERES
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,SEU_DOMINIO_AQUI

# DATABASE
DB_ENGINE=django.db.backends.postgresql
DB_NAME=gestao_negocios
DB_USER=postgres
DB_PASSWORD=TROCAR_SENHA_POSTGRES_FORTE
DB_HOST=db
DB_PORT=5432

# EMAIL (SMTP)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=senha-app-gmail
DEFAULT_FROM_EMAIL=noreply@seudominio.com

# REDIS & CELERY
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# N8N INTEGRATION
N8N_API_KEY=TROCAR_ESTE_VALOR_POR_TOKEN_32_CARACTERES

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000

# SUPERUSER
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@seudominio.com
DJANGO_SUPERUSER_PASSWORD=TROCAR_SENHA_ADMIN_FORTE
EOL

    echo -e "${YELLOW}✓ Arquivo .env criado. EDITE-O ANTES DE CONTINUAR!${NC}"
    echo ""
    echo "Execute para gerar tokens seguros:"
    echo "  python3 -c \"import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(50))\""
    echo "  python3 -c \"import secrets; print('N8N_API_KEY=' + secrets.token_urlsafe(32))\""
    echo ""
    read -p "Pressione ENTER após editar o .env..."
fi

# Verificar se ainda tem valores padrão
if grep -q "TROCAR_" .env; then
    echo -e "${RED}ATENÇÃO: Arquivo .env contém valores padrão não seguros!${NC}"
    echo "Por favor, edite o .env e troque todos os valores 'TROCAR_*'"
    read -p "Deseja continuar mesmo assim? (NÃO recomendado) (s/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Ss]$ ]]; then
        exit 1
    fi
else
    echo -e "${GREEN}✓ Arquivo .env configurado${NC}"
fi

###############################################################################
# PASSO 6: Verificar certificados SSL
###############################################################################
echo -e "${YELLOW}[6/10] Verificando certificados SSL...${NC}"
if [ ! -d "nginx/certs" ]; then
    mkdir -p nginx/certs
fi

if [ ! -f "nginx/certs/cert.pem" ] || [ ! -f "nginx/certs/key.pem" ]; then
    echo "Certificados SSL não encontrados."
    read -p "Deseja gerar certificados self-signed para teste? (s/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Ss]$ ]]; then
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout nginx/certs/key.pem \
            -out nginx/certs/cert.pem \
            -subj "/C=BR/ST=State/L=City/O=AxioGestto/CN=localhost"

        echo -e "${YELLOW}✓ Certificados self-signed gerados (APENAS PARA TESTE)${NC}"
        echo -e "${YELLOW}Para produção, use Let's Encrypt (veja DEPLOY_GUIDE.md)${NC}"
    else
        echo -e "${RED}AVISO: Nginx pode falhar sem certificados SSL${NC}"
    fi
else
    echo -e "${GREEN}✓ Certificados SSL encontrados${NC}"
fi

###############################################################################
# PASSO 7: Parar containers antigos (se existirem)
###############################################################################
echo -e "${YELLOW}[7/10] Parando containers antigos...${NC}"
if docker-compose ps | grep -q "Up"; then
    docker-compose down
    echo -e "${GREEN}✓ Containers antigos parados${NC}"
else
    echo -e "${GREEN}✓ Nenhum container rodando${NC}"
fi

###############################################################################
# PASSO 8: Build das imagens Docker
###############################################################################
echo -e "${YELLOW}[8/10] Construindo imagens Docker...${NC}"
docker-compose build --no-cache
echo -e "${GREEN}✓ Imagens construídas${NC}"

###############################################################################
# PASSO 9: Iniciar containers
###############################################################################
echo -e "${YELLOW}[9/10] Iniciando containers...${NC}"
docker-compose up -d

# Aguardar containers ficarem healthy
echo "Aguardando containers iniciarem..."
sleep 10

# Verificar status
CONTAINERS_UP=$(docker-compose ps | grep "Up" | wc -l)
if [ "$CONTAINERS_UP" -ge 5 ]; then
    echo -e "${GREEN}✓ $CONTAINERS_UP containers iniciados${NC}"
else
    echo -e "${RED}AVISO: Apenas $CONTAINERS_UP containers iniciaram. Esperado: 5+${NC}"
    echo "Execute 'docker-compose logs' para investigar"
fi

###############################################################################
# PASSO 10: Executar migrações e collectstatic
###############################################################################
echo -e "${YELLOW}[10/10] Executando migrações e collectstatic...${NC}"

# Aguardar DB ficar disponível
echo "Aguardando banco de dados..."
sleep 5

# Migrações
docker-compose exec -T web python manage.py migrate --noinput
echo -e "${GREEN}✓ Migrações aplicadas${NC}"

# Collectstatic
docker-compose exec -T web python manage.py collectstatic --noinput
echo -e "${GREEN}✓ Arquivos estáticos coletados${NC}"

# Tentar criar superuser (pode falhar se já existir)
echo "Criando superuser..."
docker-compose exec -T web python manage.py createsuperuser --noinput 2>/dev/null || echo "Superuser já existe"

###############################################################################
# FINALIZAÇÃO
###############################################################################
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════╗"
echo "║             DEPLOY CONCLUÍDO COM SUCESSO!            ║"
echo "╚═══════════════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo "Status dos containers:"
docker-compose ps
echo ""

# Obter IP do servidor
SERVER_IP=$(hostname -I | awk '{print $1}')
echo -e "${GREEN}Acessos disponíveis:${NC}"
echo "  Health Check: http://$SERVER_IP/health/"
echo "  Admin Django: https://$SERVER_IP/admin/"
echo "  Dashboard:    https://$SERVER_IP/"
echo ""

echo -e "${YELLOW}Próximos passos:${NC}"
echo "1. Testar acesso: curl http://$SERVER_IP/health/"
echo "2. Acessar admin Django e configurar:"
echo "   - Criar primeira Empresa"
echo "   - Adicionar Serviços e Profissionais"
echo "   - Configurar Horários de Funcionamento"
echo "3. Configurar n8n com as APIs:"
echo "   - POST https://$SERVER_IP/api/bot/processar/"
echo "   - GET  https://$SERVER_IP/api/n8n/servicos/"
echo "   - Header: X-API-Key (valor do .env)"
echo ""

echo -e "${YELLOW}Comandos úteis:${NC}"
echo "  Ver logs:        docker-compose logs -f"
echo "  Reiniciar:       docker-compose restart"
echo "  Parar tudo:      docker-compose down"
echo "  Status:          docker-compose ps"
echo ""

echo -e "${GREEN}Consulte o arquivo DEPLOY_GUIDE.md para mais detalhes.${NC}"
echo ""
