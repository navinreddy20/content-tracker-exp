import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.tasks import router as tasks_router
from app.core.config import settings

app = FastAPI(title=settings.app_name, version="0.1.0")

# ---------------------------------------------------------------------------
# CORS
# Allow the frontend regardless of how it is served locally:
#   - python -m http.server 8000 --directory frontend  → same origin, no CORS needed
#     but listed for explicitness
#   - VS Code Live Server (5500)
#   - Any other local port the dev may use
#   - "null" covers file:// origins (Chrome / Firefox when opened directly)
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "null",                     # file:// origin sent by browsers
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],            # includes Authorization
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
app.include_router(auth_router)
app.include_router(tasks_router)


# ---------------------------------------------------------------------------
# Health probe
# ---------------------------------------------------------------------------
@app.get("/health", tags=["meta"])
async def health() -> dict[str, str]:
    return {"status": "ok"}


def start() -> None:
    """Entry point used by `uv run start` — always binds to settings.port (default 8000)."""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=settings.port,
        reload=True,
    )
