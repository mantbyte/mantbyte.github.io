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

        // Remove the automatic mark as read here so the user can see which are unread.
        // We will only mark as read if they click the "mark all read" button.
        // BUT we should clear the badge anyway so it's not annoying.
        if (notifPanel.classList.contains('show')) {
            if (notifBadge) notifBadge.style.display = 'none';
        }
    });

    const markReadBtn = document.getElementById('notif-mark-read');
    if (markReadBtn) {
        markReadBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            localStorage.setItem('mantbyte_last_notif_check', new Date().toISOString());
            if (notifBadge) notifBadge.style.display = 'none';
            document.querySelectorAll('.notif-item.unread').forEach(el => el.classList.remove('unread'));
        });
    }

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
                notifList.innerHTML = `
                    <div class="notif-empty">
                        <div class="empty-icon">⚠️</div>
                        <p>Unable to load notifications.</p>
                    </div>`;
            }
        }
    }

    function renderNotifications(notifications) {
        if (!notifList) return;

        if (notifications.length === 0) {
            notifList.innerHTML = `
                <div class="notif-empty">
                    <div class="empty-icon">✨</div>
                    <p>No new articles yet. Check back soon!</p>
                </div>`;
            return;
        }

        let lastCheckTime = 0;
        const lastCheckStr = localStorage.getItem('mantbyte_last_notif_check');
        if (lastCheckStr) {
            lastCheckTime = new Date(lastCheckStr).getTime();
        }

        notifList.innerHTML = notifications.map(notif => {
            const date = new Date(notif.published_at);
            
            // Format time relatively (e.g. "2h ago")
            const now = new Date();
            const diffMs = now - date;
            const diffMins = Math.floor(diffMs / 60000);
            const diffHours = Math.floor(diffMins / 60);
            const diffDays = Math.floor(diffHours / 24);
            
            let dateStr = "";
            if (diffMins < 60) dateStr = `${diffMins || 1}m ago`;
            else if (diffHours < 24) dateStr = `${diffHours}h ago`;
            else if (diffDays === 1) dateStr = 'Yesterday';
            else dateStr = date.toLocaleDateString(undefined, { month: 'short', day: 'numeric' });

            const isUnread = date.getTime() > lastCheckTime;

            let imgHtml = '';
            if (notif.featured_image) {
                imgHtml = `<img src="${notif.featured_image}" alt="" class="notif-img">`;
            }

            return `
                <a href="${notif.url}" class="notif-item ${isUnread ? 'unread' : ''}">
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
