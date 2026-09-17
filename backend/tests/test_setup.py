"""Backend test."""

import pytest


def test_backend_setup():
    """Test that backend is properly configured."""
    from app.config import settings
    from app.database import Base
    
    # Check settings
    assert settings.sql_database == "AG_RBAC_POC"
    assert settings.app_name == "A&G RBAC POC"
    
    # Check models are registered
    assert len(Base.metadata.tables) > 0
    assert "users" in Base.metadata.tables
    assert "cases" in Base.metadata.tables
    assert "roles" in Base.metadata.tables
    assert "permissions" in Base.metadata.tables
