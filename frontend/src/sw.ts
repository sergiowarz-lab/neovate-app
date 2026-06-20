/// <reference lib="webworker" />
import { cleanupOutdatedCaches, precacheAndRoute } from "workbox-precaching";

declare const self: ServiceWorkerGlobalScope;

// Workbox inyecta el manifiesto de precaché aquí en build
precacheAndRoute(self.__WB_MANIFEST);
cleanupOutdatedCaches();

// ── Push notifications ─────────────────────────────────────────────────────────
self.addEventListener("push", (event) => {
  let data: { title?: string; body?: string; tag?: string } = {};
  try {
    data = event.data?.json() ?? {};
  } catch {
    data = { title: "Neovate", body: event.data?.text() ?? "" };
  }

  const options: NotificationOptions = {
    body: data.body ?? "",
    icon: "/pwa-192x192.png",
    badge: "/pwa-192x192.png",
    tag: data.tag ?? "neovate",
    data: { url: "/" },
  };

  event.waitUntil(
    self.registration.showNotification(data.title ?? "Sistema Neovate", options)
  );
});

self.addEventListener("notificationclick", (event) => {
  event.notification.close();
  const targetUrl = (event.notification.data?.url as string) ?? "/";
  event.waitUntil(
    self.clients.matchAll({ type: "window" }).then((clients) => {
      const existing = clients.find((c) => c.url.includes(targetUrl) && "focus" in c);
      if (existing) return existing.focus();
      return self.clients.openWindow(targetUrl);
    })
  );
});

// ── Offline: historial endpoints ───────────────────────────────────────────────
const HISTORIAL_CACHE = "neovate-historial-v1";
const HISTORIAL_RUTAS = [
  "/api/reportes/ss",
  "/api/reportes/nomina",
  "/api/seguimiento/kpis",
  "/api/seguimiento",
];

self.addEventListener("fetch", (event) => {
  const url = new URL(event.request.url);
  const esHistorial =
    event.request.method === "GET" &&
    HISTORIAL_RUTAS.some((r) => url.pathname.endsWith(r));

  if (esHistorial) {
    // Network First: intenta red → guarda en caché → si falla, sirve caché
    event.respondWith(
      fetch(event.request.clone())
        .then(async (response) => {
          if (response.ok) {
            const cache = await caches.open(HISTORIAL_CACHE);
            cache.put(event.request, response.clone());
          }
          return response;
        })
        .catch(async () => {
          const cached = await caches.match(event.request);
          // Si hay datos en caché, devolverlos con header indicador
          if (cached) {
            const body = await cached.text();
            return new Response(body, {
              status: 200,
              headers: {
                "Content-Type": "application/json",
                "X-From-Cache": "true",
              },
            });
          }
          // Sin caché y sin red: lista vacía
          return new Response("[]", {
            status: 200,
            headers: { "Content-Type": "application/json" },
          });
        })
    );
    return;
  }

  // Resto de llamadas API: solo red
  if (url.pathname.includes("/api/")) {
    event.respondWith(
      fetch(event.request).catch(() => new Response("Offline", { status: 503 }))
    );
  }
});
