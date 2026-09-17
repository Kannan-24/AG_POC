"""Case repository."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models import Case


class CaseRepository:
    """Repository for case operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, case_id: int, tenant_id: int) -> Optional[Case]:
        """Get case by ID with tenant isolation."""
        query = select(Case).where(
            (Case.id == case_id) & (Case.tenant_id == tenant_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_case_number(self, case_number: str, tenant_id: int) -> Optional[Case]:
        """Get case by case number with tenant isolation."""
        query = select(Case).where(
            (Case.case_number == case_number) & (Case.tenant_id == tenant_id)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all_by_tenant(self, tenant_id: int) -> list[Case]:
        """Get all cases in a tenant."""
        query = select(Case).where(Case.tenant_id == tenant_id)
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(
        self,
        tenant_id: int,
        case_number: str,
        member_name: str,
        status: str = "open",
        assigned_to: Optional[str] = None,
    ) -> Case:
        """Create a new case."""
        case = Case(
            tenant_id=tenant_id,
            case_number=case_number,
            member_name=member_name,
            status=status,
            assigned_to=assigned_to,
        )
        self.db.add(case)
        await self.db.commit()
        await self.db.refresh(case)
        return case
    
    async def update(self, case_id: int, tenant_id: int, update_data: dict) -> Optional[Case]:
        """Update case with tenant isolation."""
        case = await self.get_by_id(case_id, tenant_id)
        if not case:
            return None
        
        for key, value in update_data.items():
            if value is not None:
                setattr(case, key, value)
        
        await self.db.commit()
        await self.db.refresh(case)
        return case
