import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../auth/AuthContext';
import { usePermissions } from '../hooks/usePermissions';
import { casesAPI } from '../services/api';
import { Card, Button, StatusBadge, LoadingState, ErrorState } from '../components/Shared';
import '../styles/Cases.css';

export function CaseDetailPage() {
  const { caseId } = useParams();
  const { currentUser } = useAuth();
  const { hasPermission } = usePermissions();
  const navigate = useNavigate();
  const [caseData, setCaseData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editData, setEditData] = useState({});

  useEffect(() => {
    fetchCase();
  }, [caseId]);

  const fetchCase = async () => {
    try {
      setLoading(true);
      const response = await casesAPI.getById(caseId);
      setCaseData(response.data);
      setEditData(response.data);
      setError(null);
    } catch (err) {
      console.error('Failed to fetch case:', err);
      setError('Case not found or access denied');
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await casesAPI.update(caseId, editData);
      setCaseData(editData);
      setIsEditing(false);
      setError(null);
    } catch (err) {
      console.error('Failed to update case:', err);
      setError('Failed to update case');
    }
  };

  const handleReassign = async () => {
    const newAssignee = prompt('Enter new assignee:');
    if (newAssignee) {
      try {
        await casesAPI.reassign(caseId, newAssignee);
        await fetchCase();
      } catch (err) {
        setError('Failed to reassign case');
      }
    }
  };

  const handleSign = async () => {
    try {
      await casesAPI.sign(caseId);
      await fetchCase();
    } catch (err) {
      setError('Failed to sign decision');
    }
  };

  if (loading) {
    return <LoadingState />;
  }

  if (error) {
    return <ErrorState message={error} onRetry={fetchCase} />;
  }

  if (!caseData) {
    return <ErrorState message="Case not found" />;
  }

  return (
    <div className="case-detail-container">
      <div className="case-detail-header">
        <h1>{caseData.case_number}</h1>
        <Button onClick={() => navigate('/cases')} variant="secondary">
          ← Back
        </Button>
      </div>

      <Card className="case-detail-card">
        <div className="case-detail-grid">
          <div className="case-field">
            <label>Case ID</label>
            <p>{caseData.case_number}</p>
          </div>
          <div className="case-field">
            <label>Member Name</label>
            {isEditing ? (
              <input
                type="text"
                value={editData.member_name}
                onChange={(e) =>
                  setEditData({ ...editData, member_name: e.target.value })
                }
              />
            ) : (
              <p>{caseData.member_name}</p>
            )}
          </div>
          <div className="case-field">
            <label>Status</label>
            {isEditing ? (
              <select
                value={editData.status}
                onChange={(e) =>
                  setEditData({ ...editData, status: e.target.value })
                }
              >
                <option value="open">Open</option>
                <option value="in-progress">In Progress</option>
                <option value="closed">Closed</option>
              </select>
            ) : (
              <StatusBadge status={caseData.status} />
            )}
          </div>
          <div className="case-field">
            <label>Assigned To</label>
            <p>{caseData.assigned_to || '-'}</p>
          </div>
          <div className="case-field">
            <label>Tenant</label>
            <p>{currentUser.tenant_name}</p>
          </div>
          <div className="case-field">
            <label>Created Date</label>
            <p>{new Date(caseData.created_at).toLocaleDateString()}</p>
          </div>
        </div>

        <div className="case-actions">
          {hasPermission('edit_case') && !isEditing && (
            <Button onClick={() => setIsEditing(true)} variant="primary">
              Edit
            </Button>
          )}
          {isEditing && (
            <>
              <Button onClick={handleSave} variant="primary">
                Save
              </Button>
              <Button onClick={() => setIsEditing(false)} variant="secondary">
                Cancel
              </Button>
            </>
          )}
          {hasPermission('reassign_case') && (
            <Button onClick={handleReassign} variant="secondary">
              Reassign
            </Button>
          )}
          {hasPermission('sign_decision') && (
            <Button onClick={handleSign} variant="success">
              Sign Decision
            </Button>
          )}
        </div>
      </Card>

      {error && (
        <Card className="error-message">
          <p>❌ {error}</p>
        </Card>
      )}
    </div>
  );
}
