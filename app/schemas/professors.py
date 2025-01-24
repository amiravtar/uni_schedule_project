from datetime import datetime, time, timedelta
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

    @field_validator("time_slots", mode="after")
    @classmethod
    def merge_time_slots(cls, value: List[TimeSlot]) -> List[TimeSlot]:
        merged_slots = []

        # Sort time slots by day, then by start_time
        sorted_slots = sorted(value, key=lambda slot: (slot.day.value, slot.start_time))

        for slot in sorted_slots:
            if not merged_slots:
                merged_slots.append(slot)
                continue

            last_slot:TimeSlot = merged_slots[-1]

            # Convert times to datetime objects for comparison
            last_end = datetime.strptime(last_slot.end_time, "%H:%M")
            current_start = datetime.strptime(slot.start_time, "%H:%M")
            current_end = datetime.strptime(slot.end_time, "%H:%M")

            # Check if the slots overlap or are within 15 minutes of each other
            if last_slot.day == slot.day and (
                current_start - last_end <= timedelta(minutes=15)
            ):
                # Merge the slots by extending the end time
                last_slot.end_time = max(last_slot.end_time, slot.end_time)
            else:
                # Add the current slot as a new entry
                merged_slots.append(slot)

        return merged_slots


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
