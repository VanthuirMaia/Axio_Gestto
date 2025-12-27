#!/bin/bash

###############################################################################
# Script de Setup Inicial do Servidor - Gestto
# Executa no VPS Hostinger para preparar ambiente de produção
###############################################################################

set -e

# Cores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════╗"
echo "║   SETUP INICIAL - GESTTO PRODUÇÃO         ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

# Verificar se está rodando no Ubuntu
if ! grep -q "Ubuntu" /etc/os-release 2>/dev/null; then
    echo -e "${RED}❌ Este script é para Ubuntu. Sistema não suportado.${NC}"
    exit 1
fi

echo -e "${YELLOW}[1/6] Atualizando sistema...${NC}"
sudo apt update -qq
sudo apt upgrade -y -qq
echo -e "${GREEN}✓ Sistema atualizado${NC}"

echo -e "${YELLOW}[2/6] Instalando dependências...${NC}"
sudo apt install -y git curl wget build-essential ca-certificates gnupg lsb-release
echo -e "${GREEN}✓ Dependências instaladas${NC}"

echo -e "${YELLOW}[3/6] Instalando Docker...${NC}"
if ! command -v docker &> /dev/null; then
    # Remover versões antigas
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

    # Adicionar repositório Docker
    sudo mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

    sudo apt update -qq
    sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

    # Adicionar usuário ao grupo docker
    sudo usermod -aG docker $USER

    echo -e "${GREEN}✓ Docker instalado: $(docker --version)${NC}"
else
    echo -e "${GREEN}✓ Docker já instalado: $(docker --version)${NC}"
fi

echo -e "${YELLOW}[4/6] Instalando Docker Compose...${NC}"
if ! command -v docker-compose &> /dev/null; then
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.24.5/docker-compose-$(uname -s)-$(uname -m)" \
      -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo -e "${GREEN}✓ Docker Compose instalado: $(docker-compose --version)${NC}"
else
    echo -e "${GREEN}✓ Docker Compose já instalado: $(docker-compose --version)${NC}"
fi

echo -e "${YELLOW}[5/6] Criando estrutura de diretórios...${NC}"
sudo mkdir -p /var/www/gestto
sudo chown -R $USER:$USER /var/www/gestto
echo -e "${GREEN}✓ Diretório /var/www/gestto criado${NC}"

echo -e "${YELLOW}[6/6] Configurando firewall (UFW)...${NC}"
if command -v ufw &> /dev/null; then
    sudo ufw --force enable
    sudo ufw allow 22/tcp    # SSH
    sudo ufw allow 80/tcp    # HTTP
    sudo ufw allow 443/tcp   # HTTPS
    sudo ufw status
    echo -e "${GREEN}✓ Firewall configurado${NC}"
else
    echo -e "${YELLOW}⚠️  UFW não instalado. Pule esta etapa.${NC}"
fi

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════╗"
echo "║        SETUP CONCLUÍDO COM SUCESSO!       ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

echo ""
echo -e "${YELLOW}Próximos passos:${NC}"
echo ""
echo "1. IMPORTANTE: Faça logout e login novamente para aplicar permissões do Docker:"
echo "   ${GREEN}exit${NC}"
echo ""
echo "2. Após reconectar, clone o repositório:"
echo "   ${GREEN}cd /var/www/gestto${NC}"
echo "   ${GREEN}git clone https://github.com/SEU_USUARIO/axio_gestto.git .${NC}"
echo ""
echo "3. Crie o arquivo .env.production:"
echo "   ${GREEN}nano /var/www/gestto/.env.production${NC}"
echo ""
echo "4. Suba a aplicação:"
echo "   ${GREEN}cd /var/www/gestto${NC}"
echo "   ${GREEN}docker-compose -f docker-compose.prod.yml build${NC}"
echo "   ${GREEN}docker-compose -f docker-compose.prod.yml up -d${NC}"
echo ""
echo "5. Verifique os logs:"
echo "   ${GREEN}docker-compose -f docker-compose.prod.yml logs -f${NC}"
echo ""
echo -e "${GREEN}Consulte SETUP_RAPIDO.md para instruções detalhadas.${NC}"
echo ""
