from __future__ import annotations

from datetime import UTC, datetime
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
)


class UserBase(BaseModel):
    username: str
    email: EmailStr


class UserCreate(UserBase):
    password: str


class UserPublic(UserBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class Token(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    access_token: str
    token_type: str


class ProjectCreate(BaseModel):
    title: str


class ProjectUpdate(BaseModel):
    title: str | None = None


class ProjectPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    created_at: datetime


def check_due_date_is_future(due_date: datetime | None) -> datetime | None:
    if due_date is not None and due_date < datetime.now(tz=UTC):
        raise ValueError("due_date must be in the future")
    return due_date


class TaskCreate(BaseModel):
    title: str
    description: str | None = None
    priority: Annotated[int, Field(ge=1, le=5)] = 1
    completed: bool = False
    due_date: Annotated[datetime | None, AfterValidator(check_due_date_is_future)] = (
        None
    )
    project_id: int | None = None


class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: Annotated[int | None, Field(ge=1, le=5)] = None
    completed: bool | None = None
    due_date: Annotated[datetime | None, AfterValidator(check_due_date_is_future)] = (
        None
    )
    project_id: int | None = None


class TaskPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str | None
    priority: Annotated[int, Field(ge=1, le=5)]
    completed: bool
    due_date: datetime | None
    project_id: int | None


class TaskPublicWithProject(TaskPublic):
    project: ProjectPublic | None = None


class TaskPublicWithLabels(TaskPublic):
    labels: list[LabelPublic] = []


class TaskPublicWithProjectLabels(TaskPublicWithProject, TaskPublicWithLabels):
    pass


class LabelBase(BaseModel):
    name: str


class LabelCreate(LabelBase):
    pass


class LabelUpdate(BaseModel):
    name: str | None = None


class LabelPublic(LabelBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class LabelPublicWithTasks(LabelPublic):
    tasks: list[TaskPublic] = []
