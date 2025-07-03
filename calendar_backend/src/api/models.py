"""Database models for users, events, and tasks using SQLAlchemy."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# PUBLIC_INTERFACE
class User(Base):
    """Represents an application user. Typically managed via Clerk.dev."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    clerk_id = Column(String, unique=True, nullable=False, doc="Clerk.dev unique user ID")
    email = Column(String, unique=True, nullable=False)
    full_name = Column(String, nullable=True)

    events = relationship("Event", back_populates="user")
    tasks = relationship("Task", back_populates="user")

# PUBLIC_INTERFACE
class Event(Base):
    """Calendar event model."""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    location = Column(String, nullable=True)
    is_all_day = Column(Boolean, default=False)

    user = relationship("User", back_populates="events")

# PUBLIC_INTERFACE
class Task(Base):
    """To-do task model."""
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    due_date = Column(DateTime, nullable=True)
    is_completed = Column(Boolean, default=False)

    user = relationship("User", back_populates="tasks")
