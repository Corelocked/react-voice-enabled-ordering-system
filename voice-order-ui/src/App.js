// App.js
import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import VoiceOrder from './components/VoiceOrder';
import Login from './components/Login';
import Signup from './components/Signup';

function App() {
    return (
        <Router>
            <div className="App">
                <Routes>
                    <Route path="/" element={<Navigate to="/login" />} />
                    <Route path="/login" element={<Login />} />
                    <Route path="/signup" element={<Signup />} />
                    <Route path="/voice-order" element={<VoiceOrder />} />
                </Routes>
            </div>
        </Router>
    );
}

export default App;
