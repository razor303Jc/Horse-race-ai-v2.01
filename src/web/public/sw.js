// Service Worker for caching and offline functionality
const CACHE_NAME = "horse-racing-ai-v2.03";
const API_CACHE_NAME = "horse-racing-api-cache";
const STATIC_CACHE_NAME = "horse-racing-static-cache";

// Cache versioning
const CACHE_VERSION = "1.0.0";
const FULL_CACHE_NAME = `${CACHE_NAME}-${CACHE_VERSION}`;

// URLs to cache for offline functionality
const STATIC_ASSETS = [
  "/",
  "/static/js/bundle.js",
  "/static/css/main.css",
  "/manifest.json",
  "/favicon.ico",
];

// API endpoints to cache
const API_ENDPOINTS = [
  "/api/daily_races",
  "/api/real_race_cards",
  "/api/stage8/performance",
  "/api/betting/recommendations",
];

// Cache strategies
const CACHE_STRATEGIES = {
  CACHE_FIRST: "cache-first",
  NETWORK_FIRST: "network-first",
  STALE_WHILE_REVALIDATE: "stale-while-revalidate",
  NETWORK_ONLY: "network-only",
  CACHE_ONLY: "cache-only",
};

// Cache durations (in milliseconds)
const CACHE_DURATIONS = {
  STATIC: 24 * 60 * 60 * 1000, // 24 hours
  API: 5 * 60 * 1000, // 5 minutes
  IMAGES: 7 * 24 * 60 * 60 * 1000, // 7 days
  RACE_DATA: 2 * 60 * 1000, // 2 minutes (frequently updated)
};

// Install event - cache static assets
self.addEventListener("install", (event) => {
  console.log("Service Worker installing...");

  event.waitUntil(
    Promise.all([
      // Cache static assets
      caches.open(STATIC_CACHE_NAME).then((cache) => {
        return cache.addAll(STATIC_ASSETS);
      }),

      // Cache API endpoints with initial data
      caches.open(API_CACHE_NAME).then((cache) => {
        return Promise.all(
          API_ENDPOINTS.map((endpoint) => {
            return fetch(endpoint)
              .then((response) => {
                if (response.ok) {
                  return cache.put(endpoint, response.clone());
                }
              })
              .catch((err) => {
                console.log(`Failed to cache ${endpoint}:`, err);
              });
          })
        );
      }),
    ]).then(() => {
      // Force activation of new service worker
      return self.skipWaiting();
    })
  );
});

// Activate event - clean up old caches
self.addEventListener("activate", (event) => {
  console.log("Service Worker activating...");

  event.waitUntil(
    Promise.all([
      // Clean up old caches
      caches.keys().then((cacheNames) => {
        return Promise.all(
          cacheNames.map((cacheName) => {
            if (
              cacheName.startsWith(CACHE_NAME) &&
              cacheName !== FULL_CACHE_NAME
            ) {
              console.log("Deleting old cache:", cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),

      // Take control of all pages
      self.clients.claim(),
    ])
  );
});

// Fetch event - implement caching strategies
self.addEventListener("fetch", (event) => {
  const { request } = event;
  const url = new URL(request.url);

  // Skip non-GET requests
  if (request.method !== "GET") {
    return;
  }

  // Skip requests to other domains
  if (url.origin !== location.origin) {
    return;
  }

  // Determine cache strategy based on request
  let strategy = CACHE_STRATEGIES.NETWORK_FIRST;
  let cacheName = FULL_CACHE_NAME;
  let cacheDuration = CACHE_DURATIONS.STATIC;

  if (url.pathname.startsWith("/api/")) {
    // API requests
    strategy = CACHE_STRATEGIES.STALE_WHILE_REVALIDATE;
    cacheName = API_CACHE_NAME;

    if (url.pathname.includes("race") || url.pathname.includes("live")) {
      cacheDuration = CACHE_DURATIONS.RACE_DATA;
    } else {
      cacheDuration = CACHE_DURATIONS.API;
    }
  } else if (
    url.pathname.includes(".jpg") ||
    url.pathname.includes(".png") ||
    url.pathname.includes(".svg")
  ) {
    // Images
    strategy = CACHE_STRATEGIES.CACHE_FIRST;
    cacheName = STATIC_CACHE_NAME;
    cacheDuration = CACHE_DURATIONS.IMAGES;
  } else if (STATIC_ASSETS.some((asset) => url.pathname.includes(asset))) {
    // Static assets
    strategy = CACHE_STRATEGIES.CACHE_FIRST;
    cacheName = STATIC_CACHE_NAME;
    cacheDuration = CACHE_DURATIONS.STATIC;
  }

  event.respondWith(handleRequest(request, strategy, cacheName, cacheDuration));
});

// Handle requests with different caching strategies
async function handleRequest(request, strategy, cacheName, cacheDuration) {
  const cache = await caches.open(cacheName);

  switch (strategy) {
    case CACHE_STRATEGIES.CACHE_FIRST:
      return cacheFirst(request, cache, cacheDuration);

    case CACHE_STRATEGIES.NETWORK_FIRST:
      return networkFirst(request, cache, cacheDuration);

    case CACHE_STRATEGIES.STALE_WHILE_REVALIDATE:
      return staleWhileRevalidate(request, cache, cacheDuration);

    case CACHE_STRATEGIES.NETWORK_ONLY:
      return fetch(request);

    case CACHE_STRATEGIES.CACHE_ONLY:
      return cache.match(request);

    default:
      return networkFirst(request, cache, cacheDuration);
  }
}

// Cache first strategy
async function cacheFirst(request, cache, cacheDuration) {
  const cachedResponse = await cache.match(request);

  if (cachedResponse && !isExpired(cachedResponse, cacheDuration)) {
    return cachedResponse;
  }

  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const responseToCache = networkResponse.clone();
      await cacheWithTimestamp(cache, request, responseToCache);
    }
    return networkResponse;
  } catch (error) {
    console.log("Network failed, returning cached response:", error);
    return cachedResponse || new Response("Offline", { status: 503 });
  }
}

// Network first strategy
async function networkFirst(request, cache, cacheDuration) {
  try {
    const networkResponse = await fetch(request);
    if (networkResponse.ok) {
      const responseToCache = networkResponse.clone();
      await cacheWithTimestamp(cache, request, responseToCache);
    }
    return networkResponse;
  } catch (error) {
    console.log("Network failed, trying cache:", error);
    const cachedResponse = await cache.match(request);
    if (cachedResponse) {
      return cachedResponse;
    }
    throw error;
  }
}

// Stale while revalidate strategy
async function staleWhileRevalidate(request, cache, cacheDuration) {
  const cachedResponse = await cache.match(request);

  // Start network request in background
  const networkPromise = fetch(request)
    .then(async (networkResponse) => {
      if (networkResponse.ok) {
        const responseToCache = networkResponse.clone();
        await cacheWithTimestamp(cache, request, responseToCache);
      }
      return networkResponse;
    })
    .catch((error) => {
      console.log("Background network request failed:", error);
    });

  // Return cached response if available and not expired
  if (cachedResponse && !isExpired(cachedResponse, cacheDuration)) {
    // Don't wait for network request
    networkPromise.then(() => {
      // Notify clients of updated data
      notifyClients("cache-updated", { url: request.url });
    });
    return cachedResponse;
  }

  // Wait for network response if no valid cache
  return networkPromise;
}

// Add timestamp to cached responses
async function cacheWithTimestamp(cache, request, response) {
  const responseWithTimestamp = new Response(response.body, {
    status: response.status,
    statusText: response.statusText,
    headers: {
      ...response.headers,
      "sw-cached-at": Date.now().toString(),
    },
  });

  return cache.put(request, responseWithTimestamp);
}

// Check if cached response is expired
function isExpired(response, maxAge) {
  const cachedAt = response.headers.get("sw-cached-at");
  if (!cachedAt) return true;

  const age = Date.now() - parseInt(cachedAt);
  return age > maxAge;
}

// Notify clients of events
function notifyClients(type, data) {
  self.clients.matchAll().then((clients) => {
    clients.forEach((client) => {
      client.postMessage({ type, data });
    });
  });
}

// Background sync for offline actions
self.addEventListener("sync", (event) => {
  console.log("Background sync triggered:", event.tag);

  if (event.tag === "background-sync-bets") {
    event.waitUntil(syncOfflineBets());
  } else if (event.tag === "background-sync-analytics") {
    event.waitUntil(syncOfflineAnalytics());
  }
});

// Sync offline bets when connection is restored
async function syncOfflineBets() {
  try {
    const offlineBets = await getOfflineData("offline-bets");

    for (const bet of offlineBets) {
      try {
        const response = await fetch("/api/betting/place", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(bet),
        });

        if (response.ok) {
          await removeOfflineData("offline-bets", bet.id);
          notifyClients("bet-synced", { bet });
        }
      } catch (error) {
        console.log("Failed to sync bet:", error);
      }
    }
  } catch (error) {
    console.log("Failed to sync offline bets:", error);
  }
}

// Sync offline analytics when connection is restored
async function syncOfflineAnalytics() {
  try {
    const offlineAnalytics = await getOfflineData("offline-analytics");

    for (const analytics of offlineAnalytics) {
      try {
        const response = await fetch("/api/analytics/track", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(analytics),
        });

        if (response.ok) {
          await removeOfflineData("offline-analytics", analytics.id);
        }
      } catch (error) {
        console.log("Failed to sync analytics:", error);
      }
    }
  } catch (error) {
    console.log("Failed to sync offline analytics:", error);
  }
}

// IndexedDB helpers for offline data
async function getOfflineData(storeName) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("horse-racing-offline", 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction([storeName], "readonly");
      const store = transaction.objectStore(storeName);
      const getAllRequest = store.getAll();

      getAllRequest.onsuccess = () => resolve(getAllRequest.result);
      getAllRequest.onerror = () => reject(getAllRequest.error);
    };

    request.onupgradeneeded = () => {
      const db = request.result;
      if (!db.objectStoreNames.contains(storeName)) {
        db.createObjectStore(storeName, { keyPath: "id" });
      }
    };
  });
}

async function removeOfflineData(storeName, id) {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("horse-racing-offline", 1);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => {
      const db = request.result;
      const transaction = db.transaction([storeName], "readwrite");
      const store = transaction.objectStore(storeName);
      const deleteRequest = store.delete(id);

      deleteRequest.onsuccess = () => resolve();
      deleteRequest.onerror = () => reject(deleteRequest.error);
    };
  });
}

// Push notification handling
self.addEventListener("push", (event) => {
  console.log("Push notification received:", event);

  if (!event.data) {
    return;
  }

  try {
    const data = event.data.json();
    const options = {
      body: data.body,
      icon: "/favicon.ico",
      badge: "/badge-icon.png",
      vibrate: [200, 100, 200],
      data: data.data,
      actions: data.actions || [],
      tag: data.tag || "default",
    };

    event.waitUntil(self.registration.showNotification(data.title, options));
  } catch (error) {
    console.log("Failed to show notification:", error);
  }
});

// Notification click handling
self.addEventListener("notificationclick", (event) => {
  console.log("Notification clicked:", event);

  event.notification.close();

  if (event.action) {
    // Handle action buttons
    switch (event.action) {
      case "view-race":
        event.waitUntil(
          clients.openWindow(`/race/${event.notification.data.raceId}`)
        );
        break;
      case "place-bet":
        event.waitUntil(
          clients.openWindow(`/betting?race=${event.notification.data.raceId}`)
        );
        break;
    }
  } else {
    // Default action
    event.waitUntil(clients.openWindow("/"));
  }
});

console.log("Service Worker loaded successfully");
