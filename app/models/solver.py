from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

from sqlmodel import JSON, Column, Field, SQLModel


class SolverResualt(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    resualt: dict = Field(sa_column=Column(JSON))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )  # Auto set to current time
