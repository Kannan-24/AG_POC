import React from 'react';
import '../styles/Shared.css';

export function Card({ children, className = '' }) {
  return <div className={`card ${className}`}>{children}</div>;
}

export function Button({
  children,
  onClick,
  className = '',
  variant = 'primary',
  disabled = false,
  ...props
}) {
  return (
    <button
      className={`btn btn-${variant} ${className}`}
      onClick={onClick}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  );
}

export function StatCard({ label, value, icon }) {
  return (
    <Card className="stat-card">
      <div className="stat-icon">{icon}</div>
      <div className="stat-content">
        <p className="stat-label">{label}</p>
        <p className="stat-value">{value}</p>
      </div>
    </Card>
  );
}

export function StatusBadge({ status }) {
  const statusClasses = {
    active: 'badge-success',
    open: 'badge-warning',
    closed: 'badge-secondary',
    'in-progress': 'badge-info',
    signed: 'badge-success',
    denied: 'badge-danger',
  };

  return (
    <span className={`badge ${statusClasses[status] || 'badge-secondary'}`}>
      {status}
    </span>
  );
}

export function Table({ columns, data, onRowClick }) {
  return (
    <div className="table-container">
      <table className="table">
        <thead>
          <tr>
            {columns.map((col) => (
              <th key={col.key} style={{ width: col.width }}>
                {col.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.length === 0 ? (
            <tr>
              <td colSpan={columns.length} className="text-center">
                No data available
              </td>
            </tr>
          ) : (
            data.map((row, idx) => (
              <tr
                key={idx}
                onClick={() => onRowClick?.(row)}
                className={onRowClick ? 'cursor-pointer hover:bg-gray-50' : ''}
              >
                {columns.map((col) => (
                  <td key={col.key}>
                    {col.render ? col.render(row[col.key], row) : row[col.key]}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}

export function LoadingState() {
  return (
    <div className="loading-container">
      <div className="spinner"></div>
      <p>Loading...</p>
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <Card className="error-state">
      <p className="error-message">⚠️ {message}</p>
      {onRetry && (
        <Button onClick={onRetry} variant="secondary">
          Retry
        </Button>
      )}
    </Card>
  );
}

export function EmptyState({ message }) {
  return (
    <Card className="empty-state">
      <p className="empty-message">{message}</p>
    </Card>
  );
}
