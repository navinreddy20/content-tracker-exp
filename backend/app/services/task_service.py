"""Task service — all business logic lives here, never in routes.

Routes call these functions and receive plain SQLAlchemy model objects back.
This module has no knowledge of HTTP status codes, Request, or Response objects.
"""
from datetime import date

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import AssignedRole, Task, TaskState
from app.schemas.task import TaskCreate, TaskUpdate


async def get_all_tasks(
    db: AsyncSession,
    state: TaskState | None = None,
    assigned_role: AssignedRole | None = None,
) -> list[Task]:
    """Return tasks ordered by id, optionally filtered by state and/or role.

    Both filters are AND-ed when supplied together.
    No filters → returns every task (existing behaviour preserved).
    """
    query = select(Task).order_by(Task.id)
    if state is not None:
        query = query.where(Task.state == state)
    if assigned_role is not None:
        query = query.where(Task.assigned_role == assigned_role)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_tasks_by_role(db: AsyncSession, role: AssignedRole) -> list[Task]:
    """Return all tasks assigned to *role*, ordered by id.

    Returns an empty list (not 404) when no tasks match — the role is valid
    but simply has no tasks yet.
    """
    result = await db.execute(
        select(Task).where(Task.assigned_role == role).order_by(Task.id)
    )
    return list(result.scalars().all())


async def get_task(db: AsyncSession, task_id: int) -> Task | None:
    """Return a single task by id, or None if not found."""
    return await db.get(Task, task_id)


async def create_task(db: AsyncSession, data: TaskCreate) -> Task:
    """Insert a new task.

    The server assigns created_at; the caller must not send it.
    Returns the fully-populated Task after commit + refresh.
    """
    task = Task(
        title=data.title,
        description=data.description,
        assigned_role=data.assigned_role,
        state=data.state,
        created_at=date.today(),
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(
    db: AsyncSession,
    task_id: int,
    data: TaskUpdate,
) -> Task | None:
    """Partially update a task.

    Only the fields present in the request body are changed.
    Uses model_dump(exclude_unset=True) so state-only payloads (column drop /
    advance button) don't accidentally null-out title or description.

    Returns the updated Task, or None if task_id doesn't exist.
    """
    task = await db.get(Task, task_id)
    if task is None:
        return None

    patch = data.model_dump(exclude_unset=True)
    for field, value in patch.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)
    return task


async def delete_task(db: AsyncSession, task_id: int) -> bool:
    """Delete a task by id.

    Returns True if the task existed and was deleted, False if not found.
    """
    task = await db.get(Task, task_id)
    if task is None:
        return False

    await db.delete(task)
    await db.commit()
    return True
