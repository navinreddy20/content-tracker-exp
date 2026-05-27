import asyncio
from logging.config import fileConfig

from alembic import context

# ---------------------------------------------------------------------------
# Alembic config — must be the first thing set up so logging works before
# any app code is imported.
# ---------------------------------------------------------------------------
config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ---------------------------------------------------------------------------
# App imports — after logging so handler config is already in place.
# `import app.models` is the side-effect import that registers every model
# class with Base.metadata so autogenerate can diff them.
# ---------------------------------------------------------------------------
from app.core.database import Base, engine  # noqa: E402
import app.models  # noqa: F401, E402

target_metadata = Base.metadata


# ---------------------------------------------------------------------------
# Offline mode — produces a .sql script without touching the database.
# ---------------------------------------------------------------------------
def run_migrations_offline() -> None:
    from app.core.config import settings

    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,   # SQLite does not support ALTER TABLE natively
    )
    with context.begin_transaction():
        context.run_migrations()


# ---------------------------------------------------------------------------
# Online mode — runs against the live async engine.
# ---------------------------------------------------------------------------
def do_run_migrations(connection) -> None:
    """Called synchronously inside connection.run_sync()."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        render_as_batch=True,   # SQLite does not support ALTER TABLE natively
    )
    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Reuse the app engine — single source of truth for DB URL and pool."""
    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await engine.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
