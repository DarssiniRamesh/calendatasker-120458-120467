"""Notification subsystem (stub)."""

from fastapi import APIRouter

router = APIRouter(prefix="/reminders", tags=["reminders"])

# PUBLIC_INTERFACE
@router.get("/")
def list_reminders():
    """
    Placeholder endpoint for listing reminders or sending notifications.
    """
    # TODO: Integrate with background jobs, email reminders, Resend API, etc.
    return {"message": "Reminder/notification API stub"}
