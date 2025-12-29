// Registro do Service Worker para PWA
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker
      .register('/service-worker.js')
      .then((registration) => {
        console.log('✅ Service Worker registrado com sucesso:', registration.scope);

        // Verifica atualizações a cada 60 segundos
        setInterval(() => {
          registration.update();
        }, 60000);

        // Detecta quando há uma nova versão disponível
        registration.addEventListener('updatefound', () => {
          const newWorker = registration.installing;

          newWorker.addEventListener('statechange', () => {
            if (newWorker.state === 'installed' && navigator.serviceWorker.controller) {
              // Nova versão disponível
              console.log('🔄 Nova versão disponível!');

              // Você pode mostrar um toast/notificação aqui
              if (confirm('Nova versão disponível! Deseja atualizar agora?')) {
                newWorker.postMessage({ type: 'SKIP_WAITING' });
                window.location.reload();
              }
            }
          });
        });
      })
      .catch((error) => {
        console.error('❌ Erro ao registrar Service Worker:', error);
      });

    // Recarrega a página quando o service worker assumir controle
    let refreshing = false;
    navigator.serviceWorker.addEventListener('controllerchange', () => {
      if (!refreshing) {
        refreshing = true;
        window.location.reload();
      }
    });
  });
}

// Detecta se o app foi instalado
window.addEventListener('appinstalled', (event) => {
  console.log('✅ PWA instalado com sucesso!');
});

// Prompt de instalação (opcional - para botão personalizado)
let deferredPrompt;

window.addEventListener('beforeinstallprompt', (event) => {
  // Previne o prompt automático
  event.preventDefault();

  // Salva o evento para usar depois
  deferredPrompt = event;

  console.log('💡 PWA pode ser instalado');

  // Você pode mostrar um botão de instalação customizado aqui
  // Exemplo: document.getElementById('install-button').style.display = 'block';
});

// Função para disparar instalação (chame via botão se quiser)
function installPWA() {
  if (deferredPrompt) {
    deferredPrompt.prompt();

    deferredPrompt.userChoice.then((choiceResult) => {
      if (choiceResult.outcome === 'accepted') {
        console.log('✅ Usuário aceitou instalar o PWA');
      } else {
        console.log('❌ Usuário recusou instalar o PWA');
      }
      deferredPrompt = null;
    });
  }
}

// Detecta se está rodando como PWA instalado
function isRunningAsPWA() {
  return window.matchMedia('(display-mode: standalone)').matches ||
         window.navigator.standalone === true;
}

if (isRunningAsPWA()) {
  console.log('📱 Rodando como PWA instalado');
}
