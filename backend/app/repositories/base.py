"""Base repository with tenant isolation."""

from typing import TypeVar, Generic, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import DeclarativeBase
from fastapi import HTTPException, status

T = TypeVar("T", bound=DeclarativeBase)


class TenantScopedRepository(Generic[T]):
    """Base repository with automatic tenant filtering."""
    
    def __init__(self, db: AsyncSession, model: type[T]):
        self.db = db
        self.model = model
    
    def _apply_tenant_filter(self, query, tenant_id: int):
        """Apply tenant filter to query."""
        if hasattr(self.model, "tenant_id"):
            return query.where(self.model.tenant_id == tenant_id)
        return query
    
    async def get_by_id(self, item_id: int, tenant_id: int) -> Optional[T]:
        """Get item by ID with tenant isolation."""
        query = select(self.model).where(self.model.id == item_id)
        query = self._apply_tenant_filter(query, tenant_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self, tenant_id: int) -> List[T]:
        """Get all items for tenant."""
        query = select(self.model)
        query = self._apply_tenant_filter(query, tenant_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, item: T, tenant_id: int) -> T:
        """Create new item in tenant context."""
        if hasattr(item, "tenant_id"):
            item.tenant_id = tenant_id
        self.db.add(item)
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def update(self, item_id: int, update_data: dict, tenant_id: int) -> Optional[T]:
        """Update item with tenant isolation."""
        item = await self.get_by_id(item_id, tenant_id)
        if not item:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(item, key, value)
        
        await self.db.commit()
        await self.db.refresh(item)
        return item
    
    async def delete(self, item_id: int, tenant_id: int) -> bool:
        """Delete item with tenant isolation."""
        item = await self.get_by_id(item_id, tenant_id)
        if not item:
            return False
        
        await self.db.delete(item)
        await self.db.commit()
        return True
