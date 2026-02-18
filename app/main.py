from fastapi import FastAPI

from app.api import api_router
from app.core.config import config
from app.deps import SessionDep
from app.models import HealthCheck, Message

app = FastAPI(
    title="Task Management API",
    description="API for managing tasks with FastAPI, SQLModel, and Pydantic.",
    version="0.1.0",
)

# Set all CORS enabled origins
if config.all_cors_origins:
    from fastapi.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,  # ty:ignore[invalid-argument-type]
        allow_origins=config.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


app.include_router(api_router)


@app.get("/")
async def root() -> Message:
    """Health check endpoint for the API."""
    return Message("Welcome to the Task Management API")


@app.get("/health", tags=["status"])
async def read_health(*, _session: SessionDep) -> HealthCheck:
    return HealthCheck(status="ok")
