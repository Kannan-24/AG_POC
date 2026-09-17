import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { authAPI } from '../services/api';
import { Card, Button, LoadingState } from '../components/Shared';
import '../styles/Login.css';

// Demo users data
const DEMO_USERS = [
  {
    id: 1,
    name: 'Alice',
    email: 'alice@prominence.demo',
    role: 'A&G Specialist',
    tenant: 'Prominence Health',
  },
  {
    id: 2,
    name: 'Mike',
    email: 'mike@prominence.demo',
    role: 'Medical Director',
    tenant: 'Prominence Health',
  },
  {
    id: 3,
    name: 'Bob',
    email: 'bob@demohealth.demo',
    role: 'Supervisor',
    tenant: 'Demo Health Plan',
  },
  {
    id: 4,
    name: 'Sara',
    email: 'sara@demohealth.demo',
    role: 'Tenant Administrator',
    tenant: 'Demo Health Plan',
  },
];

const TENANTS = [
  { name: 'Prominence Health', users: [DEMO_USERS[0], DEMO_USERS[1]] },
  { name: 'Demo Health Plan', users: [DEMO_USERS[2], DEMO_USERS[3]] },
];

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [selectedUser, setSelectedUser] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleUserSelect = async (user) => {
    setIsLoading(true);
    setError(null);

    try {
      // Call demo login
      const response = await authAPI.demoLogin(user.id);
      const { access_token, token_type, tenant_id, role } = response.data;

      // Fetch current user info
      localStorage.setItem('token', access_token);
      const userResponse = await authAPI.getCurrentUser();
      const currentUser = userResponse.data;

      // Fetch permissions
      const permissionsResponse = await authAPI.getUserPermissions();
      const { permissions } = permissionsResponse.data;

      // Login
      login(currentUser, access_token);

      // Store permissions
      localStorage.setItem('permissions', JSON.stringify(permissions));

      // Redirect to dashboard
      navigate('/dashboard');
    } catch (err) {
      console.error('Login failed:', err);
      setError('Login failed. Please try again.');
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return <LoadingState />;
  }

  return (
    <div className="login-container">
      <div className="login-card">
        <div className="login-header">
          <h1>Prominence Health A&G</h1>
          <p className="login-subtitle">SaaS RBAC & Multi-Tenant POC</p>
        </div>

        {error && <div className="login-error">{error}</div>}

        <div className="login-content">
          {TENANTS.map((tenant) => (
            <div key={tenant.name} className="tenant-group">
              <h2 className="tenant-name">{tenant.name}</h2>
              <div className="users-grid">
                {tenant.users.map((user) => (
                  <Button
                    key={user.id}
                    onClick={() => handleUserSelect(user)}
                    className="user-card"
                    variant="secondary"
                  >
                    <div className="user-name">{user.name}</div>
                    <div className="user-role">{user.role}</div>
                  </Button>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
