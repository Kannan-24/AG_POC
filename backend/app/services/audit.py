"""Audit service."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import AuditEventRepository
from app.models import AuditEvent


class AuditService:
    """Service for audit operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.audit_repo = AuditEventRepository(db)
    
    async def log_action(
        self,
        tenant_id: int,
        actor_id: int,
        actor_role: str,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        result: str = "ALLOWED",
        details: Optional[str] = None,
    ) -> AuditEvent:
        """Log an audit action."""
        return await self.audit_repo.create(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            result=result,
            details=details,
        )
    
    async def get_audit_events(self, tenant_id: int, limit: int = 1000) -> list[AuditEvent]:
        """Get audit events for tenant."""
        return await self.audit_repo.get_all_by_tenant(tenant_id, limit)
