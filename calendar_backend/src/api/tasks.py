"""RESTful endpoints for task CRUD (including status), JWT Clerk-protected."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from typing import List

from . import models
from .auth import clerk_jwt_required
from .crud import (
    get_tasks_for_user,
    get_task,
    create_task,
    delete_task,
)
from pydantic import BaseModel, Field
from .models import Task as TaskDB

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

router = APIRouter(prefix="/tasks", tags=["tasks"])

class TaskBase(BaseModel):
    title: str = Field(..., description="Task title")
    description: str | None = Field(None, description="Task description")
    due_date: datetime | None = Field(None, description="Due date")
    is_completed: bool = Field(False, description="Is task completed")

class TaskCreate(TaskBase):
    pass

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    due_date: datetime | None = None
    is_completed: bool | None = None

class TaskOut(TaskBase):
    id: int
    is_pending: bool = Field(..., description="Task is open and due within 48h or overdue")
    class Config:
        orm_mode = True

def is_task_pending(task: TaskDB) -> bool:
    if task.is_completed:
        return False
    now = datetime.utcnow()
    if task.due_date:
        if task.due_date < now:
            return True
        return (task.due_date - now) <= timedelta(hours=48)
    return True  # No due date tasks: treat as always pending

# PUBLIC_INTERFACE
@router.get("/", response_model=List[TaskOut], summary="List all tasks for user")
async def list_tasks(
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    """Retrieve all tasks for the authenticated user."""
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    db_tasks = get_tasks_for_user(db, user.id)
    result = []
    for t in db_tasks:
        t_dict = TaskOut.from_orm(t).dict()
        t_dict['is_pending'] = is_task_pending(t)
        result.append(TaskOut(**t_dict))
    return result

# PUBLIC_INTERFACE
@router.post("/", response_model=TaskOut, summary="Create a new task")
async def create_task_endpoint(
    data: TaskCreate,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    "Create a new task for the authenticated user."
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    t = TaskDB(
        user_id=user.id,
        **data.dict(),
    )
    t = create_task(db, t)
    t_data = TaskOut.from_orm(t).dict()
    t_data['is_pending'] = is_task_pending(t)
    return TaskOut(**t_data)

# PUBLIC_INTERFACE
@router.get("/{task_id}", response_model=TaskOut, summary="Get task by ID")
async def get_task_by_id(
    task_id: int,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    "Get a single task by ID (must belong to the user)."
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    t = get_task(db, task_id, user.id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    t_data = TaskOut.from_orm(t).dict()
    t_data['is_pending'] = is_task_pending(t)
    return TaskOut(**t_data)

# PUBLIC_INTERFACE
@router.put("/{task_id}", response_model=TaskOut, summary="Update task")
async def update_task_endpoint(
    task_id: int,
    data: TaskUpdate,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    "Update a task by ID (must belong to user, incl. completion status)."
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    t = get_task(db, task_id, user.id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = False
    for field, value in data.dict(exclude_unset=True).items():
        setattr(t, field, value)
        updated = True
    if updated:
        db.commit()
        db.refresh(t)
    t_data = TaskOut.from_orm(t).dict()
    t_data['is_pending'] = is_task_pending(t)
    return TaskOut(**t_data)

# PUBLIC_INTERFACE
@router.delete("/{task_id}", response_model=dict, summary="Delete task")
async def delete_task_endpoint(
    task_id: int,
    db: Session = Depends(get_db),
    user_claims=Depends(clerk_jwt_required),
):
    "Delete a task by ID (must belong to user)."
    clerk_id = user_claims["sub"]
    user = db.query(models.User).filter_by(clerk_id=clerk_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    t = delete_task(db, task_id, user.id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found or no permission")
    return {"result": "deleted", "task_id": task_id}

