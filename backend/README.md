# A&G RBAC + Multi-Tenant POC Backend

FastAPI backend for the A&G RBAC POC.

## Getting Started

### Prerequisites

- Python 3.10+
- SQL Server (development instance: `KOPPHPDEV006\SQLEXPRESS`)
- ODBC Driver 17 for SQL Server

### Installation

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env

# Edit .env with your SQL Server connection
```

### Running the Server

```bash
# Using uvicorn
uvicorn app.main:app --reload

# Or using the run script
python run.py
```

Server runs on: http://localhost:8000

API docs: http://localhost:8000/docs (Swagger UI)

### Database Migrations

```bash
# Run migrations
alembic upgrade head

# Create new migration
alembic revision --autogenerate -m "Description"

# Rollback one migration
alembic downgrade -1
```

## Project Structure

```
backend/
├── app/
│   ├── api/              # API route handlers
│   │   ├── auth.py       # Authentication routes
│   │   ├── cases.py      # Cases routes
│   │   ├── users.py      # Users routes
│   │   ├── roles.py      # Roles routes
│   │   ├── audit.py      # Audit routes
│   │   ├── tenant.py     # Tenant routes
│   │   └── __init__.py
│   │
│   ├── models/           # SQLAlchemy ORM models
│   │   ├── models.py     # All models (Tenant, User, Role, etc.)
│   │   └── __init__.py
│   │
│   ├── schemas/          # Pydantic request/response schemas
│   │   ├── schemas.py    # All schemas
│   │   └── __init__.py
│   │
│   ├── repositories/     # Data access layer with tenant isolation
│   │   ├── base.py       # Base TenantScopedRepository
│   │   ├── tenant.py     # TenantRepository
│   │   ├── user.py       # UserRepository
│   │   ├── case.py       # CaseRepository
│   │   ├── role.py       # RoleRepository
│   │   ├── permission.py # PermissionRepository
│   │   ├── audit.py      # AuditEventRepository
│   │   └── __init__.py
│   │
│   ├── services/         # Business logic layer
│   │   ├── auth.py       # AuthService
│   │   ├── case.py       # CaseService
│   │   ├── audit.py      # AuditService
│   │   ├── user.py       # UserService
│   │   └── __init__.py
│   │
│   ├── auth/             # Authentication & authorization
│   │   ├── context.py    # AuthContext, JWT helpers
│   │   ├── authorization.py  # PermissionChecker, decorators
│   │   └── __init__.py
│   │
│   ├── config/           # Configuration
│   │   ├── settings.py   # Settings from environment
│   │   └── __init__.py
│   │
│   ├── database/         # Database setup
│   │   ├── base.py       # Base model
│   │   ├── session.py    # AsyncSession, engine
│   │   └── __init__.py
│   │
│   ├── main.py           # FastAPI app
│   └── __init__.py
│
├── alembic/              # Database migrations
│   ├── versions/
│   │   └── 001_initial_schema.py
│   ├── env.py
│   ├── script.py.mako
│   └── __init__.py
│
├── tests/                # Backend tests
│   ├── conftest.py       # Test configuration
│   ├── test_auth.py      # Auth tests
│   ├── test_tenant_isolation.py  # Tenant isolation tests
│   └── test_setup.py     # Setup tests
│
├── requirements.txt      # Python dependencies
├── .env.example          # Environment template
├── run.py               # Development server entry
├── alembic.ini          # Alembic configuration
└── README.md
```

## Architecture

### Clean Architecture Pattern

```
API Routes (api/*)
    ↓
Services (services/*)
    ↓
Repositories (repositories/*)
    ↓
Models (models/*)
    ↓
Database
```

### Dependency Injection

- All dependencies injected through FastAPI `Depends()`
- No global state (except database engine)
- Easy to test with mock repositories

### Tenant Isolation Pattern

```
AuthContext
  ├─ user_id
  ├─ tenant_id  ← Key for isolation
  └─ permissions

↓

PermissionChecker
  ├─ check permission

↓

Repository (TenantScopedRepository)
  ├─ Automatically applies: WHERE tenant_id = context.tenant_id
  ├─ Prevents cross-tenant data access
  └─ Centralized in one place
```

## API Endpoints Summary

### Authentication
- `POST /auth/demo-login` - Demo login
- `GET /auth/me` - Current user
- `GET /auth/me/permissions` - User permissions

### Cases (Tenant-Isolated)
- `GET /cases` - List tenant cases [view_cases]
- `GET /cases/{id}` - Get case [view_cases]
- `POST /cases` - Create case [create_case]
- `PATCH /cases/{id}` - Update case [edit_case]
- `POST /cases/{id}/reassign` - Reassign [reassign_case]
- `POST /cases/{id}/sign` - Sign decision [sign_decision]

### Users (Tenant-Isolated)
- `GET /users` - List users [configure_tenant]

### Roles
- `GET /roles` - List roles
- `GET /roles/{id}/permissions` - Role permissions

### Audit (Tenant-Isolated)
- `GET /audit` - Audit log [view_audit]

### Tenant
- `GET /tenant` - Tenant info
- `GET /tenant/configuration` - Config [configure_tenant]
- `PATCH /tenant/configuration` - Update config [configure_tenant]

## Authorization

### Permission-Based Authorization

Every protected endpoint:

1. **Extracts** AuthContext from JWT token
2. **Gets** user permissions from database
3. **Requires** specific permission
4. **Returns** 403 if permission missing

Example:

```python
@router.post("/cases/{id}/sign")
async def sign_decision(
    case_id: int,
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    
    # Get and check permission
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    checker.require_permission("sign_decision")  # 403 if missing
    
    # Business logic...
```

## Tenant Isolation

### Rule: Every Query Must Filter by Tenant

**Repositories automatically enforce this:**

```python
async def get_by_id(self, item_id: int, tenant_id: int):
    query = select(self.model).where(
        (self.model.id == item_id) & 
        (self.model.tenant_id == tenant_id)  # ← Automatic filter
    )
    result = await self.db.execute(query)
    return result.scalar_one_or_none()
```

**Never trust frontend tenant_id:**

```python
# ❌ WRONG: User can change tenant_id in request
tenant_id = request.query_params.get("tenant_id")

# ✅ CORRECT: Extract from token
tenant_id = auth_context.tenant_id  # From JWT
```

## Database Seed Data

### Demo Tenants

- **Prominence Health** (code: PROM) - Tenant A
- **Demo Health Plan** (code: DEMO) - Tenant B

### Demo Users

| Tenant | User | Role | ID |
|--------|------|------|-----|
| A | Alice | A&G Specialist | 1 |
| A | Mike | Medical Director | 2 |
| B | Bob | Supervisor | 3 |
| B | Sara | Tenant Administrator | 4 |

### Demo Cases

| Tenant | Case # | Member | ID |
|--------|--------|--------|-----|
| A | AG-1001 | John Smith | 1 |
| A | AG-1002 | Jane Doe | 2 |
| A | AG-1003 | Bob Johnson | 3 |
| B | AG-2001 | Alice Williams | 4 |
| B | AG-2002 | Charlie Brown | 5 |
| B | AG-2003 | David Lee | 6 |

### Permissions

- `view_cases` - View cases
- `create_case` - Create new case
- `edit_case` - Edit case details
- `reassign_case` - Reassign case
- `sign_decision` - Sign decision
- `view_audit` - View audit log
- `configure_tenant` - Configure tenant

### Role-Permission Mapping

| Role | Permissions |
|------|------------|
| A&G Specialist | view_cases, create_case, edit_case, reassign_case |
| Medical Director | view_cases, sign_decision |
| Supervisor | view_cases, reassign_case, view_audit |
| Tenant Administrator | view_cases, create_case, edit_case, reassign_case, view_audit, configure_tenant |

## Testing

### Run All Tests

```bash
pytest
```

### Run Specific Test

```bash
pytest tests/test_auth.py::test_permission_checker_has_permission
```

### Run with Coverage

```bash
pytest --cov=app
```

### Tests Include

- **Authentication**: Token creation, permission checking
- **Tenant Isolation**: Cross-tenant access prevention
- **Setup Verification**: Models and configuration

## Configuration

### Environment Variables

```
SQL_SERVER=KOPPHPDEV006\SQLEXPRESS
SQL_DATABASE=AG_RBAC_POC
SQL_USERNAME=
SQL_PASSWORD=
SQL_TRUSTED_CONNECTION=true
DEBUG=false
APP_NAME=A&G RBAC POC
```

### SQL Server Connection

The backend uses async SQLAlchemy with `pyodbc`:

```python
# Connection string (Windows auth)
mssql+pyodbc://SERVER\INSTANCE/DATABASE?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes

# Connection string (SQL auth)
mssql+pyodbc://USERNAME:PASSWORD@SERVER\INSTANCE/DATABASE?driver=ODBC+Driver+17+for+SQL+Server
```

## Common Issues

### "No module named 'pyodbc'"

```bash
pip install pyodbc
# On Linux/Mac, may also need:
pip install --upgrade setuptools
```

### "ODBC Driver not found"

Download: https://learn.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

### "Connection refused"

- SQL Server may not be running
- Check instance name: `sqlcmd -L`
- Test connection: `sqlcmd -S KOPPHPDEV006\SQLEXPRESS -E`

## Development

### Code Style

Python code follows PEP 8. Use a linter:

```bash
pip install flake8
flake8 app/
```

### Adding New Endpoints

1. Create schema in `schemas/schemas.py`
2. Create model in `models/models.py`
3. Create repository in `repositories/`
4. Create service in `services/`
5. Create API route in `api/`

### Adding New Permissions

1. Add permission name to seed data in migration
2. Add permission constant if needed
3. Use `require_permission("permission_name")` in routes

## Production Considerations

For production deployment:

1. **Secrets**: Use Azure Key Vault, not .env
2. **Authentication**: Implement real OAuth2/SSO
3. **Database**: Use managed SQL Database (Azure SQL)
4. **Audit**: Enable SQL Server audit logs
5. **Monitoring**: Add Application Insights
6. **Rate Limiting**: Add API rate limits
7. **HTTPS**: Enforce SSL/TLS
8. **CORS**: Restrict to known domains
9. **Testing**: Comprehensive integration tests
10. **Documentation**: OpenAPI/Swagger maintained
