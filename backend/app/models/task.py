import enum
from datetime import date

from sqlalchemy import Date, Enum as SAEnum, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


# ---------------------------------------------------------------------------
# Enums — values match seed-data.json and ROLE_CONFIG / STATES in frontend
# ---------------------------------------------------------------------------

class AssignedRole(str, enum.Enum):
    """Roles that can be assigned to a task.

    Names are PascalCase so that name == value, which lets SQLAlchemy store
    the human-readable string ("Admin", "Content", …) without a values_callable.
    """
    Admin = "Admin"
    Content = "Content"
    Editor = "Editor"
    Uploader = "Uploader"


class TaskState(str, enum.Enum):
    """Pipeline stages in order (mirrors STATES array in frontend/app.js).

    Advancement logic in the service layer indexes into this order; do not
    reorder without updating task_service.STATES_ORDER.
    """
    code_ready = "code_ready"
    recorded = "recorded"
    editing = "editing"
    uploaded = "uploaded"
    published = "published"


# Ordered list used by service layer for advancement validation
STATES_ORDER: list[TaskState] = [
    TaskState.code_ready,
    TaskState.recorded,
    TaskState.editing,
    TaskState.uploaded,
    TaskState.published,
]


# ---------------------------------------------------------------------------
# SQLAlchemy 2.0 model
# ---------------------------------------------------------------------------

class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")
    assigned_role: Mapped[AssignedRole] = mapped_column(
        SAEnum(AssignedRole, native_enum=False, length=32),
        nullable=False,
    )
    state: Mapped[TaskState] = mapped_column(
        SAEnum(TaskState, native_enum=False, length=32),
        nullable=False,
        default=TaskState.code_ready,
    )
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    def __repr__(self) -> str:
        return f"<Task id={self.id} title={self.title!r} state={self.state}>"
