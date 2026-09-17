import React, { useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './auth/AuthContext';
import { ProtectedRoute } from './auth/ProtectedRoute';
import { usePermissions } from './hooks/usePermissions';

// Pages
import { LoginPage } from './pages/LoginPage';
import { DashboardPage } from './pages/DashboardPage';
import { CasesPage } from './pages/CasesPage';
import { CaseDetailPage } from './pages/CaseDetailPage';
import { AuditPage } from './pages/AuditPage';
import { PermissionsPage } from './pages/PermissionsPage';

// Components
import { AppShell, AppHeader, AppSidebar, AppMain } from './components/AppShell';
import { authAPI } from './services/api';

import './App.css';

function AppLayout({ children }) {
  const { currentUser, logout } = useAuth();
  const { hasPermission } = usePermissions();
  const navigate = useNavigate();
  const location = useLocation();

  const isLoginPage = location.pathname === '/login';

  if (isLoginPage) {
    return children;
  }

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navItems = [
    { label: 'Dashboard', path: '/dashboard', icon: '📊' },
    { label: 'Cases', path: '/cases', icon: '📋', show: true },
    { label: 'Roles & Permissions', path: '/permissions', icon: '🔐', show: true },
    { label: 'Audit Log', path: '/audit', icon: '📝', show: hasPermission('view_audit') },
  ];

  return (
    <AppShell>
      <AppHeader
        title="Prominence Health A&G"
        subtitle={currentUser ? `${currentUser.tenant_name} - ${currentUser.role}` : ''}
      />
      <div className="app-container-main">
        <AppSidebar>
          {navItems.filter(item => item.show !== false).map((item) => (
            <a
              key={item.path}
              href={item.path}
              className={`nav-link ${location.pathname === item.path ? 'active' : ''}`}
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </a>
          ))}
          <button className="nav-logout" onClick={handleLogout}>
            🚪 Logout
          </button>
        </AppSidebar>
        <AppMain>{children}</AppMain>
      </div>
    </AppShell>
  );
}

function AppContent() {
  const { isAuthenticated } = useAuth();
  const navigate = useNavigate();

  // Load permissions on app load if authenticated
  useEffect(() => {
    if (isAuthenticated) {
      authAPI.getUserPermissions()
        .then(response => {
          localStorage.setItem('permissions', JSON.stringify(response.data.permissions));
          window.location.reload(); // Reload to get updated permissions
        })
        .catch(err => console.error('Failed to load permissions:', err));
    }
  }, [isAuthenticated]);

  if (!isAuthenticated && window.location.pathname !== '/login') {
    return <Navigate to="/login" replace />;
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/dashboard"
        element={
          <ProtectedRoute>
            <DashboardPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/cases"
        element={
          <ProtectedRoute>
            <CasesPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/cases/:caseId"
        element={
          <ProtectedRoute>
            <CaseDetailPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/audit"
        element={
          <ProtectedRoute>
            <AuditPage />
          </ProtectedRoute>
        }
      />
      <Route
        path="/permissions"
        element={
          <ProtectedRoute>
            <PermissionsPage />
          </ProtectedRoute>
        }
      />
      <Route path="/" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppLayout>
          <AppContent />
        </AppLayout>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
