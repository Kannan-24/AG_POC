import React, { useEffect, useState } from 'react';
import { useAuth } from '../auth/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { auditAPI } from '../services/api';
import { Card, LoadingState, ErrorState, StatusBadge } from '../components/Shared';
import '../styles/Audit.css';

export function AuditPage() {
  const { currentUser } = useAuth();
  const { hasPermission } = usePermissions();
  const [events, setEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAuditLog();
  }, []);

  const fetchAuditLog = async () => {
    try {
      setLoading(true);
      const response = await auditAPI.getLog();
      setEvents(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch audit log:', err);
      setError('Failed to load audit log');
    } finally {
      setLoading(false);
    }
  };

  if (!hasPermission('view_audit')) {
    return (
      <Card className="access-denied">
        <h2>Access Denied</h2>
        <p>You do not have permission to view the audit log.</p>
      </Card>
    );
  }

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchAuditLog} />;
  }

  return (
    <div className="audit-container">
      <div className="audit-header">
        <h1>Audit Log</h1>
        <p>Tenant: {currentUser.tenant_name}</p>
      </div>

      <div className="audit-table">
        <table>
          <thead>
            <tr>
              <th>Timestamp</th>
              <th>User</th>
              <th>Role</th>
              <th>Action</th>
              <th>Entity</th>
              <th>Result</th>
            </tr>
          </thead>
          <tbody>
            {events.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center">
                  No audit events
                </td>
              </tr>
            ) : (
              events.map((event) => (
                <tr key={event.id}>
                  <td className="timestamp">
                    {new Date(event.created_at).toLocaleString()}
                  </td>
                  <td>{event.actor_role}</td>
                  <td>{event.actor_role}</td>
                  <td className="action-name">{event.action}</td>
                  <td>
                    {event.entity_type} {event.entity_id ? `(${event.entity_id})` : ''}
                  </td>
                  <td>
                    <StatusBadge
                      status={event.result === 'ALLOWED' ? 'success' : 'danger'}
                    />
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
