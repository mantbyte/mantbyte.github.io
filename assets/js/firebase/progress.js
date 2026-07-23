import { db, doc, setDoc, serverTimestamp } from './firestore.js';
import { getCurrentUser } from './auth.js';

let progressTimer = null;

export const saveReadingProgress = (postSlug, percent) => {
    const user = getCurrentUser();
    if (!user) return;

    // Debounce to avoid spamming Firestore writes (save every 2 seconds of idle scroll)
    if (progressTimer) clearTimeout(progressTimer);
    
    progressTimer = setTimeout(async () => {
        try {
            const historyRef = doc(db, 'users', user.uid, 'history', postSlug);
            await setDoc(historyRef, {
                progressPercent: percent,
                lastReadAt: serverTimestamp(),
                completed: percent >= 95
            }, { merge: true });
        } catch (e) {
            console.error("Failed to save reading progress", e);
        }
    }, 2000);
};
