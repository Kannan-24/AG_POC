import React, { useEffect, useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { Card, StatCard, LoadingState, ErrorState } from '../components/Shared';
import '../styles/Dashboard.css';

export function DashboardPage() {
  const { currentUser } = useAuth();
  const { hasPermission, permissions } = usePermissions();
  const [loading, setLoading] = useState(false);

  if (!currentUser) {
    return <LoadingState />;
  }

  return (
    <div className="dashboard-container">
      <div className="dashboard-header">
        <h1>Dashboard</h1>
        <p>Welcome, {currentUser.name}!</p>
      </div>

      <div className="dashboard-stats">
        <StatCard
          label="Tenant"
          value={currentUser.tenant_name}
          icon="🏢"
        />
        <StatCard
          label="Current User"
          value={currentUser.name}
          icon="👤"
        />
        <StatCard
          label="Role"
          value={currentUser.role}
          icon="👔"
        />
        <StatCard
          label="Permissions"
          value={permissions.length}
          icon="🔐"
        />
      </div>

      <div className="dashboard-content">
        <Card className="permissions-card">
          <h2>Your Permissions</h2>
          <div className="permissions-list">
            {permissions.length === 0 ? (
              <p>No permissions assigned</p>
            ) : (
              <ul>
                {permissions.map((perm) => (
                  <li key={perm} className="permission-item">
                    <span className="permission-check">✓</span>
                    <span className="permission-name">{perm}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
