#!/bin/bash
# Script para configurar n8n em produção

echo "================================================"
echo "CONFIGURAÇÃO N8N - AXIO GESTTO"
echo "================================================"
echo ""
echo "Cole a URL do webhook do n8n abaixo:"
echo "(Exemplo: https://n8n.axiodev.cloud/webhook/abc123...)"
read -p "URL do Webhook: " N8N_WEBHOOK_URL

# Validar URL
if [[ ! $N8N_WEBHOOK_URL =~ ^https:// ]]; then
    echo "❌ Erro: URL deve começar com https://"
    exit 1
fi

# Atualizar .env
if grep -q "N8N_WEBHOOK_URL=" .env; then
    # Substituir linha existente
    sed -i "s|N8N_WEBHOOK_URL=.*|N8N_WEBHOOK_URL=$N8N_WEBHOOK_URL|" .env
    echo "✅ N8N_WEBHOOK_URL atualizado no .env"
else
    # Adicionar nova linha
    echo "N8N_WEBHOOK_URL=$N8N_WEBHOOK_URL" >> .env
    echo "✅ N8N_WEBHOOK_URL adicionado ao .env"
fi

echo ""
echo "================================================"
echo "✅ CONFIGURAÇÃO CONCLUÍDA!"
echo "================================================"
echo ""
echo "Próximos passos:"
echo "1. Fazer commit das mudanças: git add . && git commit"
echo "2. Fazer push: git push origin develop"
echo "3. Em produção, reiniciar o Django"
echo ""
echo "Testando conexão com n8n..."
curl -s -o /dev/null -w "%{http_code}" "$N8N_WEBHOOK_URL" | {
    read STATUS
    if [ "$STATUS" = "404" ] || [ "$STATUS" = "405" ]; then
        echo "✅ n8n está acessível (status $STATUS é esperado sem payload)"
    else
        echo "⚠️  n8n retornou status $STATUS (verifique se o workflow está ativo)"
    fi
}
