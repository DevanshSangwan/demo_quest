import { initializeApp } from 'firebase/app';
import { getAuth } from 'firebase/auth';

const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY || "AIzaSyBFfX-PyAg2r9l83fe_T1XpUlyMckqj818",
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN || "tonequest-79260.firebaseapp.com",
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID || "tonequest-79260",
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET || "tonequest-79260.appspot.com",
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID || "",
  appId: import.meta.env.VITE_FIREBASE_APP_ID || "",
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);