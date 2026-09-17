"""Database models for A&G RBAC POC."""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from app.database import Base


class Tenant(Base):
    """Tenant model for multi-tenant architecture."""
    
    __tablename__ = "tenants"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(50), nullable=False, unique=True)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    roles = relationship("Role", back_populates="tenant", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="tenant", cascade="all, delete-orphan")
    audit_events = relationship("AuditEvent", back_populates="tenant", cascade="all, delete-orphan")


class User(Base):
    """User model - tenant-scoped."""
    
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    status = Column(String(50), default="active")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    role = relationship("Role", back_populates="users")
    audit_events = relationship("AuditEvent", back_populates="actor")


class Role(Base):
    """Role model - tenant-scoped."""
    
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="roles")
    users = relationship("User", back_populates="role")
    permissions = relationship(
        "Permission",
        secondary="role_permissions",
        back_populates="roles"
    )


class Permission(Base):
    """Permission model - global, not tenant-scoped."""
    
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    roles = relationship(
        "Role",
        secondary="role_permissions",
        back_populates="permissions"
    )


class RolePermission(Base):
    """Association table for roles and permissions."""
    
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Case(Base):
    """Case model - tenant-scoped."""
    
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    case_number = Column(String(50), nullable=False)
    member_name = Column(String(255), nullable=False)
    status = Column(String(50), default="open")
    assigned_to = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="cases")


class AuditEventAction(str, enum.Enum):
    """Enumeration of audit actions."""
    
    LOGIN = "LOGIN"
    VIEW_CASE = "VIEW_CASE"
    CREATE_CASE = "CREATE_CASE"
    EDIT_CASE = "EDIT_CASE"
    REASSIGN_CASE = "REASSIGN_CASE"
    SIGN_DECISION = "SIGN_DECISION"
    VIEW_AUDIT = "VIEW_AUDIT"
    CONFIGURE_TENANT = "CONFIGURE_TENANT"
    ACCESS_DENIED = "ACCESS_DENIED"


class AuditEvent(Base):
    """Audit event model - tenant-scoped."""
    
    __tablename__ = "audit_events"
    
    id = Column(Integer, primary_key=True, index=True)
    tenant_id = Column(Integer, ForeignKey("tenants.id"), nullable=False)
    actor_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    actor_role = Column(String(255))
    action = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(String(50))
    result = Column(String(50))  # ALLOWED, DENIED
    details = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="audit_events")
    actor = relationship("User", back_populates="audit_events")
