import React, { useEffect, useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import { onAuthStateChanged } from 'firebase/auth';
import { auth } from './firebase'; 
import ProtectedRoute from './ProtectedRoute';
import Login from './components/Login';
import VoiceOrder from './components/VoiceOrder';
import Signup from './components/Signup';

function App() {
    const [user, setUser] = useState(null);

    useEffect(() => {
        const unsubscribe = onAuthStateChanged(auth, (currentUser) => {
            setUser(currentUser); 
        });

        return () => unsubscribe();
    }, []);

    return (
        <AuthProvider>
            <Router>
                <Routes>
                    {/* Default route that checks if user is logged in */}
                    <Route path="/" element={user ? <Navigate to="/voice-order" replace /> : <Navigate to="/login" replace />} />

                    {/* Defined routes */}
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />
                    <Route
                        path="/voice-order"
                        element={
                            <ProtectedRoute redirectTo="/login">
                                <VoiceOrder />
                            </ProtectedRoute>
                        }
                    />
                </Routes>
            </Router>
        </AuthProvider>
    );
}

export default App;
