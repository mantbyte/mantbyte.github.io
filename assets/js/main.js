// Mobile menu toggle
const menuToggle = document.getElementById('menu-toggle');
const siteNav = document.getElementById('site-nav');

if (menuToggle && siteNav) {
    menuToggle.addEventListener('click', () => {
        siteNav.classList.toggle('active');
    });
}

// Reading progress bar (only on post pages)
const progressBar = document.getElementById('reading-progress');

if (progressBar) {
    window.addEventListener('scroll', () => {
        const docHeight = document.documentElement.scrollHeight - window.innerHeight;
        if (docHeight > 0) {
            const scrolled = (window.scrollY / docHeight) * 100;
            progressBar.style.width = scrolled + '%';
        }
    }, { passive: true });
}

// Scroll to top button
const scrollTopBtn = document.getElementById('scroll-top');

if (scrollTopBtn) {
    window.addEventListener('scroll', () => {
        if (window.scrollY > 400) {
            scrollTopBtn.classList.add('visible');
        } else {
            scrollTopBtn.classList.remove('visible');
        }
    }, { passive: true });

    scrollTopBtn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// Auth Popup Logic
function closeAuthPopup() {
    const popup = document.getElementById('auth-popup');
    if (popup) {
        popup.classList.remove('show');
        sessionStorage.setItem('authPopupClosed', 'true');
    }
}

window.addEventListener('DOMContentLoaded', () => {
    // Check if popup was already closed in this session
    if (sessionStorage.getItem('authPopupClosed') === 'true') {
        return;
    }

    // Wait 10 seconds before showing
    setTimeout(() => {
        // Check if user is logged out (by checking the visibility of the login icon)
        const loggedOutLink = document.querySelector('.logged-out-show');
        if (loggedOutLink) {
            const isVisible = window.getComputedStyle(loggedOutLink).display !== 'none';
            if (isVisible) {
                const popup = document.getElementById('auth-popup');
                if (popup) {
                    popup.classList.add('show');
                }
            }
        }
    }, 10000); // 10 seconds
});
