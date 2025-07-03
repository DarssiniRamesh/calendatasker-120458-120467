"""RESTful endpoints for reminders/notifications. Clerk JWT required for all."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List

from .auth import clerk_jwt_required
from .models import User
from pydantic import BaseModel, Field

def get_db():
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    import os
    DB_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.sqlite3")
    engine = create_engine(DB_URL, connect_args={"check_same_thread": False})
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

router = APIRouter(prefix="/reminders", tags=["reminders"])

# For demonstration, this model isn't persisted
class Reminder(BaseModel):
    id: int
    user_id: int
    message: str
    remind_at: datetime
    is_upcoming: bool = Field(..., description="Within the next hour")

reminder_memory_db = []

def is_reminder_upcoming(remind_at: datetime) -> bool:
    return 0 <= (remind_at - datetime.utcnow()).total_seconds() <= 3600

# PUBLIC_INTERFACE
@router.get("/", response_model=List[Reminder], summary="List reminders for current user (demo)")
async def list_reminders(
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    """List all reminders for user (stub - use memory DB, replace with persistent storage/logic)."""
    clerk_id = user_claims["sub"]
    user = db.query(User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    # Filter memory reminders for user
    results = []
    for r in reminder_memory_db:
        if r['user_id'] == user.id:
            results.append(Reminder(**{
                **r,
                "is_upcoming": is_reminder_upcoming(r['remind_at'])
            }))
    return results

# PUBLIC_INTERFACE
@router.post("/", response_model=Reminder, summary="Create a reminder (demo)")
async def create_reminder(
    data: Reminder,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    """Create reminder for current user (stub, no notification sends)."""
    clerk_id = user_claims["sub"]
    user = db.query(User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    new_id = len(reminder_memory_db) + 1
    reminder = data.dict()
    reminder["id"] = new_id
    reminder["user_id"] = user.id
    reminder_memory_db.append(reminder)
    reminder["is_upcoming"] = is_reminder_upcoming(reminder["remind_at"])
    return Reminder(**reminder)

# PUBLIC_INTERFACE
@router.get("/{reminder_id}", response_model=Reminder, summary="Fetch single reminder (demo)")
async def get_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    """Fetch a specific reminder."""
    clerk_id = user_claims["sub"]
    user = db.query(User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    r = next((r for r in reminder_memory_db if r["id"] == reminder_id and r["user_id"] == user.id), None)
    if not r:
        raise HTTPException(status_code=404, detail="Reminder not found")
    r["is_upcoming"] = is_reminder_upcoming(r["remind_at"])
    return Reminder(**r)

# PUBLIC_INTERFACE
@router.delete("/{reminder_id}", response_model=dict, summary="Delete reminder (demo)")
async def delete_reminder(
    reminder_id: int,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    """Delete a reminder (demo)."""
    clerk_id = user_claims["sub"]
    user = db.query(User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    idx = next((i for i, r in enumerate(reminder_memory_db) if r["id"] == reminder_id and r["user_id"] == user.id), None)
    if idx is None:
        raise HTTPException(status_code=404, detail="Reminder not found or no permission")
    reminder_memory_db.pop(idx)
    return {"result": "deleted", "reminder_id": reminder_id}
