"""
Authentication middleware for API Key validation
"""
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader
from typing import Optional

from app.config import settings

# API Key header scheme
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: Optional[str] = Depends(api_key_header)) -> str:
    """
    Verify API Key from request header

    Args:
        api_key: API Key from X-API-Key header

    Returns:
        Validated API Key

    Raises:
        HTTPException: If API Key is missing or invalid
    """
    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API Key is required. Please provide X-API-Key header.",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # Check if API Key is valid
    if api_key not in settings.VALID_API_KEYS:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API Key. Access denied.",
        )

    return api_key


class AuthMiddleware:
    """
    Authentication middleware for FastAPI
    Handles API Key validation for protected routes
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        """
        Process incoming requests

        Note: This middleware is for demonstration purposes.
        In production, use FastAPI's dependency injection system
        with the verify_api_key function for route protection.
        """
        await self.app(scope, receive, send)


# Optional: Role-based access control
class RoleChecker:
    """
    Role-based access control checker
    Can be used to restrict access based on user roles
    """

    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, api_key: str = Depends(verify_api_key)):
        """
        Check if the API Key has the required role

        Args:
            api_key: Validated API Key

        Returns:
            True if role is allowed

        Raises:
            HTTPException: If role is not allowed
        """
        # In a real application, you would look up the role from a database
        # For now, we'll use a simple mapping
        role = settings.API_KEY_ROLES.get(api_key, "user")

        if role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {', '.join(self.allowed_roles)}",
            )

        return True


# Dependency for optional authentication
async def get_optional_api_key(api_key: Optional[str] = Depends(api_key_header)) -> Optional[str]:
    """
    Get API Key if provided, but don't require it

    Args:
        api_key: Optional API Key from X-API-Key header

    Returns:
        API Key if valid, None otherwise
    """
    if api_key and api_key in settings.VALID_API_KEYS:
        return api_key
    return None
