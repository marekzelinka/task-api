from fastapi import APIRouter, HTTPException, status
from sqlmodel import col, select

from app.core.security import hash_password
from app.deps import CurrentUserDep, SessionDep
from app.models import User, UserCreate, UserPublic

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", status_code=status.HTTP_201_CREATED, response_model=UserPublic)
async def create_user(
    *,
    session: SessionDep,
    user: UserCreate,
) -> User:
    duplicate_username_user = await session.scalar(
        select(User).where(col(User.username).ilike(user.username))
    )
    if duplicate_username_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    duplicate_email_user = await session.scalar(
        select(User).where(col(User.email).ilike(user.email))
    )
    if duplicate_email_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Email already exists"
        )

    new_user = User.model_validate(
        user.model_dump(exclude={"email", "password"}),
        update={
            "email": user.email.lower(),
            "hashed_password": hash_password(user.password),
        },
    )

    session.add(new_user)

    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserPublic)
async def read_users_me(*, current_user: CurrentUserDep) -> User:
    return current_user
