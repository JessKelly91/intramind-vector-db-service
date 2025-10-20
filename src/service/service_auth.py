"""
Service-to-service authentication module.

Validates that requests are coming from authorized services (like API Gateway).
"""

from fastapi import Header, HTTPException, status
from typing import Optional
import secrets
from ..weaviate_client.config import get_settings


class ServiceAuthError(HTTPException):
    """Exception raised when service authentication fails."""

    def __init__(self, detail: str = "Service authentication failed"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


async def verify_service_auth(
    x_service_auth: Optional[str] = Header(None, description="Service authentication key")
) -> str:
    """
    Verify service-to-service authentication.

    This dependency validates that the request comes from an authorized service.

    Args:
        x_service_auth: Service authentication key from header

    Returns:
        Service identifier

    Raises:
        ServiceAuthError: If authentication fails
    """
    settings = get_settings()
    service_auth_key = settings.get('Service.ServiceAuthKey')

    # If no service auth key is configured, allow all (for local dev)
    if not service_auth_key:
        return "local-development"

    if not x_service_auth:
        raise ServiceAuthError("Missing X-Service-Auth header")

    # Constant-time comparison to prevent timing attacks
    if not secrets.compare_digest(x_service_auth, service_auth_key):
        raise ServiceAuthError("Invalid service authentication key")

    # In production, you might extract caller identity from the key
    # or use Azure Managed Identity to identify the caller
    caller_identity = settings.get('Service.AllowedCallers', ['api-gateway'])[0]

    return caller_identity


async def verify_api_gateway(service_id: str = None) -> bool:
    """
    Additional validation to ensure caller is specifically the API Gateway.

    Args:
        service_id: Service identifier from verify_service_auth

    Returns:
        True if caller is authorized

    Raises:
        ServiceAuthError: If caller is not authorized
    """
    settings = get_settings()
    allowed_callers = settings.get('Service.AllowedCallers', ['api-gateway'])

    if service_id not in allowed_callers:
        raise ServiceAuthError(f"Service '{service_id}' is not authorized to call this endpoint")

    return True


class AzureManagedIdentityAuth:
    """
    Azure Managed Identity authentication for service-to-service calls.

    Use this in production environments where services authenticate via Azure AD.
    """

    def __init__(self):
        self.enabled = get_settings().get('Azure.ManagedIdentityEnabled', False)

    async def verify_managed_identity(self, token: Optional[str] = Header(None, alias="Authorization")):
        """
        Verify Azure AD token from calling service.

        Args:
            token: Bearer token from Authorization header

        Returns:
            Token claims if valid

        Raises:
            ServiceAuthError: If token is invalid
        """
        if not self.enabled:
            return None

        if not token or not token.startswith("Bearer "):
            raise ServiceAuthError("Missing or invalid Authorization header")

        # TODO: Implement Azure AD token validation
        # This would use azure-identity and validate the JWT token
        # For now, this is a placeholder

        raise NotImplementedError("Azure Managed Identity auth not yet implemented")
