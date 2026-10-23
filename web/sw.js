// Сеть в приоритете; при отсутствии связи — последняя сохранённая версия.
const CACHE = "ironman-v4";
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

// push-уведомления: новая тренировка (тренеру), оценка и комментарии (спортсмену)
self.addEventListener("push", (e) => {
  let d = {}; try { d = e.data.json(); } catch { d = { title: "Ironman", body: e.data?.text() || "" }; }
  e.waitUntil(self.registration.showNotification(d.title || "Ironman", {
    body: d.body || "", icon: "icons/icon-192.png", badge: "icons/icon-192.png", data: { url: d.url || "/" }, tag: d.tag,
  }));
});
self.addEventListener("notificationclick", (e) => {
  e.notification.close();
  const url = e.notification.data?.url || "/";
  e.waitUntil(clients.matchAll({ type: "window", includeUncontrolled: true }).then((ws) => {
    const w = ws.find((x) => new URL(x.url).origin === self.location.origin);
    if (w) { w.navigate(url); return w.focus(); }
    return clients.openWindow(url);
  }));
});
