import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { casesAPI } from '../services/api';
import { Card, Button, StatusBadge, LoadingState, ErrorState } from '../components/Shared';
import '../styles/Cases.css';

export function CasesPage() {
  const { currentUser } = useAuth();
  const { hasPermission } = usePermissions();
  const navigate = useNavigate();
  const [cases, setCases] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchCases();
  }, []);

  const fetchCases = async () => {
    try {
      setLoading(true);
      const response = await casesAPI.getAll();
      setCases(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch cases:', err);
      setError('Failed to load cases');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchCases} />;
  }

  return (
    <div className="cases-container">
      <div className="cases-header">
        <h1>Cases</h1>
        {hasPermission('create_case') && (
          <Button onClick={() => navigate('/cases/new')} variant="primary">
            Create Case
          </Button>
        )}
      </div>

      <div className="cases-table">
        <table>
          <thead>
            <tr>
              <th>Case ID</th>
              <th>Member Name</th>
              <th>Status</th>
              <th>Assigned To</th>
              <th>Tenant</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {cases.length === 0 ? (
              <tr>
                <td colSpan="6" className="text-center">
                  No cases available
                </td>
              </tr>
            ) : (
              cases.map((caseItem) => (
                <tr key={caseItem.id}>
                  <td className="case-id">{caseItem.case_number}</td>
                  <td>{caseItem.member_name}</td>
                  <td>
                    <StatusBadge status={caseItem.status} />
                  </td>
                  <td>{caseItem.assigned_to || '-'}</td>
                  <td>{currentUser.tenant_name}</td>
                  <td>
                    <Button
                      onClick={() => navigate(`/cases/${caseItem.id}`)}
                      variant="secondary"
                      className="small-btn"
                    >
                      View
                    </Button>
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
