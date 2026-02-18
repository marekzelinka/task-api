import uuid
from collections.abc import Sequence
from datetime import UTC, datetime, time
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from sqlmodel import col, select

from app.deps import CurrentUserDep, SessionDep
from app.models import (
    Label,
    Project,
    Task,
    TaskCreate,
    TaskLabelLink,
    TaskPublic,
    TaskPublicWithLabels,
    TaskPublicWithProject,
    TaskPublicWithProjectLabels,
    TaskUpdate,
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=TaskPublic)
async def create_task(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    task: Annotated[TaskCreate, Body()],
) -> Task:
    db_task = Task.model_validate(task, update={"owner_id": current_user.id})

    session.add(db_task)

    await session.commit()
    await session.refresh(db_task)

    return db_task


@router.post(
    "/{task_id}/duplicate",
    status_code=status.HTTP_201_CREATED,
    response_model=TaskPublic,
)
async def create_task_copy(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    task_id: Annotated[uuid.UUID, Path()],
) -> Task:
    task = await session.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    task_data = task.model_dump(exclude={"id", "completed", "created_at", "updated_at"})

    copy_title = f"{task.title} (Copy)"
    task_copy = Task.model_validate(task_data, update={"title": copy_title})

    session.add(task_copy)

    await session.commit()
    await session.refresh(task_copy)

    return task_copy



@router.get("", response_model=list[TaskPublic])
async def read_tasks(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 100,
    completed: Annotated[bool | None, Query()] = None,
    priority: Annotated[int | None, Query(ge=1, le=5)] = None,
) -> Sequence[Task]:
    query = select(Task).where(Task.owner_id == current_user.id)
    if completed is not None:
        query = query.where(Task.completed == completed)
    if priority is not None:
        query = query.where(Task.priority == priority)

    results = await session.scalars(query.offset(offset).limit(limit))
    tasks = results.all()

    return tasks


@router.get("/upcomming", response_model=list[TaskPublic])
async def read_upcomming_tasks(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 100,
    priority: Annotated[int | None, Query(ge=1, le=5)] = None,
) -> Sequence[Task]:
    now = datetime.now(tz=UTC)

    query = (
        select(Task)
        .where(Task.owner_id == current_user.id)
        .where(col(Task.due_date) > now)
        .where(~col(Task.completed))
    )
    if priority is not None:
        query = query.where(Task.priority == priority)

    results = await session.scalars(
        query.order_by(col(Task.due_date).asc().nulls_last())
        .offset(offset)
        .limit(limit)
    )
    upcomming_tasks = results.all()

    return upcomming_tasks


@router.get("/today", response_model=list[TaskPublic])
async def read_due_today_tasks(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 100,
    priority: Annotated[int | None, Query(ge=1, le=5)] = None,
) -> Sequence[Task]:
    now = datetime.now(tz=UTC)
    today_end = datetime.combine(now.date(), time.max, tzinfo=UTC)
    today_start = datetime.combine(now.date(), time.min, tzinfo=UTC)

    query = (
        select(Task)
        .where(Task.owner_id == current_user.id)
        .where(col(Task.due_date).between(today_start, today_end))
        .where(~col(Task.completed))
    )
    if priority is not None:
        query = query.where(Task.priority == priority)

    results = await session.scalars(query.offset(offset).limit(limit))
    today_tasks = results.all()

    return today_tasks


@router.get("/overdue", response_model=list[TaskPublic])
async def read_overdue_tasks(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 100,
    priority: Annotated[int | None, Query(ge=1, le=5)] = None,
) -> Sequence[Task]:
    now = datetime.now(tz=UTC)

    query = (
        select(Task)
        .where(Task.owner_id == current_user.id)
        .where(col(Task.due_date) < now)
        .where(~col(Task.completed))
    )
    if priority is not None:
        query = query.where(Task.priority == priority)

    results = await session.scalars(query.offset(offset).limit(limit))
    overdue_tasks = results.all()

    return overdue_tasks


@router.get("/{task_id}", response_model=TaskPublicWithProjectLabels)
async def read_task(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    task_id: Annotated[uuid.UUID, Path()],
) -> Task:
    task = await session.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    return task


@router.patch("/{task_id}/projects/{project_id}", response_model=TaskPublicWithProject)
async def assign_task_to_project(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    task_id: Annotated[uuid.UUID, Path()],
    project_id: Annotated[uuid.UUID, Path()],
) -> Task:
    task = await session.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    project = await session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    task.project_id = project.id

    await session.commit()
    await session.refresh(task)

    return task


@router.patch("/{task_id}/labels/{label_id}", response_model=TaskPublicWithLabels)
async def assign_label_to_task(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    task_id: Annotated[uuid.UUID, Path()],
    label_id: Annotated[uuid.UUID, Path()],
) -> Task:
    task = await session.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    label = await session.get(Label, label_id)
    if not label or label.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Label not found"
        )
    if label in task.labels:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="Label already assigned to task",
        )

    task_label_link = TaskLabelLink(task_id=task_id, label_id=label_id)

    session.add(task_label_link)

    await session.commit()
    await session.refresh(task)

    return task


@router.patch("/{task_id}", response_model=TaskPublicWithProject)
async def update_task(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    task_id: Annotated[uuid.UUID, Path()],
    task: Annotated[TaskUpdate, Body()],
) -> Task:
    db_task = await session.get(Task, task_id)
    if not db_task or db_task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    task_data = task.model_dump(exclude_unset=True)
    db_task.sqlmodel_update(task_data)

    session.add(db_task)

    await session.commit()
    await session.refresh(db_task)

    return db_task


@router.delete(
    "/{task_id}/projects/{project_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def remove_task_from_project(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    task_id: Annotated[uuid.UUID, Path()],
    project_id: Annotated[uuid.UUID, Path()],
) -> None:
    task = await session.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    project = await session.get(Project, project_id)
    if not project or project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Project not found"
        )

    task.project_id = None

    await session.commit()
    await session.refresh(task)


@router.delete("/{task_id}/labels/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_label_from_task(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    task_id: Annotated[uuid.UUID, Path()],
    label_id: Annotated[uuid.UUID, Path()],
) -> None:
    task = await session.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    label = await session.get(Label, label_id)
    if not label or label.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Label not found"
        )

    task_label_link = await session.get(
        TaskLabelLink,
        (
            task_id,
            label_id,
        ),
    )
    if not task_label_link:
        raise HTTPException(
            status_code=status.HTTP_304_NOT_MODIFIED,
            detail="Label wasn't assigned to task",
        )

    await session.delete(task_label_link)
    await session.commit()


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    task_id: Annotated[uuid.UUID, Path()],
) -> None:
    task = await session.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )

    await session.delete(task)
    await session.commit()
