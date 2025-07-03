"""CRUD logic for events and tasks."""

from sqlalchemy.orm import Session
from . import models

# PUBLIC_INTERFACE
def get_events_for_user(db: Session, user_id: int):
    """Retrieve all events for a given user."""
    return db.query(models.Event).filter(models.Event.user_id == user_id).all()

# PUBLIC_INTERFACE
def get_event(db: Session, event_id: int, user_id: int):
    """Get a single event by ID (must belong to user)."""
    return db.query(models.Event).filter(
        models.Event.id == event_id, models.Event.user_id == user_id
    ).first()

# PUBLIC_INTERFACE
def create_event(db: Session, event: models.Event):
    """Create a new event and add it to the DB."""
    db.add(event)
    db.commit()
    db.refresh(event)
    return event

# PUBLIC_INTERFACE
def delete_event(db: Session, event_id: int, user_id: int):
    """Delete an event (must belong to user)."""
    event = get_event(db, event_id, user_id)
    if event:
        db.delete(event)
        db.commit()
    return event

# PUBLIC_INTERFACE
def get_tasks_for_user(db: Session, user_id: int):
    """Retrieve all tasks for a given user."""
    return db.query(models.Task).filter(models.Task.user_id == user_id).all()

# PUBLIC_INTERFACE
def get_task(db: Session, task_id: int, user_id: int):
    """Get a single task by ID (must belong to user)."""
    return db.query(models.Task).filter(
        models.Task.id == task_id, models.Task.user_id == user_id
    ).first()

# PUBLIC_INTERFACE
def create_task(db: Session, task: models.Task):
    """Create a new task and add it to the DB."""
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

# PUBLIC_INTERFACE
def delete_task(db: Session, task_id: int, user_id: int):
    """Delete a task (must belong to user)."""
    task = get_task(db, task_id, user_id)
    if task:
        db.delete(task)
        db.commit()
    return task
