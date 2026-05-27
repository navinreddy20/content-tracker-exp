from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

from app.models.task import AssignedRole, TaskState


# ---------------------------------------------------------------------------
# Shared config
# ---------------------------------------------------------------------------

class _CamelBase(BaseModel):
    """Base that converts snake_case fields to camelCase on the wire.

    - alias_generator=to_camel  → snake_case field → camelCase alias
    - populate_by_name=True     → internal code can still use snake_case names
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
    )


# ---------------------------------------------------------------------------
# Request schemas
# ---------------------------------------------------------------------------

class TaskCreate(_CamelBase):
    """POST /api/tasks request body.

    Frontend sends: title, description, assignedRole, state.
    id and createdAt are NOT sent — the server assigns them.
    """
    title: str = Field(..., min_length=1, description="Non-empty task title")
    description: str = Field(default="")
    assigned_role: AssignedRole
    state: TaskState = Field(default=TaskState.code_ready)


class TaskUpdate(_CamelBase):
    """PUT /api/tasks/{id} request body — all fields optional.

    Three distinct call sites send different subsets:
      - column drop / advance button  → {"state": "..."}
      - edit modal                    → full editable payload

    Service layer uses model_dump(exclude_unset=True) to patch only
    the fields that were actually supplied.
    """
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = None
    assigned_role: Optional[AssignedRole] = None
    state: Optional[TaskState] = None


# ---------------------------------------------------------------------------
# Response schema
# ---------------------------------------------------------------------------

class TaskResponse(_CamelBase):
    """Response body for GET / POST / PUT.

    Populated from a SQLAlchemy Task ORM instance via model_validate(task).
    Serialised with by_alias=True so the wire uses camelCase:
      assigned_role → assignedRole
      created_at   → createdAt

    FastAPI routes must declare response_model_by_alias=True (or use
    router-level default) so FastAPI passes by_alias=True to Pydantic.
    """
    model_config = ConfigDict(
        alias_generator=to_camel,
        populate_by_name=True,
        from_attributes=True,   # lets model_validate() read ORM attributes
    )

    id: int
    title: str
    description: str
    assigned_role: AssignedRole
    state: TaskState
    created_at: date
