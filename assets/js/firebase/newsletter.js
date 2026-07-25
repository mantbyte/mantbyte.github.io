import { db } from './firebase-init.js';
import { doc, setDoc } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('newsletter-form');
    if (!form) return;

    const emailInput = document.getElementById('newsletter-email');
    const submitBtn = document.getElementById('newsletter-submit');
    const statusMsg = document.getElementById('newsletter-status');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const email = emailInput.value.trim().toLowerCase();
        if (!email) return;

        // Get selected categories
        const categoryCheckboxes = document.querySelectorAll('.newsletter-categories input[type="checkbox"]:checked');
        const categories = Array.from(categoryCheckboxes).map(cb => cb.value);

        // UI Loading state
        submitBtn.disabled = true;
        submitBtn.innerHTML = 'Subscribing...';
        statusMsg.className = 'newsletter-status';
        statusMsg.style.display = 'none';

        try {
            const verificationToken = generateUUID();

            // Address the document by the verification capability. This lets the
            // verification page update only the record named by the email link,
            // without granting the browser any subscriber collection reads.
            await setDoc(doc(db, 'subscribers', verificationToken), {
                email: email,
                verified: false,
                created_at: new Date(),
                last_seen: new Date(),
                is_active: true,
                notification_enabled: true,
                newsletter_enabled: true,
                push_enabled: false, // Handled separately by push tokens
                language: navigator.language || 'en',
                preferences: {
                    categories: categories.length > 0 ? categories : ['Tech', 'News', 'Geopolitics']
                },
                verification_token: verificationToken,
                verification_sent: false
            });

            showStatus('Thanks! Please check your email to confirm your subscription.', 'success');
            form.reset();
        } catch (error) {
            console.error('Newsletter error:', error);
            showStatus('Something went wrong. Please try again later.', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = 'Subscribe';
        }
    });

    function showStatus(message, type) {
        statusMsg.textContent = message;
        statusMsg.className = `newsletter-status status-${type}`;
        statusMsg.style.display = 'block';
    }

    // Simple UUID generator for verification tokens
    function generateUUID() {
        return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
            var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
            return v.toString(16);
        });
    }
});
