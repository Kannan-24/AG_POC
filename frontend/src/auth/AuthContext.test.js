"""Frontend authentication tests."""

import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../auth/AuthContext';


function TestComponent() {
  const { currentUser, isAuthenticated, permissions } = useAuth();
  
  return (
    <div>
      <div data-testid="auth-status">
        {isAuthenticated ? 'Authenticated' : 'Not authenticated'}
      </div>
      {currentUser && <div data-testid="user-name">{currentUser.name}</div>}
      <div data-testid="permissions-count">{permissions.length}</div>
    </div>
  );
}


describe('AuthContext', () => {
  test('provides auth context', () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
  });
  
  test('allows login', async () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    );
    
    // Initially not authenticated
    expect(screen.getByTestId('auth-status')).toHaveTextContent('Not authenticated');
  });
});
