"""Audit event repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import AuditEvent


class AuditEventRepository:
    """Repository for audit event operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, event_id: int, tenant_id: int) -> Optional[AuditEvent]:
        """Get audit event by ID with tenant isolation."""
        query = select(AuditEvent).where(
            (AuditEvent.id == event_id) & (AuditEvent.tenant_id == tenant_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_by_tenant(self, tenant_id: int, limit: int = 1000) -> list[AuditEvent]:
        """Get all audit events for a tenant."""
        query = (
            select(AuditEvent)
            .where(AuditEvent.tenant_id == tenant_id)
            .order_by(AuditEvent.created_at.desc())
            .limit(limit)
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(
        self,
        tenant_id: int,
        actor_id: int,
        actor_role: str,
        action: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        result: str = "UNKNOWN",
        details: Optional[str] = None,
    ) -> AuditEvent:
        """Create a new audit event."""
        event = AuditEvent(
            tenant_id=tenant_id,
            actor_id=actor_id,
            actor_role=actor_role,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            result=result,
            details=details,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event
