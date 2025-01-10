from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field


class CourceTimeSlots(BaseModel):
    day: int
    start_time: int  # use convert_time_to_min to convert hh:mm to int format
    end_time: int  # use convert_time_to_min to convert hh:mm to int format
    prof: int
    original_start: str
    prefered: bool
    professor_max_time: Optional[int]
    professor_min_time: Optional[int]


class Cources(BaseModel):
    id: int
    title: str
    units: int
    duration: str  # hh:mm
    semester: int
    calculated_hours: Decimal = Field(max_digits=2, decimal_places=1)
    major_id: int
    classroom_id: int
    max_classes: int  # to determine the maximume of this kind of class at the same time
    time_slots: list[
        CourceTimeSlots
    ]  # convert the basic professor times to time slots for courses
    group_id: int  # major_id * 10 + semester, need to be uniqe among all courses


class SolverSettings(BaseModel):
    number_of_solutions: int
    classroom_limitation: bool = True
    professor_min_max_time_limitation: bool = True


class SolverInputData(BaseModel):
    courses: list[Cources]
    settings: SolverSettings
