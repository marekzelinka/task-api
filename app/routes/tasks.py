from fastapi import APIRouter, Depends, status
from sqlmodel import Session

from app.database.config import get_session
from app.models.task import Task, TaskCreate, TaskRead

router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
def create_task(*, session: Session = Depends(get_session), task: TaskCreate):
    db_task = Task.from_orm(task)
    session.add(db_task)
    session.commit()
    session.refresh(db_task)
    return db_task
