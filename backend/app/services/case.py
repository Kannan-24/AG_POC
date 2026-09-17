"""Case service."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories import CaseRepository, AuditEventRepository
from app.models import Case
from app.schemas import CaseCreate, CaseUpdate


class CaseService:
    """Service for case operations."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.case_repo = CaseRepository(db)
        self.audit_repo = AuditEventRepository(db)
    
    async def get_case(self, case_id: int, tenant_id: int) -> Optional[Case]:
        """Get case with tenant isolation."""
        return await self.case_repo.get_by_id(case_id, tenant_id)
    
    async def get_all_cases(self, tenant_id: int) -> list[Case]:
        """Get all cases for tenant."""
        return await self.case_repo.get_all_by_tenant(tenant_id)
    
    async def create_case(
        self,
        tenant_id: int,
        case_number: str,
        member_name: str,
        status: str = "open",
        assigned_to: Optional[str] = None,
    ) -> Case:
        """Create a new case."""
        return await self.case_repo.create(
            tenant_id=tenant_id,
            case_number=case_number,
            member_name=member_name,
            status=status,
            assigned_to=assigned_to,
        )
    
    async def update_case(
        self,
        case_id: int,
        tenant_id: int,
        update_data: dict,
    ) -> Optional[Case]:
        """Update case with tenant isolation."""
        return await self.case_repo.update(case_id, tenant_id, update_data)
    
    async def reassign_case(
        self,
        case_id: int,
        tenant_id: int,
        assigned_to: str,
    ) -> Optional[Case]:
        """Reassign case to user."""
        return await self.case_repo.update(
            case_id,
            tenant_id,
            {"assigned_to": assigned_to},
        )
    
    async def sign_decision(
        self,
        case_id: int,
        tenant_id: int,
    ) -> Optional[Case]:
        """Sign decision on case."""
        return await self.case_repo.update(
            case_id,
            tenant_id,
            {"status": "signed"},
        )
