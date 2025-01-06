from sqlmodel import Field, SQLModel


class Major(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str
    semesters: int
