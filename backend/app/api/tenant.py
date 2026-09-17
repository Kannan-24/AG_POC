"""Tenant API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import AuthContext, get_current_auth_context, PermissionChecker
from app.services import AuthService, AuditService
from app.repositories import TenantRepository
from app.schemas import TenantResponse

router = APIRouter(prefix="/tenant", tags=["tenant"])


@router.get("", response_model=TenantResponse)
async def get_tenant(
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get current tenant information."""
    tenant_repo = TenantRepository(db)
    audit_service = AuditService(db)
    
    # Get tenant
    tenant = await tenant_repo.get_by_id(auth_context.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="VIEW_TENANT",
        entity_type="TENANT",
        entity_id=str(auth_context.tenant_id),
        result="ALLOWED",
    )
    
    return tenant


@router.get("/configuration", response_model=dict)
async def get_tenant_configuration(
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get tenant configuration - requires configure_tenant permission."""
    auth_service = AuthService(db)
    tenant_repo = TenantRepository(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("configure_tenant")
    
    # Get tenant
    tenant = await tenant_repo.get_by_id(auth_context.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="VIEW_CONFIGURATION",
        entity_type="TENANT",
        entity_id=str(auth_context.tenant_id),
        result="ALLOWED",
    )
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "code": tenant.code,
        "status": tenant.status,
    }


@router.patch("/configuration", response_model=dict)
async def update_tenant_configuration(
    config_update: dict,
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Update tenant configuration - requires configure_tenant permission."""
    auth_service = AuthService(db)
    tenant_repo = TenantRepository(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("configure_tenant")
    
    # Get tenant
    tenant = await tenant_repo.get_by_id(auth_context.tenant_id)
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="CONFIGURE_TENANT",
        entity_type="TENANT",
        entity_id=str(auth_context.tenant_id),
        result="ALLOWED",
    )
    
    return {
        "id": tenant.id,
        "name": tenant.name,
        "code": tenant.code,
        "status": tenant.status,
    }
