import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { authAPI } from '../services/api';
import { Card, Button, LoadingState } from '../components/Shared';
import '../styles/Login.css';

// Demo users reference
const DEMO_USERS = [
  {
    name: 'Alice',
    email: 'alice@prominence.demo',
    role: 'A&G Specialist',
    tenant: 'Prominence Health',
  },
  {
    name: 'Mike',
    email: 'mike@prominence.demo',
    role: 'Medical Director',
    tenant: 'Prominence Health',
  },
  {
    name: 'Bob',
    email: 'bob@demohealth.demo',
    role: 'Supervisor',
    tenant: 'Demo Health Plan',
  },
  {
    name: 'Sara',
    email: 'sara@demohealth.demo',
    role: 'Tenant Administrator',
    tenant: 'Demo Health Plan',
  },
];

export function LoginPage() {
  const navigate = useNavigate();
  const { login } = useAuth();
  const [username, setUsername] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    setError(null);

    try {
      if (!username.trim()) {
        setError('Please enter a username');
        setIsLoading(false);
        return;
      }

      // Call demo login with username
      const response = await authAPI.demoLogin(username);
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
      const errorMsg = err.response?.data?.detail || 'Login failed. Please try again.';
      setError(errorMsg);
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

        <form onSubmit={handleLogin} className="login-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input
              id="username"
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              placeholder="Enter username"
              className="login-input"
              disabled={isLoading}
              autoComplete="username"
            />
          </div>

          <Button
            type="submit"
            className="login-button"
            disabled={isLoading}
          >
            {isLoading ? 'Logging in...' : 'Login'}
          </Button>
        </form>

        <div className="demo-users-list">
          <h3>Demo Users Available:</h3>
          <table className="users-table">
            <thead>
              <tr>
                <th>Username</th>
                <th>Role</th>
                <th>Tenant</th>
              </tr>
            </thead>
            <tbody>
              {DEMO_USERS.map((user) => (
                <tr key={user.name}>
                  <td className="username-cell">
                    <code>{user.name}</code>
                  </td>
                  <td>{user.role}</td>
                  <td>{user.tenant}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
