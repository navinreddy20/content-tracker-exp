"""Seed the tasks and users tables.

Idempotent: records whose id / username already exists in the database are
skipped, so running this script multiple times never creates duplicates.

Usage:
    uv run python seed.py
"""
import asyncio
import json
from datetime import date
from pathlib import Path

from sqlalchemy import func, select

from app.core.database import AsyncSessionLocal
from app.models.task import AssignedRole, Task, TaskState
from app.models.user import User, UserRole
from app.security.password import hash_password
import app.models  # noqa: F401 — registers all models with Base.metadata

SEED_FILE = Path(__file__).parent.parent / "specs" / "seed-data.json"

# ---------------------------------------------------------------------------
# Demo users — DEMO CREDENTIALS ONLY; use strong passwords in production
# ---------------------------------------------------------------------------
SEED_USERS: list[dict] = [
    {"username": "admin",    "password": "admin123",    "role": UserRole.admin},
    {"username": "content",  "password": "content123",  "role": UserRole.content_team},
    {"username": "editor",   "password": "editor123",   "role": UserRole.video_editor},
    {"username": "uploader", "password": "uploader123", "role": UserRole.uploader},
    {"username": "demo",     "password": "demo123",     "role": UserRole.video_editor},
]


async def seed_tasks(db) -> None:
    records = json.loads(SEED_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(records)} task records from {SEED_FILE.name}")

    inserted = skipped = 0
    for rec in records:
        existing = await db.get(Task, rec["id"])
        if existing is not None:
            print(f"  SKIP   task id={rec['id']:>2}  {rec['title']!r}")
            skipped += 1
            continue

        task = Task(
            id=rec["id"],
            title=rec["title"],
            description=rec["description"],
            assigned_role=AssignedRole(rec["assigned_role"]),
            state=TaskState(rec["state"]),
            created_at=date.fromisoformat(rec["created_at"]),
        )
        db.add(task)
        print(f"  INSERT task id={rec['id']:>2}  {rec['title']!r}")
        inserted += 1

    await db.commit()

    result = await db.execute(select(func.count()).select_from(Task))
    total = result.scalar_one()
    print(f"  Tasks: {inserted} inserted, {skipped} skipped — {total} total\n")


async def seed_users(db) -> None:
    print(f"Seeding {len(SEED_USERS)} users …")

    inserted = skipped = 0
    for u in SEED_USERS:
        result = await db.execute(select(User).where(User.username == u["username"]))
        if result.scalar_one_or_none() is not None:
            print(f"  SKIP   user {u['username']!r}")
            skipped += 1
            continue

        user = User(
            username=u["username"],
            password_hash=hash_password(u["password"]),
            role=u["role"],
        )
        db.add(user)
        print(f"  INSERT user {u['username']!r}  role={u['role'].value}")
        inserted += 1

    await db.commit()

    result = await db.execute(select(func.count()).select_from(User))
    total = result.scalar_one()
    print(f"  Users: {inserted} inserted, {skipped} skipped — {total} total\n")


async def seed() -> None:
    async with AsyncSessionLocal() as db:
        await seed_tasks(db)
        await seed_users(db)


if __name__ == "__main__":
    asyncio.run(seed())
