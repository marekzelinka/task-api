import uuid
from collections.abc import Sequence
from typing import Annotated

from fastapi import APIRouter, Body, HTTPException, Path, Query, status
from sqlmodel import select

from app.deps import CurrentUserDep, SessionDep
from app.models import Label, LabelCreate, LabelPublic, LabelUpdate

router = APIRouter(prefix="/labels", tags=["labels"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=LabelPublic)
async def create_label(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    label: Annotated[LabelCreate, Body()],
) -> Label:
    db_label = Label.model_validate(label, update={"owner_id": current_user.id})

    session.add(db_label)

    await session.commit()
    await session.refresh(db_label)

    return db_label


@router.get("", response_model=list[LabelPublic])
async def read_labels(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(gt=0)] = 100,
    # TODO: add filter query `q`, to fetch labels where name contains `q`
) -> Sequence[Label]:
    results = await session.scalars(
        select(Label)
        .where(Label.owner_id == current_user.id)
        .offset(offset)
        .limit(limit)
    )
    labels = results.all()

    return labels


@router.patch("/{label_id}", response_model=LabelPublic)
async def update_label(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    label_id: Annotated[uuid.UUID, Path()],
    label: Annotated[LabelUpdate, Body()],
) -> Label:
    db_label = await session.get(Label, label_id)
    if not db_label or db_label.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Label not found"
        )

    label_data = label.model_dump(exclude_unset=True)
    db_label.sqlmodel_update(label_data)

    session.add(db_label)

    await session.commit()
    await session.refresh(db_label)

    return db_label


@router.delete("/{label_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_label(
    *,
    session: SessionDep,
    current_user: CurrentUserDep,
    label_id: Annotated[uuid.UUID, Path()],
) -> None:
    label = await session.get(Label, label_id)
    if not label or label.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Label not found"
        )

    await session.delete(label)
    await session.commit()
