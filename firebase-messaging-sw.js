// Firebase Cloud Messaging Service Worker
// Required to receive background push notifications

importScripts('https://www.gstatic.com/firebasejs/10.9.0/firebase-app-compat.js');
importScripts('https://www.gstatic.com/firebasejs/10.9.0/firebase-messaging-compat.js');

// Must match the config in firebase-init.js
const firebaseConfig = {
  apiKey: "AIzaSyAA8cxhNcIrm1DwLmkjRZJn2ateX2e7Z8Q",
  authDomain: "mantbytes-f47ca.firebaseapp.com",
  projectId: "mantbytes-f47ca",
  storageBucket: "mantbytes-f47ca.firebasestorage.app",
  messagingSenderId: "629672485015",
  appId: "1:629672485015:web:5e3f6bf8e89c8b1c97c9d2"
};

firebase.initializeApp(firebaseConfig);

const messaging = firebase.messaging();

// Handle background messages
messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);

  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: payload.notification.image || '/assets/images/favicon.svg',
    image: payload.notification.image,
    data: payload.data
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});

// Handle notification click
self.addEventListener('notificationclick', (event) => {
  event.notification.close();

  // If the payload has a link in FCM options, open it
  let urlToOpen = '/';
  if (event.notification.data && event.notification.data.click_action) {
     urlToOpen = event.notification.data.click_action;
  }

  event.waitUntil(
    clients.matchAll({ type: 'window' }).then((windowClients) => {
      // Check if there is already a window/tab open with the target URL
      for (let i = 0; i < windowClients.length; i++) {
        const client = windowClients[i];
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      // If not, open a new window
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});
