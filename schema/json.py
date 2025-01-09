from typing import Any

from pydantic import BaseModel
from typing_extensions import TypedDict


class Professor(BaseModel):
    id: str
    name: str
    pref_days: list[int]
    days: list[str]


class Course(BaseModel):
    id: str
    name: str
    units: int
    duration: str
    semister: int
    professors: list[str]


class Data(BaseModel):
    professors: list[Professor]
    courses: list[Course]


class RootSchema(BaseModel):
    data: Data
    settings: dict[str, Any]


class ResualtCourse(BaseModel):
    id: str
    # name: str
    # units: int
    # duration: str
    # semister: int
    day: int
    start: str
    end: str
    professor_id: str
    is_prefered_time: bool


class ResualtDict(TypedDict):
    score: int
    courses: list[ResualtCourse]


class ModelResualt(BaseModel):
    resualts: list[ResualtDict]
