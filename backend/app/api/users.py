"""Users API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import AuthContext, get_current_auth_context, PermissionChecker
from app.services import UserService, AuthService, AuditService
from app.schemas import UserResponse

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=list[UserResponse])
async def get_users(
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get all users in current tenant - requires configure_tenant permission."""
    auth_service = AuthService(db)
    user_service = UserService(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("configure_tenant")
    
    # Get users
    users = await user_service.get_users_by_tenant(auth_context.tenant_id)
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="VIEW_USERS",
        entity_type="USER_LIST",
        result="ALLOWED",
    )
    
    return users
