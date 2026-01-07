import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class TaskBase(SQLModel):
    title: str = Field(index=True)
    description: str | None = Field(default=None)
    priority: int = Field(default=1, ge=1, le=5)
    completed: bool = Field(default=False)


class Task(TaskBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)},
    )


class TaskCreate(TaskBase):
    pass


class TaskPublic(TaskBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class TaskUpdate(SQLModel):
    title: str | None = None
    description: str | None = None
    priority: int | None = None
    completed: bool | None = None
