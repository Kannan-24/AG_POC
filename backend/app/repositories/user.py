"""User repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import User


class UserRepository:
    """Repository for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, user_id: int, tenant_id: int) -> Optional[User]:
        """Get user by ID with tenant isolation."""
        query = select(User).where(
            (User.id == user_id) & (User.tenant_id == tenant_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_email(self, email: str, tenant_id: int) -> Optional[User]:
        """Get user by email with tenant isolation."""
        query = select(User).where(
            (User.email == email) & (User.tenant_id == tenant_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_by_tenant(self, tenant_id: int) -> list[User]:
        """Get all users in a tenant."""
        query = select(User).where(User.tenant_id == tenant_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_by_id_any_tenant(self, user_id: int) -> Optional[User]:
        """Get user by ID (used for auth, not tenant-scoped)."""
        query = select(User).where(User.id == user_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create(
        self,
        tenant_id: int,
        name: str,
        email: str,
        role_id: int,
        status: str = "active",
    ) -> User:
        """Create a new user."""
        user = User(
            tenant_id=tenant_id,
            name=name,
            email=email,
            role_id=role_id,
            status=status,
        )
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user
