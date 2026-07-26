import { app, db } from './firebase-init.js';
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-messaging.js";
import { doc, setDoc } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Initialize Firebase Cloud Messaging
let messaging = null;

// Only initialize messaging in supported environments
try {
    if (typeof window !== 'undefined' && 'serviceWorker' in navigator) {
        messaging = getMessaging(app);
    }
} catch (error) {
    console.warn('Firebase Messaging not supported:', error);
}

// Function to handle showing the push prompt UI
function showPushPrompt() {
    // Check if notifications are supported by the browser
    if (!('Notification' in window)) {
        console.log("This browser does not support Web Push Notifications.");
        return;
    }

    // Don't show if they've already dismissed it
    if (localStorage.getItem('pushPromptDismissed') === 'true') {
        return;
    }

    // Don't show if they already granted permission
    if (Notification.permission === 'granted') {
        return;
    }

    // Don't show if they denied permission
    if (Notification.permission === 'denied') {
        return;
    }

    const promptUI = document.getElementById('push-prompt');
    if (promptUI) {
        // Add a slight delay before showing so it doesn't interrupt immediate reading
        setTimeout(() => {
            promptUI.style.display = 'flex';
        }, 3000);
    }
}

// Function to handle the subscription process
async function subscribeToPushNotifications() {
    if (!messaging) {
        console.error('Messaging not initialized');
        return false;
    }

    try {
        const permission = await Notification.requestPermission();
        if (permission === 'granted') {
            // Need the VAPID key here from your Firebase console
            // Using a placeholder - THIS MUST BE REPLACED WITH YOUR ACTUAL VAPID KEY
            // Typically fetched from an API endpoint or embedded in the page config
            console.log("Notification permission granted.");

            // Register service worker explicitly first to ensure it's ready
            const registration = await navigator.serviceWorker.register('/firebase-messaging-sw.js');

            // Get the FCM token
            const token = await getToken(messaging, {
                serviceWorkerRegistration: registration,
                vapidKey: 'BCNcM8YabA4ooT8tlOgAS_AfiztSDx9fApQcU7kMpEDuQx5GLwcTbGZ-LJRd1Q4JJzLjejB98jBt1untO7KiTm0' // REPLACE THIS WITH YOUR FIREBASE VAPID KEY
            });

            if (token) {
                console.log('Got FCM token, saving to Firestore...');
                await saveTokenToFirestore(token);
                return true;
            }
        }
    } catch (error) {
        console.error('Error subscribing to push notifications:', error);
    }
    return false;
}

// Function to save token to Firestore
async function saveTokenToFirestore(token) {
    try {
        // We use the encoded token as the document ID. This allows us to use setDoc
        // with merge: true, which acts as an upsert (create or update).
        // This is a secure pattern because it requires NO read permissions on the collection!
        const docId = encodeURIComponent(token);
        const tokenRef = doc(db, 'notification_tokens', docId);

        await setDoc(tokenRef, {
            token: token,
            browser: getBrowserName(),
            platform: navigator.platform,
            language: navigator.language,
            last_used: new Date(),
            active: true
        }, { merge: true });

        console.log('Token securely saved/updated in Firestore');
    } catch (error) {
        console.error('Error saving token to Firestore:', error);
    }
}

// Helper to get browser name
function getBrowserName() {
    const userAgent = navigator.userAgent;
    if (userAgent.match(/chrome|chromium|crios/i)) return "Chrome";
    if (userAgent.match(/firefox|fxios/i)) return "Firefox";
    if (userAgent.match(/safari/i)) return "Safari";
    if (userAgent.match(/opr\//i)) return "Opera";
    if (userAgent.match(/edg/i)) return "Edge";
    return "Other";
}

// Set up UI event listeners when DOM loads
document.addEventListener('DOMContentLoaded', () => {
    showPushPrompt();

    const acceptBtn = document.getElementById('push-accept');
    const dismissBtn = document.getElementById('push-dismiss');
    const promptUI = document.getElementById('push-prompt');

    if (acceptBtn) {
        acceptBtn.addEventListener('click', async () => {
            if (promptUI) promptUI.style.display = 'none';
            const success = await subscribeToPushNotifications();
            if (success) {
                localStorage.setItem('pushPromptDismissed', 'true');
                // Could show a "Successfully subscribed!" toast here
            }
        });
    }

    if (dismissBtn) {
        dismissBtn.addEventListener('click', () => {
            localStorage.setItem('pushPromptDismissed', 'true');
            if (promptUI) promptUI.style.display = 'none';
        });
    }
});
