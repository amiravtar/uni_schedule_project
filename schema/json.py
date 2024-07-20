from typing import Any
from pydantic import BaseModel


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
