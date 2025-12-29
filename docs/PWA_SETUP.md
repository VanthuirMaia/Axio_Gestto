# PWA - Progressive Web App - Gestto

## O que foi implementado

O Gestto agora é um **Progressive Web App (PWA)**, permitindo que usuários instalem o sistema como um aplicativo nativo em dispositivos móveis e desktops.

### Recursos PWA Implementados

✅ **Instalável**: Pode ser adicionado à tela inicial do celular/desktop
✅ **Funcionalidade Offline**: Service worker com cache inteligente
✅ **Atualização Automática**: Nova versão detectada e aplicada automaticamente
✅ **Página Offline**: Interface amigável quando sem conexão
✅ **Atalhos Rápidos**: Acesso direto a criar agendamento e calendário
✅ **Theme Color**: Barra de status personalizada no mobile

---

## Arquivos Criados/Modificados

### Novos Arquivos

```
static/
├── manifest.json              # Configuração do PWA
├── service-worker.js          # Cache e funcionalidade offline
├── js/pwa-register.js         # Registro do service worker
└── icons/                     # Pasta para ícones PWA
    ├── README.md              # Instruções para criar ícones
    └── icon-temp.svg          # Ícone temporário

templates/
└── offline.html               # Página exibida quando offline
```

### Arquivos Modificados

```
templates/base.html            # Adicionadas meta tags PWA e links
config/urls.py                 # Adicionadas rotas para service worker
core/views.py                  # Adicionadas views do PWA
```

---

## Como Testar o PWA

### Pré-requisitos

1. **HTTPS obrigatório**: PWA só funciona com HTTPS (ou localhost em desenvolvimento)
2. **Navegador compatível**: Chrome, Edge, Safari 11.1+, Firefox

### Passos para Testar

#### 1. **Preparar os Ícones (IMPORTANTE)**

Antes de testar, você precisa criar os ícones PWA:

**Opção Rápida** (recomendada):
1. Acesse https://www.pwabuilder.com/imageGenerator
2. Faça upload de uma imagem 512x512 com o logo "GESTTO"
3. Baixe o ZIP e extraia em `static/icons/`

**Ou use o ícone temporário**:
```bash
# Converter o SVG temporário para PNG (use algum conversor online)
# Copie para static/icons/ nos tamanhos necessários
```

#### 2. **Coletar Arquivos Estáticos**

```bash
python manage.py collectstatic --noinput
```

#### 3. **Executar o Servidor**

**Desenvolvimento Local (HTTP funciona)**:
```bash
python manage.py runserver
```

**Produção (HTTPS obrigatório)**:
- Configure HTTPS no servidor
- Ou use ngrok para teste: `ngrok http 8000`

#### 4. **Testar Instalação**

##### No Desktop (Chrome/Edge):

1. Abra o sistema no navegador
2. Procure o ícone de instalação na barra de endereço (➕ ou ⬇️)
3. Clique em "Instalar" ou use: Menu > Instalar Gestto
4. O app abrirá em janela separada

##### No Android:

1. Abra o sistema no Chrome
2. Toque no menu (⋮) > "Instalar app" ou "Adicionar à tela inicial"
3. Confirme a instalação
4. Ícone aparecerá na tela inicial

##### No iOS (Safari):

1. Abra o sistema no Safari
2. Toque no botão "Compartilhar" (quadrado com seta)
3. Escolha "Adicionar à Tela de Início"
4. Confirme e dê um nome

#### 5. **Verificar Service Worker**

1. Abra DevTools (F12)
2. Vá para a aba **Application**
3. Em **Service Workers**, verifique se está registrado
4. Em **Manifest**, veja as configurações do PWA
5. Em **Cache Storage**, veja os arquivos cacheados

---

## Testar Funcionalidades

### Teste 1: Instalação
- [ ] Botão de instalação aparece
- [ ] App instala corretamente
- [ ] Ícone aparece na tela inicial
- [ ] App abre em janela standalone (sem barra de endereço)

### Teste 2: Offline
- [ ] Desconecte a internet
- [ ] Navegue entre páginas já visitadas
- [ ] Tente acessar página não visitada = mostra página offline
- [ ] Reconecte = volta ao normal

### Teste 3: Cache
- [ ] Abra o app
- [ ] Feche o app
- [ ] Desconecte a internet
- [ ] Abra o app novamente = deve carregar do cache

### Teste 4: Atualização
- [ ] Faça uma mudança no código
- [ ] Deploy da nova versão
- [ ] App detecta e pede para atualizar
- [ ] Atualização acontece automaticamente

### Teste 5: Atalhos (Android)
- [ ] Pressione e segure o ícone do app
- [ ] Aparecem atalhos: "Novo Agendamento" e "Calendário"
- [ ] Atalhos levam às páginas corretas

---

## Troubleshooting

### Problema: PWA não instala

**Solução**:
1. Verifique se está usando HTTPS (ou localhost)
2. Confirme que `manifest.json` está acessível: `/static/manifest.json`
3. Verifique ícones estão presentes (mínimo: 192x192 e 512x512)
4. Veja o console do navegador para erros

### Problema: Service Worker não registra

**Solução**:
1. Abra DevTools > Application > Service Workers
2. Marque "Update on reload"
3. Force atualização: Ctrl+Shift+R
4. Verifique `/service-worker.js` está acessível

### Problema: Página offline não aparece

**Solução**:
1. Verifique se visitou páginas antes de ficar offline
2. Service worker precisa cachear as páginas primeiro
3. Limpe cache e registre novamente

### Problema: Ícones não aparecem

**Solução**:
1. Crie os ícones conforme `static/icons/README.md`
2. Tamanhos mínimos obrigatórios: 192x192 e 512x512
3. Rode `python manage.py collectstatic`
4. Limpe cache do navegador

---

## Próximos Passos (Opcional)

### Melhorias Futuras

1. **Notificações Push**
   - Avisar cliente 1h antes do agendamento
   - Lembrar profissional de atendimentos do dia

2. **Sincronização em Background**
   - Enviar agendamentos criados offline quando reconectar
   - Background sync para dados importantes

3. **Modo Offline Completo**
   - Permitir criar agendamentos offline
   - Sincronizar quando voltar online

4. **Shortcuts Dinâmicos**
   - "Último cliente atendido"
   - "Próximo agendamento"

5. **Share Target**
   - Compartilhar contatos direto para o app

---

## Configurações de Produção

### HTTPS Obrigatório

No servidor de produção, certifique-se de ter HTTPS configurado:

```python
# settings.py (produção)
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
```

### Headers de Segurança

```python
# settings.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

### Nginx (se usar)

```nginx
# Configurar cache para manifest e service worker
location /service-worker.js {
    add_header Cache-Control "no-cache, no-store, must-revalidate";
    add_header Service-Worker-Allowed "/";
}

location /static/manifest.json {
    add_header Cache-Control "public, max-age=0";
}
```

---

## Recursos e Referências

- [Web.dev - PWA](https://web.dev/progressive-web-apps/)
- [PWA Builder](https://www.pwabuilder.com/)
- [MDN - Service Workers](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Gerador de Ícones PWA](https://realfavicongenerator.net/)

---

## Suporte

- **Desktop**: Chrome 73+, Edge 79+, Safari 14+, Firefox 90+ (limitado)
- **Android**: Chrome 40+, Samsung Internet 4+
- **iOS**: Safari 11.3+ (funcionalidade limitada)

**Limitações iOS**:
- Sem notificações push (ainda)
- Service worker limitado
- Funcionalidades offline básicas

**Limitações Gerais**:
- Sem acesso a recursos nativos profundos (Bluetooth, NFC, sensores avançados)
- Não pode ser distribuído via App Store/Play Store (mas não precisa!)
