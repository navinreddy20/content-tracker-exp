# pytest fixtures for async FastAPI tests
#
# Planned fixtures:
#   engine    — in-memory aiosqlite engine (create_all / drop_all per session)
#   db        — AsyncSession scoped per test
#   client    — httpx.AsyncClient pointed at the FastAPI app with overridden db dep
