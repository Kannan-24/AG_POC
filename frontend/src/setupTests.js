"""Frontend test configuration."""

import '@testing-library/jest-dom';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;

// Mock API calls
jest.mock('./services/api', () => ({
  authAPI: {
    demoLogin: jest.fn(() => Promise.resolve({
      data: {
        access_token: 'test-token',
        user_id: 1,
        tenant_id: 1,
        role: 'Admin',
      },
    })),
    getCurrentUser: jest.fn(() => Promise.resolve({
      data: {
        user_id: 1,
        name: 'Test User',
        email: 'test@example.com',
        tenant_id: 1,
        tenant_name: 'Test Tenant',
        role: 'Admin',
      },
    })),
    getUserPermissions: jest.fn(() => Promise.resolve({
      data: {
        permissions: ['view_cases', 'create_case'],
      },
    })),
  },
  casesAPI: {
    getAll: jest.fn(),
    getById: jest.fn(),
    create: jest.fn(),
    update: jest.fn(),
    reassign: jest.fn(),
    sign: jest.fn(),
  },
}));
