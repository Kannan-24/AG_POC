import { useAuth } from '../auth/AuthContext';

export function usePermissions() {
  const { permissions } = useAuth();

  return {
    hasPermission: (permission) => permissions.includes(permission),
    permissions,
  };
}
