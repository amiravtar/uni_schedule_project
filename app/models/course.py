from datetime import time
from decimal import Decimal
from typing import TYPE_CHECKING, List, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.classroom import Classroom
    from app.models.major import Major
    from app.models.professor import Professor


class CourseProfessorLink(SQLModel, table=True):
    course_id: int = Field(foreign_key="course.id", primary_key=True, default=None)
    professor_id: int = Field(
        foreign_key="professor.id", primary_key=True, default=None
    )

class Course(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    title: str
    units: int
    duration: str  # Stored as "hh:mm" format
    semester: int
    calculated_hours: Decimal = Field(max_digits=2, decimal_places=1)

    major_id: int = Field(foreign_key="major.id")
    classroom_id: int = Field(foreign_key="classroom.id")

    professors: List["Professor"] = Relationship(
        back_populates="courses", link_model=CourseProfessorLink
    )
    major: Optional["Major"] = Relationship(back_populates="courses")
    classroom: Optional["Classroom"] = Relationship(back_populates="courses")
