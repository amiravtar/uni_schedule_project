from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy.dialects.postgresql import ARRAY
from sqlmodel import JSON, Column, Field, Relationship, SQLModel

from app.models.course import CourseProfessorLink
from app.schemas.professors import TimeSlot, Weekday

if TYPE_CHECKING:
    from app.models.major import Major

    from .course import Course


class Professor(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    full_name: str
    major_id: int = Field(foreign_key="major.id")
    max_hour: int = 0
    min_hour: int = 0
    preferred_days: List[Weekday] = Field(default=[], sa_column=Column(JSON))
    time_slots: List[TimeSlot] = Field(default=[], sa_column=Column(JSON))
    major: Optional["Major"] = Relationship(back_populates="professors")

    courses: List["Course"] = Relationship(
        back_populates="professors", link_model=CourseProfessorLink
    )
