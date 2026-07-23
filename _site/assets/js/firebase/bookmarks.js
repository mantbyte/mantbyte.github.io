import { db, doc, getDoc, setDoc, deleteDoc, serverTimestamp } from './firestore.js';
import { getCurrentUser } from './auth.js';

export const toggleBookmark = async (postSlug) => {
    const user = getCurrentUser();
    if (!user) throw new Error("Must be logged in to bookmark");

    const bookmarkRef = doc(db, 'users', user.uid, 'bookmarks', postSlug);
    const snap = await getDoc(bookmarkRef);
    
    if (snap.exists()) {
        await deleteDoc(bookmarkRef);
        return false;
    } else {
        await setDoc(bookmarkRef, { savedAt: serverTimestamp() });
        return true;
    }
};

export const getBookmarkStatus = async (postSlug) => {
    const user = getCurrentUser();
    if (!user) return false;
    
    const bookmarkRef = doc(db, 'users', user.uid, 'bookmarks', postSlug);
    const snap = await getDoc(bookmarkRef);
    return snap.exists();
};
