"""Permission repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Permission


class PermissionRepository:
    """Repository for permission operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, permission_id: int) -> Optional[Permission]:
        """Get permission by ID."""
        query = select(Permission).where(Permission.id == permission_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        query = select(Permission).where(Permission.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self) -> list[Permission]:
        """Get all permissions."""
        query = select(Permission)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, name: str, description: Optional[str] = None) -> Permission:
        """Create a new permission."""
        permission = Permission(name=name, description=description)
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        return permission
