import { initializeApp } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-app.js";
import { getAuth } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-auth.js";
import { getFirestore } from "https://www.gstatic.com/firebasejs/10.9.0/firebase-firestore.js";

const firebaseConfig = {
  apiKey: "AIzaSyAA8cxhNcIrm1DwLmkjRZJn2ateX2e7Z8Q",
  authDomain: "mantbytes-f47ca.firebaseapp.com",
  projectId: "mantbytes-f47ca",
  storageBucket: "mantbytes-f47ca.firebasestorage.app",
  messagingSenderId: "629672485015",
  appId: "1:629672485015:web:5e3f6bf8e89c8b1c97c9d2"
};

const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const db = getFirestore(app);

export { app, auth, db };
