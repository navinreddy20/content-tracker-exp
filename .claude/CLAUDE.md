# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Telusko Workflow Engine — a static, frontend-only Kanban board for tracking video production. Everything lives in `frontend/` (`index.html`, `app.js`, `styles.css`). There is no build step, no package manager, no test suite, and no backend yet.

## Running locally

Open `frontend/index.html` directly in a browser, or serve the folder with any static server (e.g. `python -m http.server 8000 --directory frontend`). Changes are picked up on reload — no bundler.

## Architecture

The app is a single-file vanilla-JS SPA (`frontend/app.js`) with three load-bearing globals that everything else flows from:

## Tech Stack
- FastAPI 0.115+
- SQLAlchemy 2.0 with async
- Pydantic v2 for schemas
- Alembic for migrations
- python-jose for JWT


- **`STATES`** — ordered pipeline (`code_ready` → `recorded` → `editing` → `uploaded` → `published`). Order defines advancement; `getNextStateKey` indexes into it. Adding or reordering stages must keep this array in sync with the `<select id="task-state">` options in `index.html`.
- **`ROLE_CONFIG`** — per-role `canAdvance` whitelists which stages each role is allowed to push a card forward from. Drag-and-drop is intentionally Admin-only; non-admins use the "Move Forward" button, gated by `canCurrentRoleAdvance`.
- **`tasks`** — in-memory array seeded with sample data; mutated only via `renderBoard()` re-renders after API calls resolve.

### Mock API layer

`api.{getTasks,createTask,updateTask,deleteTask}` in `app.js` wraps a `mockFetch` that **always rejects** after a simulated delay. This is deliberate — the UI is wired through `await api.*` calls so that swapping `mockFetch` for real `fetch()` against the planned FastAPI backend (`localhost:8000`, per the error message) is a one-function change. Don't bypass the `api` wrapper by mutating `tasks` directly; the awaited round-trip pattern is what lets the real backend slot in.

`api.getTasks()` is the only call that swallows errors (falls back to local `tasks`) for graceful degradation; the others surface failures through `showToast(..., 'error')`.

### Rendering

`renderBoard()` is the single re-render entry point — every state change calls it after the awaited API response. Cards and columns are rebuilt from scratch each time (no diffing). Drag-and-drop state lives in the module-level `draggedTaskId`, reset in `dragend` and after every drop.

### Roles & permissions (enforced in JS, not trust boundaries)

- Admin: free drag-and-drop across all columns, can delete, can edit any field including stage in the modal.
- Content / Editor / Uploader: can only advance from stages listed in their `ROLE_CONFIG.canAdvance`; stage `<select>` in the modal is disabled for non-Admins.

These checks are UX-only — when a real backend lands, it must re-enforce them server-side.

### UV package manager

'Use uv as the package manager. All Python commands run
through uv — uv pip install for packages, uv run pytest for tests,
uv run python for scripts. Never use pip or python directly.


## Code Style
- Python: snake_case for functions and variables
- Always use type hints
- Never put business logic in routes - use service layer
- Schemas in schemas/ folder, models in models/ folder


## Rules
- NEVER modify files in /frontend
- NEVER commit .env files
- Always create migration when changing models


