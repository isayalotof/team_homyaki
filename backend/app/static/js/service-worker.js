// Service Worker для PWA "Путешествуй по России"
const CACHE_NAME = 'travel-russia-v1';

// Ресурсы для предварительного кеширования
const PRECACHE_RESOURCES = [
  '/',
  '/static/css/main.css',
  '/static/css/responsive.css',
  '/static/js/main.js',
  '/static/js/components.js',
  '/static/js/api.js',
  '/offline', // Специальная страница для офлайн-режима
  '/static/images/logo.png'
];

// Установка Service Worker
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(async (cache) => {
        // Add each resource individually so that a single 404 does not abort the entire install
        for (const url of PRECACHE_RESOURCES) {
          try {
            await cache.add(url);
          } catch (err) {
            // Just log and continue – frequently happens in dev when an icon is missing
            console.warn('SW precache skip:', url, err);
          }
        }
      })
      .then(() => self.skipWaiting())
  );
});

// Активация Service Worker
self.addEventListener('activate', (event) => {
  // Очистить старые кеши при обновлении Service Worker
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.filter((cacheName) => {
          return cacheName !== CACHE_NAME;
        }).map((cacheName) => {
          return caches.delete(cacheName);
        })
      );
    }).then(() => {
      return self.clients.claim();
    })
  );
});

// Обработка запросов
self.addEventListener('fetch', (event) => {
  // Стратегия кеширования: сначала сеть, затем кеш
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        // Если запрос успешен, кешируем полученный результат
        if (event.request.method === 'GET' && response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return response;
      })
      .catch(() => {
        // Если запрос не удался, проверяем кеш
        return caches.match(event.request)
          .then((cachedResponse) => {
            // Если есть в кеше, возвращаем кешированный ответ
            if (cachedResponse) {
              return cachedResponse;
            }
            
            // Для HTML запросов, возвращаем офлайн-страницу
            if (event.request.headers.get('accept').includes('text/html')) {
              return caches.match('/offline');
            }
            
            // Для изображений возвращаем заглушку
            if (event.request.headers.get('accept').includes('image')) {
              return caches.match('/static/images/offline-image.jpg');
            }
            
            // Для остальных запросов возвращаем ошибку
            return new Response('Нет соединения с интернетом', {
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

// Синхронизация данных в фоне
self.addEventListener('sync', (event) => {
  if (event.tag === 'sync-reviews') {
    event.waitUntil(syncReviews());
  } else if (event.tag === 'sync-bookmarks') {
    event.waitUntil(syncBookmarks());
  }
});

// Пример функции для синхронизации отзывов в фоне
async function syncReviews() {
  try {
    const reviewsToSync = await getReviewsToSync();
    for (const review of reviewsToSync) {
      await sendReview(review);
    }
  } catch (error) {
    console.error('Ошибка синхронизации отзывов:', error);
  }
}

// Пример функции для синхронизации закладок
async function syncBookmarks() {
  try {
    const bookmarksToSync = await getBookmarksToSync();
    for (const bookmark of bookmarksToSync) {
      await sendBookmark(bookmark);
    }
  } catch (error) {
    console.error('Ошибка синхронизации закладок:', error);
  }
}

// Заглушки для функций работы с IndexedDB
async function getReviewsToSync() {
  // Код для получения данных из IndexedDB
  return [];
}

async function getBookmarksToSync() {
  // Код для получения данных из IndexedDB
  return [];
}

async function sendReview(review) {
  // Код для отправки отзыва на сервер
}

async function sendBookmark(bookmark) {
  // Код для отправки закладки на сервер
} 