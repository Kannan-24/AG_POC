"""Cases API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import AuthContext, get_current_auth_context, PermissionChecker
from app.services import CaseService, AuthService, AuditService
from app.schemas import CaseCreate, CaseResponse, CaseUpdate

router = APIRouter(prefix="/cases", tags=["cases"])


@router.get("", response_model=list[CaseResponse])
async def get_cases(
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get all cases for current tenant - requires view_cases permission."""
    auth_service = AuthService(db)
    case_service = CaseService(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("view_cases")
    
    # Get cases
    cases = await case_service.get_all_cases(auth_context.tenant_id)
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="VIEW_CASES",
        entity_type="CASE_LIST",
        result="ALLOWED",
    )
    
    return cases


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: int,
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific case - requires view_cases permission."""
    auth_service = AuthService(db)
    case_service = CaseService(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("view_cases")
    
    # Get case
    case = await case_service.get_case(case_id, auth_context.tenant_id)
    if not case:
        # Audit denied access
        await audit_service.log_action(
            tenant_id=auth_context.tenant_id,
            actor_id=auth_context.user_id,
            actor_role=auth_context.role_name,
            action="VIEW_CASE",
            entity_type="CASE",
            entity_id=str(case_id),
            result="DENIED",
            details="Case not found or not in tenant",
        )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="VIEW_CASE",
        entity_type="CASE",
        entity_id=str(case_id),
        result="ALLOWED",
    )
    
    return case


@router.post("", response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Create a new case - requires create_case permission."""
    auth_service = AuthService(db)
    case_service = CaseService(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("create_case")
    
    # Create case
    case = await case_service.create_case(
        tenant_id=auth_context.tenant_id,
        case_number=case_data.case_number,
        member_name=case_data.member_name,
        status=case_data.status,
        assigned_to=case_data.assigned_to,
    )
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="CREATE_CASE",
        entity_type="CASE",
        entity_id=str(case.id),
        result="ALLOWED",
    )
    
    return case


@router.patch("/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: int,
    case_data: CaseUpdate,
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Update a case - requires edit_case permission."""
    auth_service = AuthService(db)
    case_service = CaseService(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("edit_case")
    
    # Update case
    update_data = case_data.model_dump(exclude_unset=True)
    case = await case_service.update_case(case_id, auth_context.tenant_id, update_data)
    
    if not case:
        # Audit denied
        await audit_service.log_action(
            tenant_id=auth_context.tenant_id,
            actor_id=auth_context.user_id,
            actor_role=auth_context.role_name,
            action="EDIT_CASE",
            entity_type="CASE",
            entity_id=str(case_id),
            result="DENIED",
            details="Case not found or not in tenant",
        )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="EDIT_CASE",
        entity_type="CASE",
        entity_id=str(case_id),
        result="ALLOWED",
    )
    
    return case


@router.post("/{case_id}/reassign", response_model=CaseResponse)
async def reassign_case(
    case_id: int,
    assigned_to: str,
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Reassign a case - requires reassign_case permission."""
    auth_service = AuthService(db)
    case_service = CaseService(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("reassign_case")
    
    # Reassign case
    case = await case_service.reassign_case(case_id, auth_context.tenant_id, assigned_to)
    
    if not case:
        # Audit denied
        await audit_service.log_action(
            tenant_id=auth_context.tenant_id,
            actor_id=auth_context.user_id,
            actor_role=auth_context.role_name,
            action="REASSIGN_CASE",
            entity_type="CASE",
            entity_id=str(case_id),
            result="DENIED",
            details="Case not found or not in tenant",
        )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="REASSIGN_CASE",
        entity_type="CASE",
        entity_id=str(case_id),
        result="ALLOWED",
        details=f"Assigned to: {assigned_to}",
    )
    
    return case


@router.post("/{case_id}/sign", response_model=CaseResponse)
async def sign_decision(
    case_id: int,
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Sign decision on a case - requires sign_decision permission."""
    auth_service = AuthService(db)
    case_service = CaseService(db)
    audit_service = AuditService(db)
    
    # Check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("sign_decision")
    
    # Sign decision
    case = await case_service.sign_decision(case_id, auth_context.tenant_id)
    
    if not case:
        # Audit denied
        await audit_service.log_action(
            tenant_id=auth_context.tenant_id,
            actor_id=auth_context.user_id,
            actor_role=auth_context.role_name,
            action="SIGN_DECISION",
            entity_type="CASE",
            entity_id=str(case_id),
            result="DENIED",
            details="Case not found or not in tenant",
        )
        
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    
    # Audit log
    await audit_service.log_action(
        tenant_id=auth_context.tenant_id,
        actor_id=auth_context.user_id,
        actor_role=auth_context.role_name,
        action="SIGN_DECISION",
        entity_type="CASE",
        entity_id=str(case_id),
        result="ALLOWED",
    )
    
    return case
