from typing import Any
from pydantic import BaseModel


class Professor(BaseModel):
    id: int
    name: str
    pref_days: list[int]
    days: list[str]


class Course(BaseModel):
    id: int
    name: str
    units: int
    duration: str
    semister: int
    professors: list[int]


class Data(BaseModel):
    professors: list[Professor]
    courses: list[Course]


class RootSchema(BaseModel):
    data: Data
    settings: dict[str, Any]


class ResualtCourse(BaseModel):
    id: int
    name: str
    units: int
    duration: str
    semister: int
    day: int
    start: str
    end: str
    professor_id: int
    is_prefered_time: bool


class ModelResualt(BaseModel):
    resualts: list[list[ResualtCourse]]
