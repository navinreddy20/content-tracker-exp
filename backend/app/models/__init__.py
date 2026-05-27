# Re-export all models so Alembic's env.py picks them up via `import app.models`
from app.models.task import AssignedRole, Task, TaskState, STATES_ORDER
from app.models.user import User, UserRole

__all__ = ["Task", "AssignedRole", "TaskState", "STATES_ORDER", "User", "UserRole"]
