from fastapi import HTTPException, Depends, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional, Dict, Any
from app.api.controllers.auth_controller import get_current_user

# Security scheme for Swagger UI (exported for use in routes)
security = HTTPBearer(
    auto_error=False,
    scheme_name="Bearer",
    description="Enter your Bearer token in the format: Bearer <token>"
)

class AuthMiddleware:
    """Authentication middleware for token validation"""
    
    @staticmethod
    def get_current_user_required(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
        """Get current user with required authentication"""
        if not credentials:
            raise HTTPException(status_code=401, detail="Authentication required")
        
        token = credentials.credentials
        current_user = get_current_user(token)
        
        if not current_user:
            raise HTTPException(status_code=401, detail="Invalid or expired token")
        
        return current_user
    
    @staticmethod
    def get_current_user_optional(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
        """Get current user with optional authentication"""
        if not credentials:
            return None
        
        token = credentials.credentials
        current_user = get_current_user(token)
        
        if not current_user:
            return None
        
        return current_user
    
    @staticmethod
    def require_admin(current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Require admin role"""
        if current_user.get("role") != "admin":
            raise HTTPException(status_code=403, detail="Admin access required")
        
        return current_user
    
    @staticmethod
    def require_company_user(current_user: Dict[str, Any]) -> Dict[str, Any]:
        """Require company user role (not admin)"""
        if current_user.get("role") == "admin":
            raise HTTPException(status_code=403, detail="This endpoint is for company users only, not admins")
        
        if current_user.get("role") != "company":
            raise HTTPException(status_code=403, detail="Company user access required")
        
        return current_user
    
    @staticmethod
    def require_user_or_admin(
        request_data_user_id: str,
        current_user: Dict[str, Any] = Depends(get_current_user_required)
    ) -> Dict[str, Any]:
        """Require either user ownership or admin role"""
        # Admin can access any resource
        if current_user.get("role") == "admin":
            return current_user
        
        # Regular users can only access their own resources
        if current_user["user_id"] != request_data_user_id:
            raise HTTPException(status_code=403, detail="Access denied: You can only access your own resources")
        
        return current_user


# Convenience functions for common use cases
def get_authenticated_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Dict[str, Any]:
    """Dependency for getting authenticated user (required)"""
    if not credentials:
        raise HTTPException(status_code=401, detail="Authentication required")
    
    token = credentials.credentials
    current_user = get_current_user(token)
    
    if not current_user:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    return current_user

def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> Optional[Dict[str, Any]]:
    """Dependency for getting authenticated user (optional)"""
    if not credentials:
        return None
    
    token = credentials.credentials
    current_user = get_current_user(token)
    
    if not current_user:
        return None
    
    return current_user

def require_admin_access(current_user: Dict[str, Any] = Depends(get_authenticated_user)) -> Dict[str, Any]:
    """Dependency for requiring admin access"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

def require_company_user_access(current_user: Dict[str, Any] = Depends(get_authenticated_user)) -> Dict[str, Any]:
    """Dependency for requiring company user access (not admin)"""
    if current_user.get("role") == "admin":
        raise HTTPException(status_code=403, detail="This endpoint is for company users only, not admins")
    if current_user.get("role") != "company":
        raise HTTPException(status_code=403, detail="Company user access required")
    return current_user

def validate_user_access(user_id: str) -> Dict[str, Any]:
    """Dependency factory for validating user access to specific resources"""
    def _validate(current_user: Dict[str, Any] = Depends(get_authenticated_user)) -> Dict[str, Any]:
        return AuthMiddleware.require_user_or_admin(user_id, current_user)
    return _validate
