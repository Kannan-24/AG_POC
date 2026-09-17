"""Authorization decorators and helpers."""

from functools import wraps
from fastapi import HTTPException, status
from app.auth.context import AuthContext


def require_permission(required_permission: str):
    """Decorator to require specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get auth context from kwargs
            auth_context: AuthContext = kwargs.get("auth_context")
            
            if not auth_context:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
            
            # Permissions are checked in the route handler
            # This decorator is mainly for documentation
            return await func(*args, **kwargs)
        return wrapper
    return decorator


class PermissionChecker:
    """Helper class to check permissions."""
    
    def __init__(self, permissions: list):
        """Initialize with user permissions."""
        self.permissions = permissions
    
    def has_permission(self, permission: str) -> bool:
        """Check if user has a specific permission."""
        return permission in self.permissions
    
    def require_permission(self, permission: str) -> None:
        """Require a permission, raise 403 if not present."""
        if not self.has_permission(permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permission: {permission}",
            )
    
    def require_any_permission(self, permissions: list) -> None:
        """Require at least one permission from list."""
        if not any(p in self.permissions for p in permissions):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Missing required permissions",
            )
    
    def require_all_permissions(self, permissions: list) -> None:
        """Require all permissions from list."""
        missing = [p for p in permissions if p not in self.permissions]
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing)}",
            )
