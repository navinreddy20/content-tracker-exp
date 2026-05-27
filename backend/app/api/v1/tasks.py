"""FastAPI router for /api/tasks.

Routes are thin: validate input, call the service, map None → 404, return.
No SQLAlchemy imports here. No business logic here.

All endpoints require a valid Bearer token (get_current_user).
POST and DELETE additionally restrict by role (require_role).
PUT enforces RBAC advance rules when the request body changes `state`.
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.task import AssignedRole, Task, TaskState
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.security.dependencies import get_current_user, require_role
from app.services import task_service

router = APIRouter(prefix="/api/tasks", tags=["tasks"])

# Convenience type alias so every endpoint stays one-liner on the db param.
DbDep = Annotated[AsyncSession, Depends(get_db)]

# ---------------------------------------------------------------------------
# RBAC advance rules — mirrors ROLE_CONFIG / canAdvance from frontend app.js
# Keys are UserRole values; values are the TaskState keys a role may advance FROM.
# ---------------------------------------------------------------------------
_ADVANCE_ALLOWED: dict[str, list[str]] = {
    "admin":        ["code_ready", "recorded", "editing", "uploaded"],
    "content_team": ["code_ready"],
    "video_editor": ["recorded", "editing"],
    "uploader":     ["uploaded"],
}


# ---------------------------------------------------------------------------
# GET /api/tasks
# ---------------------------------------------------------------------------

@router.get(
    "",
    response_model=list[TaskResponse],
    response_model_by_alias=True,   # assigned_role → assignedRole, created_at → createdAt
    summary="List all tasks",
)
async def list_tasks(
    db: DbDep,
    state: str | None = None,
    assigned_role: str | None = None,
    _current_user: User = Depends(get_current_user),
) -> list[Task]:
    """Return tasks, optionally filtered by state and/or assigned_role.

    Requires: any authenticated role.
    """
    validated_state: TaskState | None = None
    validated_role: AssignedRole | None = None

    if state is not None:
        try:
            validated_state = TaskState(state)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"invalid state: {state}",
            )

    if assigned_role is not None:
        try:
            validated_role = AssignedRole(assigned_role)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"invalid role: {assigned_role}",
            )

    return await task_service.get_all_tasks(db, validated_state, validated_role)


# ---------------------------------------------------------------------------
# GET /api/tasks/by-role/{role}
# ---------------------------------------------------------------------------

@router.get(
    "/by-role/{role}",
    response_model=list[TaskResponse],
    response_model_by_alias=True,
    summary="List tasks by assigned role",
)
async def list_tasks_by_role(
    role: AssignedRole,
    db: DbDep,
    _current_user: User = Depends(get_current_user),
) -> list[Task]:
    """Return all tasks assigned to a given role.

    Requires: any authenticated role.
    """
    return await task_service.get_tasks_by_role(db, role)


# ---------------------------------------------------------------------------
# POST /api/tasks
# ---------------------------------------------------------------------------

@router.post(
    "",
    response_model=TaskResponse,
    response_model_by_alias=True,
    status_code=status.HTTP_201_CREATED,
    summary="Create a task",
)
async def create_task(
    data: TaskCreate,
    db: DbDep,
    _current_user: User = Depends(require_role("admin", "content_team")),
) -> Task:
    """Requires: admin or content_team role."""
    return await task_service.create_task(db, data)


# ---------------------------------------------------------------------------
# PUT /api/tasks/{task_id}
# ---------------------------------------------------------------------------

@router.put(
    "/{task_id}",
    response_model=TaskResponse,
    response_model_by_alias=True,
    summary="Update a task (partial)",
)
async def update_task(
    task_id: int,
    data: TaskUpdate,
    db: DbDep,
    current_user: User = Depends(get_current_user),
) -> Task:
    """Partial update.  Any authenticated user may change non-state fields.

    When *state* is included in the request body, the RBAC advance rule is
    enforced: only roles whose canAdvance list includes the task's *current*
    state are permitted.  Violation → 403.
    """
    if data.state is not None:
        # Fetch task first to check current state
        existing = await task_service.get_task(db, task_id)
        if existing is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Task {task_id} not found",
            )
        allowed_from = _ADVANCE_ALLOWED.get(current_user.role.value, [])
        if existing.state.value not in allowed_from:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=(
                    f"role {current_user.role.value} cannot advance from "
                    f"state {existing.state.value}"
                ),
            )

    task = await task_service.update_task(db, task_id, data)
    if task is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
    return task


# ---------------------------------------------------------------------------
# DELETE /api/tasks/{task_id}
# ---------------------------------------------------------------------------

@router.delete(
    "/{task_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a task",
)
async def delete_task(
    task_id: int,
    db: DbDep,
    _current_user: User = Depends(require_role("admin")),
) -> None:
    """Requires: admin role."""
    deleted = await task_service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task {task_id} not found",
        )
