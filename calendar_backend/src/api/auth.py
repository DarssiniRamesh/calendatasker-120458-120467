"""Authentication endpoints using Clerk.dev and JWT validation via FastAPI."""

import os
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from typing import Dict, Any
from dotenv import load_dotenv

router = APIRouter(prefix="/auth", tags=["auth"])

# Load environment variables (ensure .env is set up in your root)
load_dotenv()
CLERK_PEM_PUBLIC_KEY = os.getenv("CLERK_PEM_PUBLIC_KEY")
CLERK_JWT_ISSUER = os.getenv("CLERK_JWT_ISSUER", "https://clerk.<region>.clerk.accounts.dev/")  # Replace region as appropriate
CLERK_AUDIENCE = os.getenv("CLERK_AUDIENCE", None)  # e.g., "your-client-id"

security = HTTPBearer()

def _get_public_key() -> str:
    """Retrieve Clerk PEM public key from environment. Ensure to set CLERK_PEM_PUBLIC_KEY."""
    if not CLERK_PEM_PUBLIC_KEY:
        raise RuntimeError("CLERK_PEM_PUBLIC_KEY must be set in your environment variables")
    return CLERK_PEM_PUBLIC_KEY

# PUBLIC_INTERFACE
async def clerk_jwt_required(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> Dict[str, Any]:
    """
    FastAPI dependency to validate Clerk.dev JWT via Authorization: Bearer header.
    Returns the JWT claims on success.
    Raises HTTPException(401) if invalid/missing.
    """
    token = credentials.credentials
    try:
        public_key = _get_public_key()
        payload = jwt.decode(
            token,
            public_key,
            algorithms=["RS256"],
            issuer=CLERK_JWT_ISSUER,
            audience=CLERK_AUDIENCE,
            options={"verify_at_hash": False},
        )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid or expired token: {str(e)}",
        )
    return payload

# PUBLIC_INTERFACE
@router.get("/me", summary="Get current user (JWT-protected)")
async def read_current_user(
    user_claims: Dict[str, Any] = Depends(clerk_jwt_required),
):
    """
    Retrieve current user info from Clerk JWT claims.
    """
    return {"clerk_user_id": user_claims.get("sub"), "email": user_claims.get("email"), "claims": user_claims}


# PUBLIC_INTERFACE
@router.post("/login", summary="Login endpoint (handled by Clerk.dev)", include_in_schema=True)
def login_info():
    """
    This endpoint is informational. All login is handled via Clerk.dev hosted pages or the Frontend.
    See Clerk.dev documentation and frontend for login/signup flows.
    """
    return {"message": "Login is managed externally by Clerk.dev. Use the frontend UI."}


# PUBLIC_INTERFACE
@router.post("/logout", summary="Logout endpoint (handled by Clerk.dev)", include_in_schema=True)
def logout_info():
    """
    This endpoint is informational. All logout is handled via Clerk.dev hosted pages or the Frontend.
    """
    return {"message": "Logout is managed externally by Clerk.dev. Use the frontend UI."}


# PUBLIC_INTERFACE
@router.post("/register", summary="Register endpoint (handled by Clerk.dev)", include_in_schema=True)
def register_info():
    """
    This endpoint is informational. All registration is handled via Clerk.dev hosted pages or the Frontend.
    """
    return {"message": "Register/signup is managed externally by Clerk.dev. Use the frontend UI."}
