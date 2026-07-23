import { db, doc, collection, setDoc, getDocs, query, orderBy, serverTimestamp, increment, updateDoc, ensurePostDocExists } from './firestore.js';
import { getCurrentUser } from './auth.js';

export const addComment = async (postSlug, content) => {
    const user = getCurrentUser();
    if (!user) throw new Error("Must be logged in to comment");
    if (!content.trim()) throw new Error("Comment cannot be empty");

    await ensurePostDocExists(postSlug);

    const commentsRef = collection(db, 'posts', postSlug, 'comments');
    const newCommentRef = doc(commentsRef); // Auto-generate ID

    await setDoc(newCommentRef, {
        authorUid: user.uid,
        authorName: user.displayName || "Anonymous",
        authorPhoto: user.photoURL || "",
        content: content.trim(),
        createdAt: serverTimestamp(),
        likesCount: 0
    });

    const postRef = doc(db, 'posts', postSlug);
    await updateDoc(postRef, { commentsCount: increment(1) });

    return {
        id: newCommentRef.id,
        authorName: user.displayName,
        authorPhoto: user.photoURL,
        content: content.trim()
    };
};

export const getComments = async (postSlug) => {
    const commentsRef = collection(db, 'posts', postSlug, 'comments');
    const q = query(commentsRef, orderBy('createdAt', 'desc'));
    const snapshot = await getDocs(q);
    
    return snapshot.docs.map(doc => ({
        id: doc.id,
        ...doc.data()
    }));
};
