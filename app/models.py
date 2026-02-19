from __future__ import annotations

import re
from datetime import UTC, datetime
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, EmailStr, Field


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


def check_hex_color(color: str | None) -> str | None:
    if color is None:
        return None
    if not re.match(r"^#(?:[0-9a-fA-F]{3}){1,2}$", color):
        raise ValueError("color must be in hex format (e.g., #fff or #ffffff)")
    return color.lower()


class ProjectCreate(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=255)]
    color: Annotated[str | None, AfterValidator(check_hex_color)] = "#ffffff"


class ProjectUpdate(BaseModel):
    title: Annotated[str | None, Field(max_length=255)] = None
    color: Annotated[str | None, AfterValidator(check_hex_color)] = None


class ProjectPublic(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    color: str | None
    created_at: datetime


def check_due_date_is_future(due_date: datetime | None) -> datetime | None:
    if due_date is not None and due_date < datetime.now(tz=UTC):
        raise ValueError("due_date must be in the future")
    return due_date


class TaskCreate(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=255)]
    description: Annotated[str | None, Field(max_length=500)] = None
    priority: Annotated[int, Field(ge=1, le=5)] = 1
    completed: bool = False
    due_date: Annotated[datetime | None, AfterValidator(check_due_date_is_future)] = (
        None
    )
    project_id: int | None = None


class TaskUpdate(BaseModel):
    title: Annotated[str | None, Field(max_length=255)] = None
    description: Annotated[str | None, Field(max_length=500)] = None
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
    name: Annotated[str, Field(min_length=1, max_length=50)]


class LabelCreate(LabelBase):
    pass


class LabelUpdate(BaseModel):
    name: Annotated[str | None, Field(max_length=50)] = None


class LabelPublic(LabelBase):
    model_config = ConfigDict(from_attributes=True)

    id: int


class LabelPublicWithTasks(LabelPublic):
    tasks: list[TaskPublic] = []
