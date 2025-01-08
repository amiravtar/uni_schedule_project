from typing import Optional

from pydantic import BaseModel


class ClassroomCreate(BaseModel):
    name: str
    available_classes: int


class ClassroomUpdate(BaseModel):
    name: Optional[str] = None
    available_classes: Optional[int] = None


class ClassroomRead(BaseModel):
    id: int
    name: str
    available_classes: int
