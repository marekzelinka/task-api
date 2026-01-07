from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.main import api_router
from .core.config import config
from .core.db import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield


app = FastAPI(
    title="Task Management API",
    description="REST API for managing tasks",
    lifespan=lifespan,
)

# Set all CORS enabled origins
if config.all_cors_origins:
    app.add_middleware(
        CORSMiddleware,  # ty:ignore[invalid-argument-type]
        allow_origins=config.all_cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(api_router, prefix="/api")
