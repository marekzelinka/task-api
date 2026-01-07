from fastapi import FastAPI

from app.database.config import create_db_and_tables
from app.routes import tasks

app = FastAPI(
    title="Task Management API",
    description="API for managing tasks with FastAPI, SQLModel, and Pydantic",
    version="0.1.0",
)

app.include_router(tasks.router)


@app.get("/")
async def root():
    """Health check endpoint for the API."""
    return {"message": "Welcome to the Task Management API"}


@app.on_event("startup")
def on_startup():
    create_db_and_tables()
