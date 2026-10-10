// Сеть в приоритете; при отсутствии связи — последняя сохранённая версия.
const CACHE = "ironman-v3";
self.addEventListener("install", (e) => self.skipWaiting());
self.addEventListener("activate", (e) => e.waitUntil(
  caches.keys().then((ks) => Promise.all(ks.filter((k) => k !== CACHE).map((k) => caches.delete(k)))).then(() => self.clients.claim())));
self.addEventListener("fetch", (e) => {
  if (e.request.method !== "GET") return;
  const u = new URL(e.request.url);
  // данные и вход — всегда из сети, в кэш не кладём (личные данные, сессии)
  if (u.pathname.startsWith("/api/") || u.pathname === "/login") return;
  e.respondWith(
    fetch(e.request, { cache: "no-cache" })
      .then((r) => { const copy = r.clone(); caches.open(CACHE).then((c) => c.put(e.request, copy)); return r; })
      .catch(() => caches.match(e.request))
  );
});
