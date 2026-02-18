from fastapi import FastAPI

from app.core.config import config
from app.deps import SessionDep
from app.routers import auth, labels, projects, tasks, users

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


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(labels.router)


@app.get("/health", tags=["status"])
async def read_health(*, _session: SessionDep) -> dict:
    return {"status": "ok"}
