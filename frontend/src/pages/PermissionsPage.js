import React, { useEffect, useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { rolesAPI } from '../services/api';
import { Card, LoadingState, ErrorState } from '../components/Shared';
import '../styles/Permissions.css';

export function PermissionsPage() {
  const { hasPermission } = usePermissions();
  const [roles, setRoles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchRoles();
  }, []);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const response = await rolesAPI.getAll();
      
      // Fetch permissions for each role
      const rolesWithPerms = await Promise.all(
        response.data.map(async (role) => {
          try {
            const permsResponse = await rolesAPI.getPermissions(role.id);
            return {
              ...role,
              permissions: permsResponse.data,
            };
          } catch {
            return { ...role, permissions: [] };
          }
        })
      );
      
      setRoles(rolesWithPerms);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch roles:', err);
      setError('Failed to load roles and permissions');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchRoles} />;
  }

  const PERMISSION_NAMES = [
    'view_cases',
    'create_case',
    'edit_case',
    'reassign_case',
    'sign_decision',
    'view_audit',
    'configure_tenant',
  ];

  return (
    <div className="permissions-container">
      <div className="permissions-header">
        <h1>Roles & Permissions Matrix</h1>
        <p>Role-based access control for your organization</p>
      </div>

      <Card className="permissions-matrix-card">
        <div className="permissions-matrix">
          <table>
            <thead>
              <tr>
                <th>Role</th>
                {PERMISSION_NAMES.map((perm) => (
                  <th key={perm} className="perm-header">
                    {perm}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {roles.map((role) => (
                <tr key={role.id}>
                  <td className="role-name">
                    <strong>{role.name}</strong>
                  </td>
                  {PERMISSION_NAMES.map((perm) => {
                    const hasPermission = role.permissions?.some(
                      (p) => p.name === perm
                    );
                    return (
                      <td key={`${role.id}-${perm}`} className="perm-cell">
                        {hasPermission ? (
                          <span className="perm-check">✓</span>
                        ) : (
                          <span className="perm-empty">—</span>
                        )}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </div>
  );
}
