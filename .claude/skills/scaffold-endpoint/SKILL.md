
---
description: Scaffold a new FastAPI endpoint end-to-end for the Telusko Workflow Engine. Reads the existing API contract, adds schemas, service method, route handler, and generates a curl smoke test. Use this whenever a new endpoint needs to be added to backend/app/api/v1/.
argument-hint: <verb> <path>
disable-model-invocation: true
allowed-tools: Read Write Edit Grep Glob Bash(curl:*) Bash(uv run *) Bash(git diff:*)
paths: backend/**
---
 
You are scaffolding a new endpoint for the Telusko Workflow Engine.
 
## Input
The user provided: $ARGUMENTS
 
If $ARGUMENTS is empty, stop and ask for:
- HTTP verb (GET / POST / PUT / DELETE)
- Path (for example: /api/tasks/by-role/{role})
 
## Current branch
!`git branch --show-current`
 
## Required reading before scaffolding
1. @specs/api-contract.md — contract style, status codes, error patterns
2. backend/app/api/v1/tasks.py — existing endpoint patterns to match
3. backend/app/services/task_service.py — service layer conventions
4. backend/app/schemas/task.py — existing Pydantic v2 schemas
5. CLAUDE.md — project-wide rules
 
## Steps
 
### 1. Confirm understanding
Print one line:
"Scaffolding $ARGUMENTS — adding [schema/service/route/smoke-test]."
 
### 2. Add Pydantic schema (only if a new shape is needed)
Use Pydantic v2 syntax. model_config not class Config.
 
### 3. Add service method
In backend/app/services/task_service.py. Async SQLAlchemy 2.0 — select(), not query().
Service knows nothing about HTTP.
 
### 4. Add route handler
In backend/app/api/v1/tasks.py. Match the status code conventions:
- GET: 200
- POST: 201
- PUT: 200
- DELETE: 204 (no body)
Use HTTPException with explicit messages.
 
### 5. Generate smoke test
Output a curl command that exercises the new endpoint.
Show the expected response shape based on the schema.
 
### 6. Report
Markdown summary with:
- Files modified (one-line description each)
- The curl command
- TODOs (e.g., "add this endpoint to specs/api-contract.md if it is permanent")
 
## Hard rules
- Do NOT modify frontend/ — backend only
- Do NOT modify specs/ — those are immutable contracts
- Do NOT run alembic — schema changes are a separate skill
- If the request requires a model change, STOP and tell the user this is out of scope
