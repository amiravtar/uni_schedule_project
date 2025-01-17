from datetime import time
from enum import Enum
from typing import Any, List, Optional

from pydantic import BaseModel, field_validator

from app.schemas.major import MajorRead


class Weekday(int, Enum):
    FRIDAY = 6
    WEDNESDAY = 5
    THURSDAY = 4
    TUESDAY = 3
    MONDAY = 2
    SUNDAY = 1
    SATURDAY = 0


class TimeSlot(BaseModel):
    day: Weekday
    start_time: str
    end_time: str

    @field_validator("start_time", "end_time", mode="before")
    @classmethod
    def normalize_time(cls, value: Any) -> str:
        parsed_time = time.fromisoformat(value)
        return f"{parsed_time.hour:02}:{parsed_time.minute:02}"


class ProfessorBase(BaseModel):
    full_name: str
    major_id: int
    max_hour: int = 0
    min_hour: int = 0
    preferred_days: List[Weekday] = []
    time_slots: List[TimeSlot] = []


class ProfessorCreate(ProfessorBase):
    pass


class ProfessorRead(ProfessorBase):
    id: int
    major: MajorRead

    class Config:
        orm_mode = True


class ProfessorUpdate(BaseModel):
    full_name: Optional[str] = None
    major_id: Optional[int] = None
    max_hour: Optional[int] = None
    min_hour: Optional[int] = None
    preferred_days: Optional[List[Weekday]] = None
    time_slots: Optional[List[TimeSlot]] = None
