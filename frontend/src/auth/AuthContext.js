import React, { useState, useCallback } from 'react';

const AuthContext = React.createContext(null);

export function AuthProvider({ children }) {
  const [currentUser, setCurrentUser] = useState(null);
  const [permissions, setPermissions] = useState([]);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const login = useCallback((userData, token) => {
    setCurrentUser(userData);
    setIsAuthenticated(true);
    localStorage.setItem('token', token);
  }, []);

  const logout = useCallback(() => {
    setCurrentUser(null);
    setPermissions([]);
    setIsAuthenticated(false);
    localStorage.removeItem('token');
  }, []);

  const setUserPermissions = useCallback((userPermissions) => {
    setPermissions(userPermissions);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        currentUser,
        permissions,
        isAuthenticated,
        login,
        logout,
        setUserPermissions,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = React.useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider');
  }
  return context;
}
