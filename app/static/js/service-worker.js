self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open('static-cache-v1').then(function(cache) {
            return cache.addAll([
                '/',
                '/static/css/style.css',
                '/static/js/script.js',
                '/static/icons/icon-192x192.png',
                '/static/icons/icon-512x512.png'
            ]);
        })
    );
});

self.addEventListener('fetch', function(event) {
    event.respondWith(
        caches.match(event.request).then(function(response) {
            return response || fetch(event.request);
        })
    );
});

self.addEventListener('push', function(event) {
    var data = event.data.json();
    var options = {
        body: data.content,
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/icon-192x192.png'
    };
    event.waitUntil(
        self.registration.showNotification(data.username, options)
    );
});

self.addEventListener('notificationclick', function(event) {
    event.notification.close();
    event.waitUntil(
        clients.openWindow('/')
    );
});