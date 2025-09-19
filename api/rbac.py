"""
RBAC Middleware and Utilities for Multi-Tenant Simulation SaaS.
Supports FastAPI and dashboard integration.
"""

from fastapi import Depends, HTTPException, Request
from fastapi.security import OAuth2PasswordBearer
import jwt

# Define roles and permissions
ROLE_PERMISSIONS = {
    "admin": {"view_dashboard", "run_simulation", "manage_users", "view_billing"},
    "analyst": {"view_dashboard", "run_simulation"},
    "viewer": {"view_dashboard"},
}

OAUTH2_SCHEME = OAuth2PasswordBearer(tokenUrl="token")
JWT_SECRET = "replace_with_secure_secret"
JWT_ALGORITHM = "HS256"


def get_jwt_payload(token: str = Depends(OAUTH2_SCHEME)):
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return payload
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired token")


def require_role(required_roles):
    """
    Dependency for FastAPI endpoints.
    Usage: @app.get(..., dependencies=[Depends(require_role(["admin", "analyst"]))])
    """

    def role_checker(payload: dict = Depends(get_jwt_payload)):
        user_roles = payload.get("roles", [])
        tenant_id = payload.get("tenant_id")
        if not tenant_id:
            raise HTTPException(status_code=403, detail="Missing tenant context")
        if not any(role in required_roles for role in user_roles):
            raise HTTPException(status_code=403, detail="Insufficient role")
        return payload  # can be accessed in endpoint

    return role_checker


def has_permission(payload, permission):
    """
    Utility for dashboard (non-FastAPI) usage.
    Returns True/False if user has permission.
    """
    roles = payload.get("roles", [])
    for role in roles:
        if permission in ROLE_PERMISSIONS.get(role, set()):
            return True
    return False


def get_payload_from_request(request: Request):
    """
    Extract JWT from request cookies/headers for dashboard apps.
    """
    token = request.cookies.get("access_token") or request.headers.get(
        "Authorization", ""
    ).replace("Bearer ", "")
    if not token:
        raise Exception("Missing authentication token")
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
