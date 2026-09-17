"""User service."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository
from app.models import User


class UserService:
    """Service for user operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
    
    async def get_user(self, user_id: int, tenant_id: int) -> Optional[User]:
        """Get user with tenant isolation."""
        return await self.user_repo.get_by_id(user_id, tenant_id)
    
    async def get_users_by_tenant(self, tenant_id: int) -> list[User]:
        """Get all users in tenant."""
        return await self.user_repo.get_all_by_tenant(tenant_id)
    
    async def get_user_any_tenant(self, user_id: int) -> Optional[User]:
        """Get user by ID (for auth, not tenant-scoped)."""
        return await self.user_repo.get_by_id_any_tenant(user_id)
