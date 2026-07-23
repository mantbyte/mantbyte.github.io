import { db, doc, getDoc, setDoc, updateDoc, increment, ensurePostDocExists, serverTimestamp } from './firestore.js';
import { getCurrentUser } from './auth.js';

export const castVote = async (postSlug, voteValue) => {
    // voteValue: 1 for upvote, -1 for downvote, 0 to clear
    const user = getCurrentUser();
    if (!user) throw new Error("Must be logged in to vote");

    const interactionRef = doc(db, 'users', user.uid, 'interactions', postSlug);
    const postRef = doc(db, 'posts', postSlug);
    
    await ensurePostDocExists(postSlug);
    const interactionSnap = await getDoc(interactionRef);
    
    let currentVote = 0;
    if (interactionSnap.exists() && interactionSnap.data().vote !== undefined) {
        currentVote = interactionSnap.data().vote;
    }
    
    if (currentVote === voteValue) {
        // If clicking same vote, clear it
        voteValue = 0;
    }

    // Calculate diffs for aggregates
    let upDiff = 0;
    let downDiff = 0;
    
    if (currentVote === 1) upDiff = -1;
    else if (currentVote === -1) downDiff = -1;
    
    if (voteValue === 1) upDiff += 1;
    else if (voteValue === -1) downDiff += 1;

    // Update user's interaction
    await setDoc(interactionRef, { vote: voteValue, updatedAt: serverTimestamp() }, { merge: true });
    
    // Update global aggregates
    const updates = {};
    if (upDiff !== 0) updates.upvotesCount = increment(upDiff);
    if (downDiff !== 0) updates.downvotesCount = increment(downDiff);
    
    if (Object.keys(updates).length > 0) {
        await updateDoc(postRef, updates);
    }
    
    return { vote: voteValue, upDiff, downDiff };
};

export const getVoteStatus = async (postSlug) => {
    const user = getCurrentUser();
    if (!user) return 0;
    
    const interactionRef = doc(db, 'users', user.uid, 'interactions', postSlug);
    const interactionSnap = await getDoc(interactionRef);
    
    if (interactionSnap.exists() && interactionSnap.data().vote !== undefined) {
        return interactionSnap.data().vote;
    }
    return 0;
};

export const getPostVotes = async (postSlug) => {
    const postRef = doc(db, 'posts', postSlug);
    const snap = await getDoc(postRef);
    if (snap.exists()) {
        const d = snap.data();
        return { upvotes: d.upvotesCount || 0, downvotes: d.downvotesCount || 0 };
    }
    return { upvotes: 0, downvotes: 0 };
};
