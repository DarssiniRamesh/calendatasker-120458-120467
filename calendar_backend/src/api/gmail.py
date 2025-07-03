"""Gmail integration endpoints (stub)."""

from fastapi import APIRouter

router = APIRouter(prefix="/gmail", tags=["gmail"])

# PUBLIC_INTERFACE
@router.get("/latest")
def fetch_latest_gmail():
    """
    Placeholder for Gmail integration to fetch latest calendar-related emails.
    """
    # TODO: Implement OAuth and Gmail API access.
    return {"message": "Gmail integration API stub"}
