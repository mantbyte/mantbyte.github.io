// mantbyte PWA Service Worker
// Handles caching for offline support and fast loading

const CACHE_NAME = 'mantbyte-v1';
const OFFLINE_URL = '/offline.html';

// Core assets to cache immediately on install
const PRECACHE_ASSETS = [
  '/',
  '/offline.html',
  '/assets/css/style.css',
  '/assets/js/main.js',
  '/assets/js/search.js',
  '/assets/images/favicon.svg',
  '/assets/icons/icon-192x192.png',
  '/assets/icons/icon-512x512.png',
  '/manifest.json'
];

// Install event — precache core assets
self.addEventListener('install', (event) => {
  console.log('[SW] Installing service worker...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('[SW] Precaching core assets');
      return cache.addAll(PRECACHE_ASSETS);
    })
  );
  // Activate immediately instead of waiting
  self.skipWaiting();
});

// Activate event — clean up old caches
self.addEventListener('activate', (event) => {
  console.log('[SW] Activating service worker...');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((name) => {
          if (name !== CACHE_NAME) {
            console.log('[SW] Deleting old cache:', name);
            return caches.delete(name);
          }
        })
      );
    })
  );
  // Take control of all pages immediately
  self.clients.claim();
});

// Fetch event — Network First strategy with cache fallback
self.addEventListener('fetch', (event) => {
  // Skip cross-origin requests (Firebase, Google Fonts, analytics, etc.)
  if (!event.request.url.startsWith(self.location.origin)) {
    return;
  }

  // Skip non-GET requests
  if (event.request.method !== 'GET') {
    return;
  }

  // For navigation requests (HTML pages)
  if (event.request.mode === 'navigate') {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          // Cache the fresh page
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        })
        .catch(() => {
          // Offline — try cache first, then show offline page
          return caches.match(event.request).then((cached) => {
            return cached || caches.match(OFFLINE_URL);
          });
        })
    );
    return;
  }

  // For static assets (CSS, JS, images) — Cache First with network fallback
  if (
    event.request.url.includes('/assets/') ||
    event.request.url.includes('/icons/')
  ) {
    event.respondWith(
      caches.match(event.request).then((cached) => {
        if (cached) {
          // Return cached version but also update cache in background
          fetch(event.request).then((response) => {
            caches.open(CACHE_NAME).then((cache) => cache.put(event.request, response));
          }).catch(() => {});
          return cached;
        }
        // Not in cache — fetch from network and cache
        return fetch(event.request).then((response) => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
          return response;
        });
      })
    );
    return;
  }

  // Default — Network first
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        const clone = response.clone();
        caches.open(CACHE_NAME).then((cache) => cache.put(event.request, clone));
        return response;
      })
      .catch(() => caches.match(event.request))
  );
});
