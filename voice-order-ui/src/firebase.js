// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";
// TODO: Add SDKs for Firebase products that you want to use
// https://firebase.google.com/docs/web/setup#available-libraries

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: "AIzaSyBgBuu4u7sDTeehmPgiMXrSrFiYE3Twbb8",
  authDomain: "voice-order-assistant.firebaseapp.com",
  projectId: "voice-order-assistant",
  storageBucket: "voice-order-assistant.firebasestorage.app",
  messagingSenderId: "628014903875",
  appId: "1:628014903875:web:ed785cdb6e947ecf989af6",
  measurementId: "G-7P8TY6470X"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
export const auth = getAuth(app);