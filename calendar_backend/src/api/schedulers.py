"""Background scheduling endpoints (stub)."""

from fastapi import APIRouter

router = APIRouter(prefix="/schedulers", tags=["schedulers"])

# PUBLIC_INTERFACE
@router.get("/")
def scheduling_root():
    """
    Placeholder for scheduler (APScheduler) integration.
    """
    return {"message": "Scheduler (APScheduler) API stub"}
