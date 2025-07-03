"""RESTful endpoints for event CRUD, JWT Clerk-protected."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from . import models
from .auth import clerk_jwt_required
from .crud import (
    get_events_for_user,
    get_event,
    create_event,
    delete_event,
)
from pydantic import BaseModel, Field
from .models import Event as EventDB

# DB session dependency stub (replace with real session manager in prod)
def get_db():
    # Typically you'd yield a SQLAlchemy session
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

router = APIRouter(prefix="/events", tags=["events"])

# Pydantic models
class EventBase(BaseModel):
    title: str = Field(..., description="Event title")
    description: str | None = Field(None, description="Event description")
    start_time: datetime = Field(..., description="Event start datetime")
    end_time: datetime = Field(..., description="Event end datetime")
    location: str | None = Field(None, description="Event location")
    is_all_day: bool = Field(False, description="Is all-day event")

class EventCreate(EventBase):
    pass

class EventUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    start_time: datetime | None = None
    end_time: datetime | None = None
    location: str | None = None
    is_all_day: bool | None = None

class EventOut(EventBase):
    id: int
    is_upcoming: bool = Field(..., description="True if event is within 48h or active")
    class Config:
        orm_mode = True

def is_event_upcoming(event: EventDB) -> bool:
    now = datetime.utcnow()
    # Consider upcoming if in next 48 hours or ongoing now
    if event.start_time <= now <= event.end_time:
        return True
    return (event.start_time - now) <= timedelta(hours=48)

# PUBLIC_INTERFACE
@router.get("/", response_model=List[EventOut], summary="List all events for user")
async def list_events(
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    """Retrieve all events for the authenticated user."""
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_events = get_events_for_user(db, user.id)
    result = []
    for evt in db_events:
        evt_dict = EventOut.from_orm(evt).dict()
        evt_dict['is_upcoming'] = is_event_upcoming(evt)
        result.append(EventOut(**evt_dict))
    return result

# PUBLIC_INTERFACE
@router.post("/", response_model=EventOut, summary="Create a new event")
async def create_event_endpoint(
    data: EventCreate,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    "Create a new calendar event for the authenticated user."
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    evt = EventDB(
        user_id=user.id,
        **data.dict(),
    )
    evt = create_event(db, evt)
    evt_data = EventOut.from_orm(evt).dict()
    evt_data['is_upcoming'] = is_event_upcoming(evt)
    return EventOut(**evt_data)

# PUBLIC_INTERFACE
@router.get("/{event_id}", response_model=EventOut, summary="Get event by ID")
async def get_event_by_id(
    event_id: int,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    "Get a single event by ID (must belong to the user)."
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    evt = get_event(db, event_id, user.id)
    if not evt:
        raise HTTPException(status_code=404, detail="Event not found")
    evt_data = EventOut.from_orm(evt).dict()
    evt_data['is_upcoming'] = is_event_upcoming(evt)
    return EventOut(**evt_data)

# PUBLIC_INTERFACE
@router.put("/{event_id}", response_model=EventOut, summary="Update event")
async def update_event_endpoint(
    event_id: int,
    data: EventUpdate,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    "Update an event by ID (must belong to user)."
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    evt = get_event(db, event_id, user.id)
    if not evt:
        raise HTTPException(status_code=404, detail="Event not found")
    updated = False
    for field, value in data.dict(exclude_unset=True).items():
        setattr(evt, field, value)
        updated = True
    if updated:
        db.commit()
        db.refresh(evt)
    evt_data = EventOut.from_orm(evt).dict()
    evt_data['is_upcoming'] = is_event_upcoming(evt)
    return EventOut(**evt_data)

# PUBLIC_INTERFACE
@router.delete("/{event_id}", response_model=dict, summary="Delete event")
async def delete_event_endpoint(
    event_id: int,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    "Delete an event by ID (must belong to user)."
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    evt = delete_event(db, event_id, user.id)
    if not evt:
        raise HTTPException(status_code=404, detail="Event not found or no permission")
    return {"result": "deleted", "event_id": event_id}

