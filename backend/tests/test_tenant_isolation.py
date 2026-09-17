"""Test tenant isolation."""

import pytest
from app.repositories import UserRepository, CaseRepository, TenantRepository
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Tenant, User, Role, Case


@pytest.mark.asyncio
async def test_user_tenant_isolation(async_db):
    """Test that user repository properly isolates by tenant."""
    
    async with async_db() as db:
        # Create tenants
        tenant1 = Tenant(id=1, name="Tenant A", code="TENA")
        tenant2 = Tenant(id=2, name="Tenant B", code="TENB")
        db.add(tenant1)
        db.add(tenant2)
        await db.commit()
        
        # Create roles
        role1 = Role(id=1, tenant_id=1, name="Admin")
        role2 = Role(id=2, tenant_id=2, name="Admin")
        db.add(role1)
        db.add(role2)
        await db.commit()
        
        # Create users in different tenants
        user_tenant1 = User(
            id=1,
            tenant_id=1,
            name="User A",
            email="user@a.com",
            role_id=1,
        )
        user_tenant2 = User(
            id=2,
            tenant_id=2,
            name="User B",
            email="user@b.com",
            role_id=2,
        )
        db.add(user_tenant1)
        db.add(user_tenant2)
        await db.commit()
        
        # Test isolation
        repo = UserRepository(db)
        
        # Tenant 1 should only see its user
        users_t1 = await repo.get_all_by_tenant(1)
        assert len(users_t1) == 1
        assert users_t1[0].id == 1
        
        # Tenant 2 should only see its user
        users_t2 = await repo.get_all_by_tenant(2)
        assert len(users_t2) == 1
        assert users_t2[0].id == 2


@pytest.mark.asyncio
async def test_case_tenant_isolation(async_db):
    """Test that case repository properly isolates by tenant."""
    
    async with async_db() as db:
        # Create tenants
        tenant1 = Tenant(id=1, name="Tenant A", code="TENA")
        tenant2 = Tenant(id=2, name="Tenant B", code="TENB")
        db.add(tenant1)
        db.add(tenant2)
        await db.commit()
        
        # Create cases in different tenants
        case1 = Case(
            id=1,
            tenant_id=1,
            case_number="CASE-001",
            member_name="Member A",
        )
        case2 = Case(
            id=2,
            tenant_id=2,
            case_number="CASE-002",
            member_name="Member B",
        )
        db.add(case1)
        db.add(case2)
        await db.commit()
        
        # Test isolation
        repo = CaseRepository(db)
        
        # Tenant 1 should only see its cases
        cases_t1 = await repo.get_all_by_tenant(1)
        assert len(cases_t1) == 1
        assert cases_t1[0].id == 1
        
        # Tenant 2 should only see its cases
        cases_t2 = await repo.get_all_by_tenant(2)
        assert len(cases_t2) == 1
        assert cases_t2[0].id == 2
        
        # Cross-tenant access should return None
        cross_case = await repo.get_by_id(1, 2)
        assert cross_case is None
