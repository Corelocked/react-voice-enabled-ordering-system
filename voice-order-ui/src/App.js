import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import { AuthProvider } from './AuthContext';
import ProtectedRoute from './ProtectedRoute';
import Login from './components/Login';
import VoiceOrder from './components/VoiceOrder';

function App() {
    return (
        <AuthProvider>
            <Router>
                <Routes>
                    {/* Default route that redirects to login */}
                    <Route path="/" element={<Navigate to="/login" replace />} />
                    
                    {/* Defined routes */}
                    <Route path="/login" element={<Login />} />
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
