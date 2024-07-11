from typing import List
from pydantic import BaseModel, Field

class Professor(BaseModel):
    id: int
    name: str
    pref_days: List[int]
    days: List[str]

class Course(BaseModel):
    id: int
    name: str
    units: int
    duration: str
    semister: int
    professors: List[int]

class Data(BaseModel):
    professors: List[Professor]
    courses: List[Course]

class RootSchema(BaseModel):
    data: Data
