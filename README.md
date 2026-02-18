# TODO

Given your SQLModel (SQLAlchemy 2.0 based) setup, here is how the choice applies to your specific schemas:
1. selectinload: Best for Collections
Use this for One-to-Many (User.tasks, Project.tasks) or Many-to-Many (Task.labels).
The Query: SQLAlchemy fetches the parent, then runs a second query: SELECT ... FROM task WHERE task.owner_id IN (...).
Why use it here: If a User has 50 tasks, joinedload would return 50 rows, each repeating the User data (name, email, hashed_password). selectinload avoids this massive data duplication.
python
# Efficiently loads all tasks for the user without duplicating User data
statement = select(User).where(User.id == user_id).options(selectinload(User.tasks))
Use code with caution.

2. joinedload: Best for References
Use this for Many-to-One (Task.project, Task.owner).
The Query: A single LEFT OUTER JOIN.
Why use it here: Since a task only has one project, there is no "row explosion." You get all the data you need for TaskPublicWithProject in exactly one database round-trip.
python
# Perfect for Many-to-One: one row per task, including project details
statement = select(Task).options(joinedload(Task.project))
Use code with caution.

3. Mixing for Nested Schemas
For your complex TaskPublicWithProjectLabels schema, you should combine them for maximum efficiency:
python
from sqlalchemy.orm import joinedload, selectinload

statement = (
    select(Task)
    .options(
        joinedload(Task.project),    # Many-to-One (Single Join)
        selectinload(Task.labels)    # Many-to-Many (Separate IN query)
    )
)
Use code with caution.

Key Differences Recap
Scenario	Recommendation	Implementation
User -> Tasks	selectinload	Collections (1:N) avoid duplicate parent data.
Task -> Project	joinedload	References (N:1) are efficient in a single join.
Task -> Labels	selectinload	Many-to-Many (N:M) handles link tables better.
For a deep dive into performance tuning, check the SQLAlchemy Relationship Loading Techniques documentation or the SQLModel Tutorial on Relationships.
Would you like a code snippet showing how to use contains_eager if you need to filter tasks by a project attribute while loading them?

# Task Managment REST API

A modern, high-performance async REST API built with **FastAPI** and **SQLModel**. This project manages a database of tasks, project, with user auth using oauth, using a robust **Python** stack designed for speed and developer ergonomics.

## 🚀 Features

- **High-Performance API**: Fully asynchronous endpoints leveraging `FastAPI` and `SQLModel`.
- **CRUD Operations**: Complete management for **Tasks**, **Projects**.
- **Relational Data**: Complex relationships handled seamlessly via SQLModel.
- **Auto-Generated Documentation**: Interactive API docs available via **OpenAPI (Swagger UI)**.
- **Modern Tooling**: Managed with `uv` for lightning-fast environment and dependency resolution.
- **Code Quality**: Strict linting and formatting using `Ruff` and type checking using `ty`.
- **Database Migrations**: Version-controlled schema changes with `Alembic`.

## 🛠 Tech Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/)
- **ORM/Models**: [SQLModel](https://sqlmodel.tiangolo.com/) (Async SQLAlchemy + Pydantic)
- **Database**: [SQLite](https://sqlite.org/)
- **Migrations**: [Alembic](https://alembic.sqlalchemy.org/)
- **Package Manager**: [uv](https://docs.astral.sh/uv/)
- **Linter/Formatter**: [Ruff](https://docs.astral.sh/ruff/)
- **Type Checker**: [ty](https://docs.astral.sh/ty/)

- Command Runner (optional extension): [just](https://just.systems/)

## 🏗 Setup

### Prerequisites

This project uses the modern `pyproject.toml` standard for dependency management and requires the `uv` tool to manage the environment.

**Ensure `uv` is installed** globally on your system. If not, follow the official installation guide for [`uv`](https://docs.astral.sh/uv/).

Create a [Neon account](https://console.neon.tech/signup) for serverless Postgres.

### Installation

1.  **Create environment and install dependencies:**

    ```sh
    uv sync
    ```

2.  **Set up Environment Variables:**

    Copy the contents of [`.env.example`](./.env.example) to `.env` file in the root directory.
    
     ```sh
    cp .env.example .env
    ```

3.  **Run Migrations:**

    Initialize your SQLite database to the latest schema:

    ```sh
    uv run alembic upgrade head
    ```

### Running the Application

Start the development server using `uv`:

```sh
uv run uvicorn app.main:app --reload
```

Once started, access the interactive docs at: [http://localhost:8000/docs](http://localhost:8000/docs).

### 💻 Local Development

1. Setup your editor to work with [ruff](https://docs.astral.sh/ruff/editors/setup/) and [ty](https://docs.astral.sh/ty/editors/).

2. Install the [justfile extension](https://just.systems/man/en/editor-support.html) for your editor, and use the provided `./justfile` to run commands.

## Code Quality

- Check for linting errors using `ruff check`: 

  ```sh
  uv run ruff check --fix
  ```

- Format the code using `ruff format`: 

  ```sh
  uv run ruff format
  ```

- Run typechecker using `ty check`: 

  ```sh
  uv run ty check
  ```

## TODO

- [x] user auth
- [x] projects route 
- [x] projects have many tasks
- [x] task belong to one project
- [x] add `due_date` to tasks
- [ ] bulk actions for tasks, DELETE and PATCH
- [x] explore async sqlmodel
- [ ] Tags/Labels, table: Tag, fields:id, name, color_hex, user_id, relationship: Many-to-Many with task.
- [ ] add color hex field to project
