"""Audit API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import AuthContext, get_current_auth_context, PermissionChecker
from app.services import AuthService, AuditService
from app.schemas import AuditEventResponse

router = APIRouter(prefix="/audit", tags=["audit"])


@router.get("", response_model=list[AuditEventResponse])
async def get_audit_log(
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get audit log for current tenant - requires view_audit permission."""
    auth_service = AuthService(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("view_audit")
    
    # Get audit events
    events = await audit_service.get_audit_events(auth_context.tenant_id)
    
    # Audit log the audit access itself
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="VIEW_AUDIT",
        entity_type="AUDIT",
        result="ALLOWED",
    )
    
    return events
