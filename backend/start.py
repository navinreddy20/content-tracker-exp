"""
Start the Telusko Workflow Engine.

Usage (from the backend/ directory):
    uv run python start.py

Port is read from settings.port — defaults to 8000.
Override via env var: PORT=9000 uv run python start.py
"""
import uvicorn

from app.core.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=settings.port,
        reload=True,
    )
