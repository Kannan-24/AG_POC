# A&G RBAC + Multi-Tenant SaaS POC

A proof-of-concept application demonstrating:
- **Multi-tenant architecture** with tenant isolation
- **Role-Based Access Control (RBAC)** with permissions
- **Permission-based API authorization**
- **Frontend role-aware UI**
- **Audit logging**
- **Clean backend architecture** with repository pattern

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 16+ and npm
- SQL Server (development instance: `KOPPHPDEV006\SQLEXPRESS`)
- ODBC Driver 17 for SQL Server

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env
# Edit .env with your SQL Server connection details

# Run database migrations
alembic upgrade head

# Start FastAPI server
uvicorn app.main:app --reload
```

Backend runs on: `http://localhost:8000`

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start React development server
npm start
```

Frontend runs on: `http://localhost:3000`

## Demo Users

### Prominence Health (Tenant A)

| User | Role | Permissions |
|------|------|------------|
| Alice | A&G Specialist | view_cases, create_case, edit_case, reassign_case |
| Mike | Medical Director | view_cases, sign_decision |

### Demo Health Plan (Tenant B)

| User | Role | Permissions |
|------|------|------------|
| Bob | Supervisor | view_cases, reassign_case, view_audit |
| Sara | Tenant Administrator | view_cases, create_case, edit_case, reassign_case, view_audit, configure_tenant |

## Project Structure

```
AG_POC/
├── backend/
│   ├── app/
│   │   ├── api/          # API route handlers
│   │   ├── models/       # SQLAlchemy ORM models
│   │   ├── schemas/      # Pydantic request/response schemas
│   │   ├── repositories/ # Data access layer (tenant-isolated)
│   │   ├── services/     # Business logic layer
│   │   ├── auth/         # Authentication & authorization
│   │   ├── config/       # Configuration management
│   │   ├── database/     # Database session & base
│   │   └── main.py       # FastAPI application entry
│   ├── alembic/          # Database migrations
│   ├── tests/            # Backend tests
│   ├── requirements.txt  # Python dependencies
│   ├── .env.example      # Environment template
│   └── README.md
│
├── frontend/
│   ├── public/           # Static assets
│   ├── src/
│   │   ├── components/   # Reusable UI components
│   │   ├── pages/        # Page components
│   │   ├── auth/         # Auth context & helpers
│   │   ├── services/     # API client
│   │   ├── hooks/        # Custom hooks
│   │   ├── styles/       # CSS stylesheets
│   │   ├── App.js        # Main app component
│   │   └── index.js      # React entry point
│   ├── package.json
│   ├── README.md
│   └── public/index.html
│
└── README.md (this file)
```

## Architecture

### Backend Architecture

```
API Routes
    ↓
Authorization (Decorator)
    ↓
Service Layer
    ↓
Repository Layer (Tenant Isolation)
    ↓
SQLAlchemy Models
    ↓
SQL Server
```

**Key Principle:** Every tenant-scoped record has a `tenant_id` that is automatically enforced in the repository layer.

### Frontend Architecture

```
React Components
    ↓
Auth Context (useAuth hook)
    ↓
Permission Hooks (usePermissions)
    ↓
API Client (axios)
    ↓
Backend APIs
```

**Key Principle:** UI uses permissions for visibility; backend enforces authorization.

## API Endpoints

### Authentication

```
POST   /auth/demo-login           Demo login
GET    /auth/me                   Current user info
GET    /auth/me/permissions       Current user permissions
```

### Cases

```
GET    /cases                     List tenant cases
GET    /cases/{id}                Get case detail (view_cases)
POST   /cases                     Create case (create_case)
PATCH  /cases/{id}                Update case (edit_case)
POST   /cases/{id}/reassign       Reassign case (reassign_case)
POST   /cases/{id}/sign           Sign decision (sign_decision)
```

### Users & Roles

```
GET    /users                     List tenant users (configure_tenant)
GET    /roles                     List tenant roles
GET    /roles/{id}/permissions    Get role permissions
```

### Audit

```
GET    /audit                     Get audit log (view_audit)
```

### Tenant

```
GET    /tenant                    Get tenant info
GET    /tenant/configuration      Get config (configure_tenant)
PATCH  /tenant/configuration      Update config (configure_tenant)
```

## Tenant Isolation

### How It Works

1. **Authentication**: User logs in with demo login → JWT token contains `user_id`, `tenant_id`, `role_name`
2. **Request**: Frontend sends token in `Authorization: Bearer <token>` header
3. **Authorization**: Backend validates token and extracts `tenant_id`
4. **Repository Filtering**: All queries automatically add `WHERE tenant_id = :current_tenant_id`
5. **API Response**: Only tenant-scoped data is returned

### Example

**Alice (Tenant A) tries to access case AG-2001 (Tenant B):**

```python
case = await case_repo.get_by_id(case_id=2001, tenant_id=1)
# Internally queries:
# SELECT * FROM cases WHERE id=2001 AND tenant_id=1
# Result: None (case exists with tenant_id=2, not found for tenant_id=1)
```

## RBAC Authorization

### Permission-Based Authorization

1. **Get User Permissions**: Load user's role and role's permissions
2. **Check Permission**: Use `PermissionChecker` to verify access
3. **Enforce**: Return 403 Forbidden if permission missing

### Example

```python
@router.get("/cases/{case_id}")
async def get_case(
    case_id: int,
    auth_context: AuthContext = Depends(get_current_auth_context),
    db: AsyncSession = Depends(get_db),
):
    auth_service = AuthService(db)
    
    # Get permissions
    permissions = await auth_service.get_user_permissions(auth_context.user_id)
    checker = PermissionChecker(permissions)
    
    # Check permission
    checker.require_permission("view_cases")  # Raises 403 if missing
    
    # Get case with tenant isolation
    case = await case_repo.get_by_id(case_id, auth_context.tenant_id)
    return case
```

## Database Schema

### Key Tables

- **tenants**: Multi-tenant metadata
- **users**: User accounts (tenant-scoped)
- **roles**: User roles (tenant-scoped)
- **permissions**: Global permission definitions
- **role_permissions**: Role-to-permission mappings
- **cases**: Application cases (tenant-scoped)
- **audit_events**: Audit logs (tenant-scoped)

### Tenant Isolation Enforcement

All tenant-scoped tables include:
```sql
tenant_id INT NOT NULL FOREIGN KEY REFERENCES tenants(id)
```

Repositories automatically filter queries by `tenant_id`.

## Testing

### Backend Tests

```bash
cd backend
pytest
```

Tests include:
- Authorization tests (permission checking)
- Tenant isolation tests (cross-tenant access prevention)
- Setup verification

### Frontend Tests

```bash
cd frontend
npm test
```

Tests include:
- Auth context tests
- Component rendering tests
- Permission hook tests

## Demo Scenario

### Step 1: Login as Alice

1. Go to `http://localhost:3000`
2. Select "Alice - A&G Specialist"
3. See dashboard with Alice's permissions

### Step 2: View Cases

1. Navigate to "Cases"
2. See only Tenant A cases: AG-1001, AG-1002, AG-1003
3. Click a case to see details

### Step 3: Attempt Cross-Tenant Access

1. Try to access `/cases/2001` (Tenant B case) in the URL
2. Backend returns 404 or 403 (case doesn't exist for tenant A)

### Step 4: Attempt Unauthorized Action

1. Notice "Sign Decision" button is hidden (Alice doesn't have permission)
2. Try to call API directly using browser console:
   ```javascript
   fetch('http://localhost:8000/cases/1/sign', {
     method: 'POST',
     headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` }
   })
   ```
3. Response: `403 Forbidden` (backend enforces)

### Step 5: Login as Mike

1. Logout and login as "Mike - Medical Director"
2. See "Sign Decision" action available
3. Notice Mike can only access cases (view permission), not create/edit

### Step 6: Switch to Tenant B

1. Logout and login as "Bob - Supervisor"
2. See only Tenant B cases: AG-2001, AG-2002, AG-2003
3. Notice different audit trail

## Security Principles

### Frontend Security (Not Sufficient)

- ❌ UI hiding buttons is **UX only**, not security
- ❌ localStorage tokens can be inspected
- ❌ Frontend filtering can be bypassed

### Backend Security (Authoritative)

- ✅ JWT validation on every request
- ✅ `tenant_id` extracted from token (not frontend)
- ✅ Repository layer enforces tenant filtering
- ✅ API returns 403 for unauthorized requests
- ✅ Audit logging for all actions

## Known Limitations (By Design)

This is a **POC**, not production-ready. Intentionally NOT implemented:

- ❌ Production authentication (OAuth2, SSO, OIDC)
- ❌ Full A&G case workflow
- ❌ OCR, extraction, classification AI
- ❌ Letter generation, effectuation, IRE workflow
- ❌ CMS reporting, Talkdesk integration
- ❌ Azure Event Hub, Cosmos, Blob integration
- ❌ Full production deployment (containerization, secrets management)
- ❌ Performance optimization (caching, indexing tuning)
- ❌ Advanced audit features (audit retention policies, compliance)

## Configuration

### Backend Environment Variables

```
SQL_SERVER=KOPPHPDEV006\SQLEXPRESS
SQL_DATABASE=AG_RBAC_POC
SQL_USERNAME=
SQL_PASSWORD=
SQL_TRUSTED_CONNECTION=true
DEBUG=false
```

### Frontend Environment Variables

```
REACT_APP_API_URL=http://localhost:8000
```

## Database Migrations

### Create New Migration

```bash
cd backend
alembic revision --autogenerate -m "Description of change"
```

### Apply Migrations

```bash
alembic upgrade head
```

### Rollback

```bash
alembic downgrade -1
```

## Troubleshooting

### "Failed to connect to SQL Server"

- Check `SQL_SERVER` hostname in `.env`
- Verify ODBC Driver 17 is installed
- Confirm SQL Server is running
- Test connection: `sqlcmd -S KOPPHPDEV006\SQLEXPRESS -E`

### "Module not found: ..."

- Reinstall dependencies: `pip install -r requirements.txt` (backend) or `npm install` (frontend)
- Activate virtual environment: `venv\Scripts\activate` (backend)

### "CORS errors"

- Ensure backend is running on `http://localhost:8000`
- Check `REACT_APP_API_URL` environment variable
- Verify CORS middleware is enabled in FastAPI

### "Permission denied errors"

- Ensure JWT token is valid and not expired
- Check token contains correct `tenant_id`
- Verify user has required role
- Check audit log for denied events

## Next Steps for Production

1. **Authentication**: Implement real OAuth2/SSO
2. **Database**: Use production SQL Server instance
3. **Secrets**: Use Azure Key Vault or similar
4. **API**: Add rate limiting, request validation
5. **Frontend**: Add input validation, error handling
6. **Testing**: Add comprehensive unit and E2E tests
7. **Deployment**: Docker, Kubernetes, Azure App Service
8. **Monitoring**: Application Insights, Azure Monitor
9. **Audit**: Azure Audit Logs, Compliance Center

## Support

This is a POC for demonstration purposes. For questions or issues, refer to individual README files in `backend/` and `frontend/` directories.
