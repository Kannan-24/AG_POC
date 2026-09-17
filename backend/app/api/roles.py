"""Roles API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import AuthContext, get_current_auth_context, PermissionChecker
from app.services import AuthService, AuditService
from app.repositories import RoleRepository, PermissionRepository
from app.schemas import RoleResponse, PermissionResponse

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("", response_model=list[RoleResponse])
async def get_roles(
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get all roles for current tenant."""
    auth_service = AuthService(db)
    audit_service = AuditService(db)
    role_repo = RoleRepository(db)
    
    # Get roles
    roles = await role_repo.get_all_by_tenant(auth_context.tenant_id)
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="VIEW_ROLES",
        entity_type="ROLE_LIST",
        result="ALLOWED",
    )
    
    return roles


@router.get("/{role_id}/permissions", response_model=list[PermissionResponse])
async def get_role_permissions(
    role_id: int,
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get permissions for a role."""
    auth_service = AuthService(db)
    audit_service = AuditService(db)
    role_repo = RoleRepository(db)
    
    # Get role permissions
    permissions = await role_repo.get_permissions_by_role_id(role_id, auth_context.tenant_id)
    
    if not permissions and not await role_repo.get_by_id(role_id, auth_context.tenant_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found",
        )
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="VIEW_PERMISSIONS",
        entity_type="ROLE",
        entity_id=str(role_id),
        result="ALLOWED",
    )
    
    return permissions
