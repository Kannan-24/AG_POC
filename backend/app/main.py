"""Main FastAPI application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import (
    auth_router,
    cases_router,
    users_router,
    roles_router,
    audit_router,
    tenant_router,
)
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    description="A&G RBAC + Multi-Tenant POC",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(cases_router)
app.include_router(users_router)
app.include_router(roles_router)
app.include_router(audit_router)
app.include_router(tenant_router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"}
