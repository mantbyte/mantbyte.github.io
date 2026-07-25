import { db } from './firebase-init.js';
import { collection, query, orderBy, limit, getDocs } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

document.addEventListener('DOMContentLoaded', () => {
    const notifBell = document.getElementById('notif-bell');
    const notifBadge = document.getElementById('notif-badge');
    const notifPanel = document.getElementById('notif-panel');
    const notifList = document.getElementById('notif-list');

    if (!notifBell || !notifPanel) return;

    // Toggle panel
    notifBell.addEventListener('click', (e) => {
        e.preventDefault();
        notifPanel.classList.toggle('show');

        // Mark as read (hide badge) when opened
        if (notifPanel.classList.contains('show')) {
            localStorage.setItem('mantbyte_last_notif_check', new Date().toISOString());
            if (notifBadge) notifBadge.style.display = 'none';
        }
    });

    // Close when clicking outside
    document.addEventListener('click', (e) => {
        if (!notifBell.contains(e.target) && !notifPanel.contains(e.target)) {
            notifPanel.classList.remove('show');
        }
    });

    // Fetch notifications from Firestore
    async function fetchNotifications() {
        try {
            const notifRef = collection(db, 'site_notifications');
            // Get latest 5 notifications
            const q = query(notifRef, orderBy('published_at', 'desc'), limit(5));
            const querySnapshot = await getDocs(q);

            const notifications = [];
            querySnapshot.forEach((doc) => {
                notifications.push({ id: doc.id, ...doc.data() });
            });

            renderNotifications(notifications);
            checkUnread(notifications);
        } catch (error) {
            console.error("Error fetching notifications:", error);
            if (notifList) {
                notifList.innerHTML = '<div class="notif-empty">Unable to load notifications.</div>';
            }
        }
    }

    function renderNotifications(notifications) {
        if (!notifList) return;

        if (notifications.length === 0) {
            notifList.innerHTML = '<div class="notif-empty">No new articles yet. Check back soon!</div>';
            return;
        }

        notifList.innerHTML = notifications.map(notif => {
            const date = new Date(notif.published_at);
            const dateStr = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

            let imgHtml = '';
            if (notif.featured_image) {
                imgHtml = `<img src="${notif.featured_image}" alt="" class="notif-img">`;
            }

            return `
                <a href="${notif.url}" class="notif-item">
                    ${imgHtml}
                    <div class="notif-content">
                        <span class="notif-category">${notif.category || 'Article'}</span>
                        <h4 class="notif-title">${notif.title}</h4>
                        <span class="notif-date">${dateStr}</span>
                    </div>
                </a>
            `;
        }).join('');
    }

    function checkUnread(notifications) {
        if (notifications.length === 0 || !notifBadge) return;

        const lastCheckStr = localStorage.getItem('mantbyte_last_notif_check');
        let unreadCount = 0;

        if (!lastCheckStr) {
            unreadCount = notifications.length;
        } else {
            const lastCheck = new Date(lastCheckStr);
            unreadCount = notifications.filter(n => new Date(n.published_at) > lastCheck).length;
        }

        if (unreadCount > 0) {
            notifBadge.textContent = unreadCount > 9 ? '9+' : unreadCount;
            notifBadge.style.display = 'flex';
        } else {
            notifBadge.style.display = 'none';
        }
    }

    // Initialize
    fetchNotifications();
});
