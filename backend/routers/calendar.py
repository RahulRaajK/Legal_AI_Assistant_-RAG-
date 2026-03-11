from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from backend.database import get_db
from backend.models.calendar import CourtHoliday

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])

@router.get("/holidays")
async def list_holidays(db: AsyncSession = Depends(get_db)):
    """List all court holidays"""
    result = await db.execute(select(CourtHoliday).order_by(CourtHoliday.holiday_date.asc()))
    holidays = result.scalars().all()
    return [
        {
            "id": h.id,
            "holiday_date": h.holiday_date.isoformat(),
            "description": h.description,
            "is_working_day": h.is_working_day
        }
        for h in holidays
    ]
