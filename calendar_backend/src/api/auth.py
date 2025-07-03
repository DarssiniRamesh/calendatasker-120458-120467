"""Authentication endpoints using Clerk.dev (placeholder)."""

from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["auth"])

# PUBLIC_INTERFACE
@router.get("/me")
def read_current_user():
    """
    Placeholder for retrieving current user info via Clerk.dev authentication.
    """
    # TODO: Integrate Clerk sessions/JWT claim verification.
    return {"message": "User info would be fetched from Clerk.dev"}
