// ==========================================================================
// PWA Install & Notification Prompt Controller
// ==========================================================================

(function() {
    'use strict';

    // ---- PWA Install Logic ----

    let deferredPrompt = null;
    const INSTALL_DISMISSED_KEY = 'pwaInstallDismissed';
    const INSTALL_DISMISSED_EXPIRY = 7 * 24 * 60 * 60 * 1000; // 7 days
    const NOTIF_DISMISSED_KEY = 'notifPromptDismissed';
    const NOTIF_DISMISSED_EXPIRY = 3 * 24 * 60 * 60 * 1000; // 3 days

    function isDismissed(key, expiry) {
        const raw = localStorage.getItem(key);
        if (!raw) return false;
        const ts = parseInt(raw, 10);
        if (Date.now() - ts > expiry) {
            localStorage.removeItem(key);
            return false;
        }
        return true;
    }

    function isIos() {
        return /iphone|ipad|ipod/i.test(navigator.userAgent) && !window.MSStream;
    }

    function isInStandaloneMode() {
        return (window.matchMedia('(display-mode: standalone)').matches) ||
               (window.navigator.standalone === true);
    }

    // Capture the beforeinstallprompt event (Android / Desktop Chrome)
    window.addEventListener('beforeinstallprompt', (e) => {
        e.preventDefault();
        deferredPrompt = e;
        console.log('[PWA] beforeinstallprompt captured');
        showInstallBanner();
    });

    function showInstallBanner() {
        if (isDismissed(INSTALL_DISMISSED_KEY, INSTALL_DISMISSED_EXPIRY)) return;
        if (isInStandaloneMode()) return;

        const banner = document.getElementById('pwa-install-banner');
        if (banner) {
            setTimeout(() => {
                banner.style.display = 'flex';
                banner.classList.add('pwa-slide-in');
            }, 2000);
        }
    }

    function showIosInstallPrompt() {
        if (isDismissed(INSTALL_DISMISSED_KEY, INSTALL_DISMISSED_EXPIRY)) return;
        if (isInStandaloneMode()) return;
        if (!isIos()) return;

        const modal = document.getElementById('ios-install-modal');
        if (modal) {
            setTimeout(() => {
                modal.style.display = 'flex';
            }, 3000);
        }
    }

    // Expose closeIosInstall globally
    window.closeIosInstall = function() {
        const modal = document.getElementById('ios-install-modal');
        if (modal) modal.style.display = 'none';
        localStorage.setItem(INSTALL_DISMISSED_KEY, Date.now().toString());
    };

    // ---- Notification Permission Logic ----

    function showNotifPrompt() {
        if (!('Notification' in window)) return;
        if (Notification.permission === 'granted' || Notification.permission === 'denied') return;
        if (isDismissed(NOTIF_DISMISSED_KEY, NOTIF_DISMISSED_EXPIRY)) return;
        if (isInStandaloneMode() && isIos()) return; // iOS PWA can't do web push

        const prompt = document.getElementById('notif-permission-prompt');
        if (prompt) {
            // Show notification prompt after install prompt (or by itself)
            const delay = deferredPrompt ? 8000 : 5000;
            setTimeout(() => {
                // Only show if the install banner is not currently visible
                const installBanner = document.getElementById('pwa-install-banner');
                if (installBanner && installBanner.style.display !== 'none') {
                    // Wait for install banner to be dismissed first
                    const observer = new MutationObserver(() => {
                        if (installBanner.style.display === 'none') {
                            observer.disconnect();
                            setTimeout(() => {
                                prompt.style.display = 'flex';
                                prompt.classList.add('pwa-slide-in');
                            }, 1000);
                        }
                    });
                    observer.observe(installBanner, { attributes: true, attributeFilter: ['style'] });
                } else {
                    prompt.style.display = 'flex';
                    prompt.classList.add('pwa-slide-in');
                }
            }, delay);
        }
    }

    // ---- Attach Event Listeners ----

    document.addEventListener('DOMContentLoaded', () => {
        // --- Install Banner Buttons ---
        const installBtn = document.getElementById('pwa-install-btn');
        const installDismiss = document.getElementById('pwa-install-dismiss');
        const installBanner = document.getElementById('pwa-install-banner');

        if (installBtn) {
            installBtn.addEventListener('click', async () => {
                if (deferredPrompt) {
                    deferredPrompt.prompt();
                    const result = await deferredPrompt.userChoice;
                    console.log('[PWA] Install result:', result.outcome);
                    deferredPrompt = null;
                }
                if (installBanner) {
                    installBanner.classList.remove('pwa-slide-in');
                    installBanner.classList.add('pwa-slide-out');
                    setTimeout(() => { installBanner.style.display = 'none'; }, 400);
                }
            });
        }

        if (installDismiss) {
            installDismiss.addEventListener('click', () => {
                localStorage.setItem(INSTALL_DISMISSED_KEY, Date.now().toString());
                if (installBanner) {
                    installBanner.classList.remove('pwa-slide-in');
                    installBanner.classList.add('pwa-slide-out');
                    setTimeout(() => { installBanner.style.display = 'none'; }, 400);
                }
            });
        }

        // --- Notification Prompt Buttons ---
        const notifEnable = document.getElementById('notif-prompt-enable');
        const notifDismiss = document.getElementById('notif-prompt-dismiss');
        const notifPrompt = document.getElementById('notif-permission-prompt');

        if (notifEnable) {
            notifEnable.addEventListener('click', async () => {
                // Hide prompt immediately
                if (notifPrompt) {
                    notifPrompt.classList.remove('pwa-slide-in');
                    notifPrompt.classList.add('pwa-slide-out');
                    setTimeout(() => { notifPrompt.style.display = 'none'; }, 400);
                }
                localStorage.setItem(NOTIF_DISMISSED_KEY, Date.now().toString());

                // Trigger the existing push-accept button to reuse Firebase logic
                const existingAccept = document.getElementById('push-accept');
                if (existingAccept) {
                    existingAccept.click();
                } else {
                    // Fallback: request permission directly
                    try {
                        const permission = await Notification.requestPermission();
                        console.log('[PWA] Notification permission:', permission);
                    } catch (err) {
                        console.warn('[PWA] Notification permission error:', err);
                    }
                }
            });
        }

        if (notifDismiss) {
            notifDismiss.addEventListener('click', () => {
                localStorage.setItem(NOTIF_DISMISSED_KEY, Date.now().toString());
                if (notifPrompt) {
                    notifPrompt.classList.remove('pwa-slide-in');
                    notifPrompt.classList.add('pwa-slide-out');
                    setTimeout(() => { notifPrompt.style.display = 'none'; }, 400);
                }
            });
        }

        // --- Show prompts ---
        // For iOS, show the iOS install instructions
        if (isIos() && !isInStandaloneMode()) {
            showIosInstallPrompt();
        }

        // Show notification prompt (on all platforms)
        showNotifPrompt();
    });

    // Track successful install
    window.addEventListener('appinstalled', () => {
        console.log('[PWA] App installed successfully!');
        deferredPrompt = null;
        const banner = document.getElementById('pwa-install-banner');
        if (banner) banner.style.display = 'none';
    });

})();
