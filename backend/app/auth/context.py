"""Authentication and authorization context."""

from typing import Optional
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthCredentials
import jwt
from datetime import datetime, timedelta

security = HTTPBearer()

# JWT configuration
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"
DEMO_TOKEN_EXPIRE_HOURS = 24


class AuthContext:
    """Current authentication context."""
    
    def __init__(
        self,
        user_id: int,
        tenant_id: int,
        role_name: str,
    ):
        self.user_id = user_id
        self.tenant_id = tenant_id
        self.role_name = role_name
        self.permissions: Optional[list] = None


def create_demo_token(user_id: int, tenant_id: int, role_name: str) -> str:
    """Create a demo JWT token."""
    payload = {
        "user_id": user_id,
        "tenant_id": tenant_id,
        "role_name": role_name,
        "exp": datetime.utcnow() + timedelta(hours=DEMO_TOKEN_EXPIRE_HOURS),
        "iat": datetime.utcnow(),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def verify_token(token: str) -> dict:
    """Verify JWT token and return payload."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


async def get_current_auth_context(
    credentials: HTTPAuthCredentials = Depends(security),
) -> AuthContext:
    """Get current authentication context from token."""
    token = credentials.credentials
    payload = verify_token(token)
    
    return AuthContext(
        user_id=payload["user_id"],
        tenant_id=payload["tenant_id"],
        role_name=payload["role_name"],
    )
