import React, { useContext } from 'react';
import { Navigate } from 'react-router-dom';
import { AuthContext } from './AuthContext'; 

const ProtectedRoute = ({ children, redirectTo }) => {
    const { user } = useContext(AuthContext); 

    if (!user) {
        return <Navigate to={redirectTo} replace />;
    }

    return children;
};

export default ProtectedRoute;
