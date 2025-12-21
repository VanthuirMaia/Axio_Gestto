FROM nginx:alpine

# Remover configuração padrão
RUN rm /etc/nginx/conf.d/default.conf

# Copiar nossa configuração
COPY nginx.conf /etc/nginx/conf.d/

# Criar diretório para certificados SSL
RUN mkdir -p /etc/nginx/certs

# Gerar certificado SSL auto-assinado (para desenvolvimento)
# Em produção, use Let's Encrypt
RUN apk add --no-cache openssl && \
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout /etc/nginx/certs/key.pem \
    -out /etc/nginx/certs/cert.pem \
    -subj "/C=BR/ST=State/L=City/O=Organization/CN=localhost"

EXPOSE 80 443
