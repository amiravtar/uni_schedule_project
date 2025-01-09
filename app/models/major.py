from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .course import Course
    from .professor import Professor


class Major(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    semesters: int

    professors: list["Professor"] = Relationship(back_populates="major")
    courses: list["Course"] = Relationship(back_populates="major")
