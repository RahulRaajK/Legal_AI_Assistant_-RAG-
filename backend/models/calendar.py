"""Calendar models for tracking court holidays and hearings."""
import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, Date, Boolean
from backend.database import Base


class CourtHoliday(Base):
    __tablename__ = "court_holidays"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    holiday_date = Column(Date, unique=True, index=True, nullable=False)
    description = Column(String, nullable=False)
    is_working_day = Column(Boolean, default=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
