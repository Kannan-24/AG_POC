"""Role repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from app.models import Role, Permission


class RoleRepository:
    """Repository for role operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, role_id: int, tenant_id: int) -> Optional[Role]:
        """Get role by ID with tenant isolation."""
        query = (
            select(Role)
            .where((Role.id == role_id) & (Role.tenant_id == tenant_id))
            .options(joinedload(Role.permissions))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_by_tenant(self, tenant_id: int) -> list[Role]:
        """Get all roles in a tenant."""
        query = (
            select(Role)
            .where(Role.tenant_id == tenant_id)
            .options(joinedload(Role.permissions))
        )
        result = await self.db.execute(query)
        return result.scalars().unique().all()
    
    async def get_permissions_by_role_id(self, role_id: int, tenant_id: int) -> list[Permission]:
        """Get all permissions for a role."""
        query = (
            select(Permission)
            .join(Role.permissions)
            .where((Role.id == role_id) & (Role.tenant_id == tenant_id))
        )
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(
        self,
        tenant_id: int,
        name: str,
        description: Optional[str] = None,
    ) -> Role:
        """Create a new role."""
        role = Role(
            tenant_id=tenant_id,
            name=name,
            description=description,
        )
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        return role
