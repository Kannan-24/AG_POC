"""Pydantic schemas for API requests and responses."""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


# Tenant Schemas
class TenantBase(BaseModel):
    """Base tenant schema."""
    name: str
    code: str
    status: str = "active"


class TenantCreate(TenantBase):
    """Schema for creating a tenant."""
    pass


class TenantResponse(TenantBase):
    """Schema for tenant response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Permission Schemas
class PermissionBase(BaseModel):
    """Base permission schema."""
    name: str
    description: Optional[str] = None


class PermissionCreate(PermissionBase):
    """Schema for creating a permission."""
    pass


class PermissionResponse(PermissionBase):
    """Schema for permission response."""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Role Schemas
class RoleBase(BaseModel):
    """Base role schema."""
    name: str
    description: Optional[str] = None


class RoleCreate(RoleBase):
    """Schema for creating a role."""
    pass


class RoleResponse(RoleBase):
    """Schema for role response."""
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    permissions: List[PermissionResponse] = []
    
    class Config:
        from_attributes = True


# User Schemas
class UserBase(BaseModel):
    """Base user schema."""
    name: str
    email: str
    role_id: int
    status: str = "active"


class UserCreate(UserBase):
    """Schema for creating a user."""
    pass


class UserResponse(UserBase):
    """Schema for user response."""
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Case Schemas
class CaseBase(BaseModel):
    """Base case schema."""
    case_number: str
    member_name: str
    status: str = "open"
    assigned_to: Optional[str] = None


class CaseCreate(CaseBase):
    """Schema for creating a case."""
    pass


class CaseUpdate(BaseModel):
    """Schema for updating a case."""
    member_name: Optional[str] = None
    status: Optional[str] = None
    assigned_to: Optional[str] = None


class CaseResponse(CaseBase):
    """Schema for case response."""
    id: int
    tenant_id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Audit Event Schemas
class AuditEventResponse(BaseModel):
    """Schema for audit event response."""
    id: int
    tenant_id: int
    actor_id: int
    actor_role: Optional[str] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[str] = None
    result: str
    details: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


# Auth Schemas
class CurrentUserResponse(BaseModel):
    """Schema for /me endpoint."""
    user_id: int
    name: str
    email: str
    tenant_id: int
    tenant_name: str
    role: str


class UserPermissionsResponse(BaseModel):
    """Schema for /me/permissions endpoint."""
    permissions: List[str]


# Demo Login
class DemoLoginRequest(BaseModel):
    """Request for demo login."""
    username: str


class DemoLoginResponse(BaseModel):
    """Response from demo login."""
    access_token: str
    token_type: str = "bearer"
    user_id: int
    tenant_id: int
    role: str
