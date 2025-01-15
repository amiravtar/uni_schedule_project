from decimal import Decimal
from typing import Any, ClassVar, Optional

from pydantic import BaseModel, Field, field_validator


def convert_time_to_min(time: int):  # hhmm
    """Converts time in hhmm format to minutes
    :param time: _description_
    :type time: int
    :return: _description_
    :rtype: _type_
    """
    hours = time // 100
    minutes = time % 100
    total_minutes = hours * 60 + minutes
    return total_minutes


def minutes_to_time(total_minutes: int):
    # total_minutes = total_minutes % 1440  # Wrap around at 1440 minutes (24 hours)
    hours = total_minutes // 60
    minutes = total_minutes % 60
    return str(hours * 100 + minutes).zfill(4)


class CourceTimeSlots(BaseModel):
    day: int
    start_time: str  # hhmm
    end_time: str  # hhmm
    prof: int
    original_start: str
    prefered: bool

    def __hash__(self) -> int:
        return hash(
            (
                self.day,
                self.start_time,
                self.end_time,
                self.prof,
                self.prefered,
                self.original_start,
            )
        )


class Courses(BaseModel):
    id: int
    title: str
    units: int
    duration: str  # hh:mm
    semester: int
    calculated_hours: (
        int  # multiply the input decimal value by 100 so it gets converted to int
    )
    major_id: int
    classroom_id: int
    max_classes: int  # to determine the maximume of this kind of class at the same time
    time_slots: list[
        CourceTimeSlots
    ]  # convert the basic professor times to time slots for courses
    group_id: int  # major_id * 10 + semester, need to be uniqe among all courses
    major_name: str
    classroom_name: str

    def __hash__(self) -> int:
        return hash(self.id)


class SolverSettings(BaseModel):
    number_of_solutions: int
    classroom_limitation: bool = True
    professor_min_max_time_limitation: bool = True


class SolverInputData(BaseModel):
    courses: list[Courses]
    settings: SolverSettings


class SolverCourseSelectedDate(BaseModel):
    day: int
    professor_id: int
    professor_name: str
    start_time: str  # hh:mm
    end_time: str  # hh:mm
    prefered: bool

    @field_validator("start_time", "end_time", mode="before")
    def normalize_time(cls, value: Any) -> str:
        return f"{value[:2]}:{value[2:]}"


class SolverSolutionCourse(Courses):
    selected_slot: SolverCourseSelectedDate
    time_slots: ClassVar[list] # type: ignore

    class Config:
        fields = {"time_slots": {"exclude": True}}


class SolverSolution(BaseModel):
    courses: list[SolverSolutionCourse]


class SolverResualt(BaseModel):
    Solutions: list[SolverSolution]
