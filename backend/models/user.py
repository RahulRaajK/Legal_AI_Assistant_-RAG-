"""User model for authentication and role management."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Boolean, Enum as SAEnum, Text
from sqlalchemy.orm import relationship
from backend.database import Base
import enum


class UserRole(str, enum.Enum):
    JUDGE = "judge"
    LAWYER = "lawyer"
    ADVOCATE = "advocate"
    CITIZEN = "citizen"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRole.CITIZEN.value)
    bar_council_id = Column(String, nullable=True)  # For lawyers/advocates
    court_name = Column(String, nullable=True)  # For judges
    specialization = Column(String, nullable=True)  # For lawyers profile
    about = Column(Text, nullable=True)  # For lawyers profile
    phone = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cases = relationship("Case", back_populates="user", lazy="selectin")
    chat_sessions = relationship("ChatSession", back_populates="user", lazy="selectin")
