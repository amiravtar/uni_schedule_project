from pydantic import BaseModel


# Schema for creating a new Major
class MajorCreate(BaseModel):
    name: str
    semesters: int

# Schema for reading Major data
class MajorRead(BaseModel):
    id: int
    name: str
    semesters: int

    class Config:
        orm_mode = True
