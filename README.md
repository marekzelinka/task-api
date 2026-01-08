# Task Managment REST API

This project presents an API for managing tasks using **FastAPI**, **Pydantic** for data validation, and **PostgreSQL** via **Neon**.

## Prerequisites

- This project uses the modern `pyproject.toml` standard for dependency management and requires the `uv` tool to manage the environment:
  - **Ensure `uv` is installed** globally on your system. If not, follow the official installation guide for [`uv`](https://docs.astral.sh/uv/).

- A [Neon account](https://console.neon.tech/signup) for serverless Postgres.


## Setup

1.  **Install project dependencies**

    ```sh
    uv sync
    ```

2.  **Setup env variables**

    ```sh
    cp .env.example .env
    ```


3.  **Start app in dev mode**

    ```sh
    uv run uvicorn app.main:app --reload
    # or if you have 
    just dev
    ```

4.  **Visit OpenAPI docs in browser**

    ```sh
    open http://localhost:8000/docs
    ```

## Development

1. Setup your editor to work with [ruff](https://docs.astral.sh/ruff/editors/setup/) and [ty](https://docs.astral.sh/ty/editors/).

2. Setup [just](https://just.systems/man/en/introduction.html) to run project-specific commands, and also the [justfile extension](https://just.systems/man/en/editor-support.html) for your editor, and use the provided [`justfile`](./justfile) to run commands.


## Tech Stack

- `FastAPI` : A Web / API framework
- `SQLModel` : A library for interacting with SQL databases
- `Uvicorn` : An ASGI server for our app

## Todo

- [ ] user auth
- [ ] projects route 
- [ ] projects have many tasks
- [ ] task belong to one project
- [ ] add `due_date` to tasks
- [ ] bulk actions for tasks, DELETE and PATCH
- [ ] explore async sqlmodel
