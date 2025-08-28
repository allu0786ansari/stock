// src/components/firebase.js
import { initializeApp, getApps, getApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getDatabase } from "firebase/database";
import { getFirestore } from "firebase/firestore";

// ✅ Use .env variables (set these in your .env file)
const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
  // 👇 Only include if you need analytics
  measurementId: process.env.REACT_APP_FIREBASE_MEASUREMENT_ID,
  // 👇 Only include if you enable Realtime Database
  databaseURL: process.env.REACT_APP_FIREBASE_DATABASE_URL,
};

// Avoid initializing twice
const app = !getApps().length ? initializeApp(firebaseConfig) : getApp();

const auth = getAuth(app);
const database = getDatabase(app);
const db = getFirestore(app);

export { auth, database, db, app };
