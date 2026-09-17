"""API routes module."""

from .auth import router as auth_router
from .cases import router as cases_router
from .users import router as users_router
from .roles import router as roles_router
from .audit import router as audit_router
from .tenant import router as tenant_router

__all__ = [
    "auth_router",
    "cases_router",
    "users_router",
    "roles_router",
    "audit_router",
    "tenant_router",
]
