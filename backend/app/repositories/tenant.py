"""Tenant repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Tenant


class TenantRepository:
    """Repository for tenant operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, tenant_id: int) -> Optional[Tenant]:
        """Get tenant by ID."""
        query = select(Tenant).where(Tenant.id == tenant_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_code(self, code: str) -> Optional[Tenant]:
        """Get tenant by code."""
        query = select(Tenant).where(Tenant.code == code)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self) -> list[Tenant]:
        """Get all tenants."""
        query = select(Tenant)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, name: str, code: str, status: str = "active") -> Tenant:
        """Create a new tenant."""
        tenant = Tenant(name=name, code=code, status=status)
        self.db.add(tenant)
        await self.db.commit()
        await self.db.refresh(tenant)
        return tenant
