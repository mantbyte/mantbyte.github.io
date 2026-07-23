import { db, doc, getDoc, updateDoc, collection, getDocs, query, where } from './firestore.js';
import { getCurrentUser } from './auth.js';

export const getProfile = async () => {
    const user = getCurrentUser();
    if (!user) return null;
    
    const snap = await getDoc(doc(db, 'users', user.uid));
    return snap.exists() ? snap.data() : null;
};

export const updatePreferences = async (preferences) => {
    const user = getCurrentUser();
    if (!user) throw new Error("Not logged in");
    
    const userRef = doc(db, 'users', user.uid);
    await updateDoc(userRef, { preferences });
};

export const getUserBookmarks = async () => {
    const user = getCurrentUser();
    if (!user) return [];
    
    const bookmarksRef = collection(db, 'users', user.uid, 'bookmarks');
    const snap = await getDocs(bookmarksRef);
    return snap.docs.map(doc => doc.id);
};

export const getUserLikes = async () => {
    const user = getCurrentUser();
    if (!user) return [];
    
    const interactionsRef = collection(db, 'users', user.uid, 'interactions');
    const q = query(interactionsRef, where('liked', '==', true));
    const snap = await getDocs(q);
    return snap.docs.map(doc => doc.id);
};
