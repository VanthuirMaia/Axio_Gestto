// Service Worker para Gestto PWA
const CACHE_NAME = 'gestto-v1';
const OFFLINE_URL = '/offline/';

// Arquivos essenciais para cache inicial
const STATIC_CACHE_URLS = [
  '/',
  '/static/css/custom.css',
  '/static/js/sidebar.js',
  '/static/manifest.json',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
  'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.css'
];

// Instalação do Service Worker
self.addEventListener('install', (event) => {
  console.log('[Service Worker] Instalando...');

  event.waitUntil(
    caches.open(CACHE_NAME)
      .then((cache) => {
        console.log('[Service Worker] Cache aberto');
        return cache.addAll(STATIC_CACHE_URLS);
      })
      .catch((err) => {
        console.error('[Service Worker] Erro ao cachear arquivos:', err);
      })
  );

  // Ativa imediatamente o novo service worker
  self.skipWaiting();
});

// Ativação do Service Worker
self.addEventListener('activate', (event) => {
  console.log('[Service Worker] Ativando...');

  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('[Service Worker] Removendo cache antigo:', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );

  // Assume controle imediato de todas as páginas
  return self.clients.claim();
});

// Estratégia de cache: Network First, fallback to Cache
self.addEventListener('fetch', (event) => {
  // Ignora requisições não-GET
  if (event.request.method !== 'GET') return;

  // Ignora requisições do Django Admin
  if (event.request.url.includes('/admin/')) return;

  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Se a resposta for válida, clona e salva no cache
        if (response && response.status === 200) {
          const responseClone = response.clone();

          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }

        return response;
      })
      .catch(() => {
        // Se falhar (offline), tenta buscar do cache
        return caches.match(event.request)
          .then((cachedResponse) => {
            if (cachedResponse) {
              return cachedResponse;
            }

            // Se for navegação e não tiver cache, mostra página offline
            if (event.request.mode === 'navigate') {
              return caches.match(OFFLINE_URL);
            }

            return new Response('Offline - Recurso não disponível', {
              status: 503,
              statusText: 'Service Unavailable',
              headers: new Headers({
                'Content-Type': 'text/plain'
              })
            });
          });
      })
  );
});

// Listener para mensagens (útil para forçar atualização)
self.addEventListener('message', (event) => {
  if (event.data && event.data.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
