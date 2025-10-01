const CACHE_NAME = "networking-cache-v1";  // Mantén v1; cambia a v2 solo para actualizaciones futuras
const urlsToCache = [
  "/",  // Página principal (redirige a /index o /login)
  "/login",  // Para login offline
  "/index",  // Tu página principal post-login
  "/static/manifest.json",  // Corregido: Path Flask correcto (no root)
  "/static/icons/icon-192.png",  // Icono pequeño
  "/static/icons/icon-512.png",  // Icono grande
  "/static/icons/icon-144.png",  // Icono mediano (agregado para completitud)
  "/static/icons/favicon.ico",  // Favicon (opcional, pero recomendado)
  "https://fonts.googleapis.com/css2?family=Roboto+Mono&display=swap"  // Fuente externa (cacheada)
  // Opcionales: Agrega si tienes CSS/JS fijos, e.g., "/static/style.css"
];

// Instalar SW y cachear (con logs y errores)
self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME).then(cache => {
      console.log("Cacheando archivos para PWA...");
      return cache.addAll(urlsToCache);
    }).catch(error => {
      console.error("Error al cachear:", error);
    })
  );
  // self.skipWaiting();  // Descomenta para activar inmediatamente (opcional)
});

// Activar SW y limpiar viejos (con logs)
self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            console.log("Limpiando caché viejo:", cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
  // self.clients.claim();  // Descomenta para control inmediato (mejora UX, opcional)
});

// Interceptar fetch (con logs, non-GET ignore y fallback offline)
self.addEventListener("fetch", event => {
  if (event.request.method !== "GET") {
    return;  // Optimiza: Ignora POST/PUT (e.g., subida chat)
  }

  event.respondWith(
    caches.match(event.request).then(response => {
      if (response) {
        console.log("Servido desde caché:", event.request.url);
        return response;
      }
      return fetch(event.request).catch(error => {
        console.error("Error en red, usando caché:", error);
        // Fallback para documentos (HTML) offline: Muestra /index como backup
        if (event.request.destination === 'document' && !response) {
          return caches.match('/index') || caches.match('/');  // Prioriza /index
        }
      });
    })
  );
});
