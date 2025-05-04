self.addEventListener('install', event => {
  console.log('Service Worker instalado');
  self.skipWaiting();
});

self.addEventListener('fetch', event => {
  // Puedes añadir lógica de cache aquí si quieres modo offline
});
