#!/bin/bash

###############################################################################
# Script de Diagnóstico VPS - Mapear infraestrutura existente
# Execute no servidor para descobrir configuração atual
###############################################################################

echo "════════════════════════════════════════════════════════"
echo "  DIAGNÓSTICO VPS - Mapeamento de Infraestrutura"
echo "════════════════════════════════════════════════════════"
echo ""

echo "📦 [1/8] CONTAINERS DOCKER RODANDO"
echo "────────────────────────────────────────────────────────"
docker ps --format "table {{.Names}}\t{{.Image}}\t{{.Ports}}\t{{.Status}}"
echo ""

echo "🌐 [2/8] REDES DOCKER"
echo "────────────────────────────────────────────────────────"
docker network ls
echo ""

echo "🔌 [3/8] PORTAS EM USO (80, 443, 5432, 6379, etc)"
echo "────────────────────────────────────────────────────────"
sudo netstat -tulpn | grep -E ':(80|443|5432|6379|8080|8081|9000|3000|5000|8000)' || echo "Nenhuma porta mapeada encontrada"
echo ""

echo "📂 [4/8] VOLUMES DOCKER"
echo "────────────────────────────────────────────────────────"
docker volume ls | head -20
echo ""

echo "🗂️ [5/8] ESTRUTURA DE DIRETÓRIOS /var/www e /opt"
echo "────────────────────────────────────────────────────────"
ls -la /var/www/ 2>/dev/null || echo "/var/www não existe"
echo ""
ls -la /opt/ 2>/dev/null | grep -v "^total" | head -10 || echo "/opt vazio"
echo ""

echo "🔍 [6/8] VERIFICAR NGINX/PROXY REVERSO"
echo "────────────────────────────────────────────────────────"
if docker ps | grep -i "nginx-proxy\|nginx_proxy\|nginxproxymanager\|npm"; then
    echo "✅ Nginx Proxy Manager detectado!"
    docker ps | grep -i "nginx" --color=never
elif docker ps | grep -i "traefik"; then
    echo "✅ Traefik detectado!"
    docker ps | grep -i "traefik" --color=never
elif docker ps | grep -i "caddy"; then
    echo "✅ Caddy detectado!"
    docker ps | grep -i "caddy" --color=never
elif systemctl status nginx >/dev/null 2>&1; then
    echo "✅ Nginx instalado como serviço (não Docker)"
else
    echo "⚠️  Nenhum proxy reverso detectado"
fi
echo ""

echo "🗄️ [7/8] VERIFICAR REDIS"
echo "────────────────────────────────────────────────────────"
REDIS_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i redis | head -1)
if [ -n "$REDIS_CONTAINER" ]; then
    echo "✅ Container Redis encontrado: $REDIS_CONTAINER"
    echo "Testando conexão..."
    docker exec $REDIS_CONTAINER redis-cli ping 2>/dev/null && echo "✅ Redis respondendo" || echo "⚠️  Redis não responde"
    echo ""
    echo "Databases em uso:"
    docker exec $REDIS_CONTAINER redis-cli INFO keyspace 2>/dev/null || echo "Sem databases em uso"
else
    echo "⚠️  Container Redis não encontrado"
fi
echo ""

echo "🐘 [8/8] VERIFICAR POSTGRESQL"
echo "────────────────────────────────────────────────────────"
PG_CONTAINER=$(docker ps --format '{{.Names}}' | grep -i postgres | head -1)
if [ -n "$PG_CONTAINER" ]; then
    echo "✅ Container PostgreSQL encontrado: $PG_CONTAINER"
    echo "Testando conexão..."
    docker exec $PG_CONTAINER pg_isready 2>/dev/null && echo "✅ PostgreSQL respondendo" || echo "⚠️  PostgreSQL não responde"
    echo ""
    echo "Porta exposta:"
    docker port $PG_CONTAINER 2>/dev/null || echo "Porta não mapeada"
else
    echo "⚠️  Container PostgreSQL não encontrado"
fi
echo ""

echo "════════════════════════════════════════════════════════"
echo "  DIAGNÓSTICO CONCLUÍDO!"
echo "════════════════════════════════════════════════════════"
echo ""
echo "📋 RESUMO PARA ANÁLISE:"
echo ""
echo "Copie TODA a saída acima e cole para o Claude Code"
echo "para que possamos configurar o Gestto sem conflitos."
echo ""
