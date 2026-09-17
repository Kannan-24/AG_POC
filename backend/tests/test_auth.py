"""Test RBAC authorization."""

import pytest
from app.auth import create_demo_token, PermissionChecker
from fastapi import HTTPException, status


def test_create_demo_token():
    """Test JWT token creation."""
    token = create_demo_token(user_id=1, tenant_id=1, role_name="Admin")
    assert token is not None
    assert isinstance(token, str)


def test_permission_checker_has_permission():
    """Test permission checker for single permission."""
    permissions = ["view_cases", "create_case", "edit_case"]
    checker = PermissionChecker(permissions)
    
    assert checker.has_permission("view_cases") is True
    assert checker.has_permission("sign_decision") is False


def test_permission_checker_require_permission():
    """Test requiring a specific permission."""
    permissions = ["view_cases", "create_case"]
    checker = PermissionChecker(permissions)
    
    # Should not raise
    checker.require_permission("view_cases")
    
    # Should raise
    with pytest.raises(HTTPException) as exc_info:
        checker.require_permission("sign_decision")
    
    assert exc_info.value.status_code == status.HTTP_403_FORBIDDEN


def test_permission_checker_require_any():
    """Test requiring at least one permission."""
    permissions = ["view_cases", "create_case"]
    checker = PermissionChecker(permissions)
    
    # Should not raise (has one of them)
    checker.require_any_permission(["view_cases", "sign_decision"])
    
    # Should raise (has none of them)
    with pytest.raises(HTTPException):
        checker.require_any_permission(["sign_decision", "view_audit"])


def test_permission_checker_require_all():
    """Test requiring all permissions."""
    permissions = ["view_cases", "create_case", "edit_case"]
    checker = PermissionChecker(permissions)
    
    # Should not raise (has all)
    checker.require_all_permissions(["view_cases", "create_case"])
    
    # Should raise (missing one)
    with pytest.raises(HTTPException):
        checker.require_all_permissions(["view_cases", "sign_decision"])
