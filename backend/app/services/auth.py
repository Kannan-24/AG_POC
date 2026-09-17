"""Auth service."""

from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import UserRepository, RoleRepository, PermissionRepository
from app.models import User, Role


class AuthService:
    """Service for authentication operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.user_repo = UserRepository(db)
        self.role_repo = RoleRepository(db)
        self.permission_repo = PermissionRepository(db)
    
    async def get_user_with_permissions(self, user_id: int) -> tuple[User, Role, list[str]]:
        """Get user with their role and permissions."""
        user = await self.user_repo.get_by_id_any_tenant(user_id)
        if not user:
            return None, None, []
        
        # Get role with permissions eager-loaded
        role = await self.role_repo.get_by_id(user.role_id, user.tenant_id)
        
        # Extract permission names
        permissions = [p.name for p in role.permissions] if role and role.permissions else []
        
        return user, role, permissions
    
    async def get_user_permissions(self, user_id: int) -> list[str]:
        """Get user's permissions."""
        _, _, permissions = await self.get_user_with_permissions(user_id)
        return permissions
    
    async def has_permission(self, user_id: int, permission_name: str) -> bool:
        """Check if user has a specific permission."""
        permissions = await self.get_user_permissions(user_id)
        return permission_name in permissions
