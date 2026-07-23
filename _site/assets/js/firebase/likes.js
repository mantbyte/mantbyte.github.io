import { db, doc, getDoc, setDoc, updateDoc, increment, ensurePostDocExists, serverTimestamp } from './firestore.js';
import { getCurrentUser } from './auth.js';

export const toggleLike = async (postSlug) => {
    const user = getCurrentUser();
    if (!user) throw new Error("Must be logged in to like a post");

    const interactionRef = doc(db, 'users', user.uid, 'interactions', postSlug);
    const postRef = doc(db, 'posts', postSlug);
    
    await ensurePostDocExists(postSlug);
    const interactionSnap = await getDoc(interactionRef);
    
    let liked = false;
    let incrementVal = 1;

    if (interactionSnap.exists()) {
        const data = interactionSnap.data();
        if (data.liked) {
            liked = false;
            incrementVal = -1;
        } else {
            liked = true;
            incrementVal = 1;
        }
    } else {
        liked = true;
        incrementVal = 1;
    }

    // Update user's personal interaction
    await setDoc(interactionRef, { liked, updatedAt: serverTimestamp() }, { merge: true });
    // Update global aggregate
    await updateDoc(postRef, { likesCount: increment(incrementVal) });
    
    return { liked, incrementVal };
};

export const getLikeStatus = async (postSlug) => {
    const user = getCurrentUser();
    if (!user) return false;
    
    const interactionRef = doc(db, 'users', user.uid, 'interactions', postSlug);
    const interactionSnap = await getDoc(interactionRef);
    
    if (interactionSnap.exists()) {
        return interactionSnap.data().liked || false;
    }
    return false;
};

export const getPostLikes = async (postSlug) => {
    const postRef = doc(db, 'posts', postSlug);
    const snap = await getDoc(postRef);
    return snap.exists() ? snap.data().likesCount || 0 : 0;
};
