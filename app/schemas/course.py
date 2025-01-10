from datetime import time
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.classroom import ClassroomRead
from app.schemas.major import MajorRead
from app.schemas.professors import ProfessorRead


class CourseBase(BaseModel):
    title: str
    units: int = Field(gt=0)  # Units must be greater than 0
    duration: str = Field(pattern=r"^\d{2}:\d{2}$")  # Validates "hh:mm" format
    semester: int = Field(gt=0, lt=11)  # Semester must be greater than 0
    calculated_hours: Decimal = Field(max_digits=2, decimal_places=1)
    major_id: int
    classroom_id: int


class CourseCreate(CourseBase):
    professor_ids: List[int] = []  # IDs for professors to link


class CourseRead(CourseBase):
    id: int
    professors: List[ProfessorRead] = []
    major: Optional[MajorRead]
    classroom: Optional[ClassroomRead]

    class Config:
        orm_mode = True


class CourseUpdate(BaseModel):
    title: Optional[str] = None
    units: Optional[int] = Field(gt=0)
    duration: Optional[str] = Field(pattern=r"^\d{2}:\d{2}$")
    semester: Optional[int] = Field(gt=0, lt=11)
    calculated_hours: Optional[Decimal] = Field(max_digits=2, decimal_places=1)
    major_id: Optional[int] = None
    classroom_id: Optional[int] = None
    professor_ids: Optional[List[int]] = None
