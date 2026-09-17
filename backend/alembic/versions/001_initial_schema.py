"""Initial RBAC and Multi-Tenant POC schema with seed data.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = "001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial schema and seed data."""
    
    # Create tenants table
    op.create_table(
        "tenants",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("code", sa.String(50), nullable=False, unique=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_tenants_code", "code"),
    )
    
    # Create roles table (tenant-scoped)
    op.create_table(
        "roles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_roles_tenant_id", "tenant_id"),
    )
    
    # Create permissions table (global)
    op.create_table(
        "permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_permissions_name", "name"),
    )
    
    # Create role_permissions association table
    op.create_table(
        "role_permissions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("permission_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.ForeignKeyConstraint(["permission_id"], ["permissions.id"]),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_role_permissions_role_id", "role_id"),
        sa.Index("ix_role_permissions_permission_id", "permission_id"),
    )
    
    # Create users table (tenant-scoped)
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("role_id", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.ForeignKeyConstraint(["role_id"], ["roles.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_users_tenant_id", "tenant_id"),
        sa.Index("ix_users_email", "email"),
    )
    
    # Create cases table (tenant-scoped)
    op.create_table(
        "cases",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("case_number", sa.String(50), nullable=False),
        sa.Column("member_name", sa.String(255), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="open"),
        sa.Column("assigned_to", sa.String(255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_cases_tenant_id", "tenant_id"),
        sa.Index("ix_cases_case_number", "case_number"),
    )
    
    # Create audit_events table (tenant-scoped)
    op.create_table(
        "audit_events",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=False),
        sa.Column("actor_role", sa.String(255), nullable=True),
        sa.Column("action", sa.String(50), nullable=False),
        sa.Column("entity_type", sa.String(50), nullable=True),
        sa.Column("entity_id", sa.String(50), nullable=True),
        sa.Column("result", sa.String(50), nullable=True),
        sa.Column("details", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.getdate()),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.Index("ix_audit_events_tenant_id", "tenant_id"),
        sa.Index("ix_audit_events_created_at", "created_at"),
    )
    
    # Seed data
    # Insert tenants
    op.execute(
        "INSERT INTO tenants (name, code, status, created_at, updated_at) VALUES "
        "('Prominence Health', 'PROM', 'active', GETDATE(), GETDATE()), "
        "('Demo Health Plan', 'DEMO', 'active', GETDATE(), GETDATE())"
    )
    
    # Insert permissions
    permissions = [
        "view_cases",
        "create_case",
        "edit_case",
        "reassign_case",
        "sign_decision",
        "view_audit",
        "configure_tenant",
    ]
    for perm in permissions:
        op.execute(
            f"INSERT INTO permissions (name, description, created_at, updated_at) "
            f"VALUES ('{perm}', NULL, GETDATE(), GETDATE())"
        )
    
    # Insert roles for Tenant A (Prominence Health, id=1)
    op.execute(
        "INSERT INTO roles (tenant_id, name, description, created_at, updated_at) "
        "VALUES "
        "(1, 'A&G Specialist', 'Appeals & Grievances Specialist', GETDATE(), GETDATE()), "
        "(1, 'Medical Director', 'Medical Director', GETDATE(), GETDATE())"
    )
    
    # Insert roles for Tenant B (Demo Health Plan, id=2)
    op.execute(
        "INSERT INTO roles (tenant_id, name, description, created_at, updated_at) "
        "VALUES "
        "(2, 'Supervisor', 'Supervisor', GETDATE(), GETDATE()), "
        "(2, 'Tenant Administrator', 'Tenant Administrator', GETDATE(), GETDATE())"
    )
    
    # Assign permissions to roles
    # A&G Specialist (role_id=1): view_cases, create_case, edit_case, reassign_case
    role_perms = [
        (1, 1),  # A&G Specialist -> view_cases
        (1, 2),  # A&G Specialist -> create_case
        (1, 3),  # A&G Specialist -> edit_case
        (1, 4),  # A&G Specialist -> reassign_case
        (2, 1),  # Medical Director -> view_cases
        (2, 5),  # Medical Director -> sign_decision
        (3, 1),  # Supervisor -> view_cases
        (3, 4),  # Supervisor -> reassign_case
        (3, 6),  # Supervisor -> view_audit
        (4, 1),  # Tenant Administrator -> view_cases
        (4, 2),  # Tenant Administrator -> create_case
        (4, 3),  # Tenant Administrator -> edit_case
        (4, 4),  # Tenant Administrator -> reassign_case
        (4, 6),  # Tenant Administrator -> view_audit
        (4, 7),  # Tenant Administrator -> configure_tenant
    ]
    
    for role_id, perm_id in role_perms:
        op.execute(
            f"INSERT INTO role_permissions (role_id, permission_id, created_at) "
            f"VALUES ({role_id}, {perm_id}, GETDATE())"
        )
    
    # Insert users
    # Tenant A users
    op.execute(
        "INSERT INTO users (tenant_id, name, email, role_id, status, created_at, updated_at) "
        "VALUES "
        "(1, 'Alice', 'alice@prominence.demo', 1, 'active', GETDATE(), GETDATE()), "
        "(1, 'Mike', 'mike@prominence.demo', 2, 'active', GETDATE(), GETDATE())"
    )
    
    # Tenant B users
    op.execute(
        "INSERT INTO users (tenant_id, name, email, role_id, status, created_at, updated_at) "
        "VALUES "
        "(2, 'Bob', 'bob@demohealth.demo', 3, 'active', GETDATE(), GETDATE()), "
        "(2, 'Sara', 'sara@demohealth.demo', 4, 'active', GETDATE(), GETDATE())"
    )
    
    # Insert cases
    # Tenant A cases
    op.execute(
        "INSERT INTO cases (tenant_id, case_number, member_name, status, assigned_to, created_at, updated_at) "
        "VALUES "
        "(1, 'AG-1001', 'John Smith', 'open', 'Alice', GETDATE(), GETDATE()), "
        "(1, 'AG-1002', 'Jane Doe', 'open', NULL, GETDATE(), GETDATE()), "
        "(1, 'AG-1003', 'Bob Johnson', 'in-progress', 'Mike', GETDATE(), GETDATE())"
    )
    
    # Tenant B cases
    op.execute(
        "INSERT INTO cases (tenant_id, case_number, member_name, status, assigned_to, created_at, updated_at) "
        "VALUES "
        "(2, 'AG-2001', 'Alice Williams', 'open', 'Bob', GETDATE(), GETDATE()), "
        "(2, 'AG-2002', 'Charlie Brown', 'open', NULL, GETDATE(), GETDATE()), "
        "(2, 'AG-2003', 'David Lee', 'in-progress', 'Sara', GETDATE(), GETDATE())"
    )


def downgrade() -> None:
    """Drop all tables."""
    op.drop_table("audit_events")
    op.drop_table("cases")
    op.drop_table("users")
    op.drop_table("role_permissions")
    op.drop_table("permissions")
    op.drop_table("roles")
    op.drop_table("tenants")
