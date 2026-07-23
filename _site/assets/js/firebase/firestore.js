import { db } from './firebase-init.js';
import { 
    doc, getDoc, setDoc, updateDoc, deleteDoc, increment, 
    collection, query, where, orderBy, getDocs, serverTimestamp, runTransaction
} from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

// Ensure post aggregate doc exists before trying to update it
export const ensurePostDocExists = async (postSlug) => {
    const postRef = doc(db, 'posts', postSlug);
    const snap = await getDoc(postRef);
    if (!snap.exists()) {
        await setDoc(postRef, {
            likesCount: 0,
            upvotesCount: 0,
            downvotesCount: 0,
            commentsCount: 0,
            viewsCount: 0
        });
    }
    return postRef;
};

// Re-export commonly used firestore functions to keep other modules clean
export { db, doc, getDoc, setDoc, updateDoc, deleteDoc, increment, collection, query, where, orderBy, getDocs, serverTimestamp, runTransaction };
