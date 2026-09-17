"""Authentication API routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import (
    AuthContext,
    get_current_auth_context,
    create_demo_token,
)
from app.services import AuthService, UserService
from app.schemas import (
    DemoLoginRequest,
    DemoLoginResponse,
    CurrentUserResponse,
    UserPermissionsResponse,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/demo-login", response_model=DemoLoginResponse)
async def demo_login(
    request: DemoLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Demo login endpoint - for POC only."""
    user_service = UserService(db)
    auth_service = AuthService(db)
    
    # Get user by username (name field)
    user = await user_service.get_user_by_name(request.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User '{request.username}' not found",
        )
    
    # Create token
    token = create_demo_token(
        user_id=user.id,
        tenant_id=user.tenant_id,
        role_name=user.role.name if user.role else "Unknown",
    )
    
    return DemoLoginResponse(
        access_token=token,
        token_type="bearer",
        user_id=user.id,
        tenant_id=user.tenant_id,
        role=user.role.name if user.role else "Unknown",
    )


@router.get("/me", response_model=CurrentUserResponse)
async def get_current_user(
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get current user information."""
    user_service = UserService(db)
    
    user = await user_service.get_user_any_tenant(auth_context.user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )
    
    return CurrentUserResponse(
        user_id=user.id,
        name=user.name,
        email=user.email,
        tenant_id=user.tenant_id,
        tenant_name=user.tenant.name if user.tenant else "Unknown",
        role=auth_context.role_name,
    )


@router.get("/me/permissions", response_model=UserPermissionsResponse)
async def get_user_permissions(
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    """Get current user's permissions."""
    auth_service = AuthService(db)
    
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    
    return UserPermissionsResponse(permissions=permissions)
