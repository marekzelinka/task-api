from fastapi import APIRouter, HTTPException, status
from sqlmodel import select

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
    results = await session.exec(select(User).where(User.username == user.username))
    db_user = results.first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered",
        )

    user_dict = user.model_dump()
    new_user = User.model_validate(
        user_dict, update={"hashed_password": hash_password(user.password)}
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.get("/me", response_model=UserPublic)
async def read_users_me(*, current_user: CurrentUserDep) -> User:
    return current_user
