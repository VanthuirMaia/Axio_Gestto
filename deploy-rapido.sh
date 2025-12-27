#!/bin/bash

###############################################################################
# DEPLOY RÁPIDO - GESTTO PRODUÇÃO
# Resolve o problema do DATABASE_URL e sobe a aplicação
###############################################################################

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}"
echo "╔════════════════════════════════════════════╗"
echo "║   DEPLOY GESTTO - CONFIGURAÇÃO RÁPIDA     ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"

echo -e "${YELLOW}[1/5] Criando database gestto_db no PostgreSQL...${NC}"
sudo -u postgres psql -c "CREATE DATABASE gestto_db;" 2>/dev/null || echo "Database já existe"
sudo -u postgres psql -c "CREATE USER gestto_user WITH PASSWORD 'Gestto@2025!Secure';" 2>/dev/null || echo "User já existe"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE gestto_db TO gestto_user;"
sudo -u postgres psql -c "ALTER DATABASE gestto_db OWNER TO gestto_user;"
echo -e "${GREEN}✓ Database configurado${NC}"

echo -e "${YELLOW}[2/5] Verificando arquivo .env.production...${NC}"
if grep -q "^DATABASE_URL=" /var/www/gestto/.env.production 2>/dev/null; then
    echo -e "${RED}⚠️  DATABASE_URL ainda está ativo! Editando...${NC}"
    sed -i 's/^DATABASE_URL=/#DATABASE_URL=/' /var/www/gestto/.env.production
    echo -e "${GREEN}✓ DATABASE_URL comentado${NC}"
else
    echo -e "${GREEN}✓ .env.production OK${NC}"
fi

echo -e "${YELLOW}[3/5] Fazendo pull do repositório...${NC}"
cd /var/www/gestto
git pull origin main
echo -e "${GREEN}✓ Código atualizado${NC}"

echo -e "${YELLOW}[4/5] Buildando imagem Docker...${NC}"
docker build -t gestto-app:latest .
echo -e "${GREEN}✓ Imagem buildada${NC}"

echo -e "${YELLOW}[5/5] Fazendo deploy no Docker Swarm...${NC}"
# Exportar variáveis do .env.production de forma segura (protegendo caracteres especiais)
while IFS='=' read -r key value; do
    # Só exportar se a linha começar com letra/número (não com # ou espaço)
    if [[ "$key" =~ ^[A-Za-z0-9_] ]]; then
        # Remover aspas se houver
        value="${value%\"}"
        value="${value#\"}"
        export "$key=$value"
    fi
done < /var/www/gestto/.env.production

docker stack deploy -c /var/www/gestto/gestto-stack.yaml gestto
echo -e "${GREEN}✓ Stack deployed${NC}"

echo ""
echo -e "${GREEN}Aguardando 30 segundos para os containers iniciarem...${NC}"
sleep 30

echo ""
echo -e "${YELLOW}Status dos serviços:${NC}"
docker stack services gestto

echo ""
echo -e "${YELLOW}Logs do Django (últimas 50 linhas):${NC}"
docker service logs gestto_gestto_web --tail 50

echo ""
echo -e "${GREEN}"
echo "╔════════════════════════════════════════════╗"
echo "║        DEPLOY CONCLUÍDO!                  ║"
echo "╚════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo "Acesse: https://www.gestto.app.br"
echo ""
