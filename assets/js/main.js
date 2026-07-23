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
