from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import create_db_and_tables
from app.routers import tasks


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Task Management API",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(tasks.router)


@app.get("/", tags=["status"], description="Healthcheck endpoint for the API")
async def read_healthcheck():
    return {"message": "Welcome to the Task Management API"}
