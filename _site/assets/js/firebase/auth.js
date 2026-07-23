import { auth, db } from './firebase-init.js';
import { 
    GoogleAuthProvider, 
    signInWithPopup, 
    signOut, 
    onAuthStateChanged 
} from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { doc, setDoc, getDoc, serverTimestamp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

const provider = new GoogleAuthProvider();

export const loginWithGoogle = async () => {
    try {
        const result = await signInWithPopup(auth, provider);
        const user = result.user;
        
        // Ensure user profile exists in Firestore
        const userRef = doc(db, 'users', user.uid);
        const userSnap = await getDoc(userRef);
        
        if (!userSnap.exists()) {
            await setDoc(userRef, {
                uid: user.uid,
                displayName: user.displayName,
                photoURL: user.photoURL,
                email: user.email,
                createdAt: serverTimestamp(),
                preferences: {
                    theme: 'system',
                    emailNotifications: true
                }
            });
        }
        
        return user;
    } catch (error) {
        console.error("Login failed:", error);
        throw error;
    }
};

export const logout = async () => {
    try {
        await signOut(auth);
    } catch (error) {
        console.error("Logout failed:", error);
        throw error;
    }
};

export const observeAuthState = (callback) => {
    return onAuthStateChanged(auth, callback);
};

export const getCurrentUser = () => auth.currentUser;
