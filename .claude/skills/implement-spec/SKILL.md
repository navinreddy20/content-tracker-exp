
---
description: Implement a feature described in a markdown spec file under specs/features/. Reads the spec, builds the feature end-to-end across schemas, service, routes, and runs the smoke tests from the spec. Use when the user provides a spec file path.
argument-hint: <path-to-spec-file>
disable-model-invocation: true
allowed-tools: Read Write Edit Grep Glob Bash(curl:*) Bash(uv run *) Bash(git diff:*)
---
 
You are implementing a feature from a markdown specification.
 
## Input
The spec file path is in $ARGUMENTS.
Example: /implement-spec specs/features/task-filtering.md
 
## Required reading
1. The spec file at $ARGUMENTS — this is your source of truth
2. CLAUDE.md — project conventions
3. backend/app/api/v1/tasks.py — existing endpoint patterns
4. backend/app/services/task_service.py — service patterns
5. backend/app/schemas/task.py — schema patterns
6. specs/api-contract.md — the overall contract
 
## Steps
 
### 1. Restate the spec
Print one line: "Implementing <feature-name>: <one-line behaviour>"
This proves you read the spec, not guessed it.
 
### 2. Extract acceptance criteria
List them. These are your tests.
If the spec has no acceptance criteria section, STOP. Tell the user
the spec needs acceptance criteria before implementation.
 
### 3. Extract out-of-scope items
List them. These are NOT part of this work.
Do not implement them even if they seem like natural additions.
 
### 4. Implement
Touch only the files needed. Match existing patterns in each file.
Pydantic v2. Async SQLAlchemy. snake_case Python. CLAUDE.md conventions.
 
### 5. Run smoke tests from the spec
Execute every curl command in the spec's smoke test section.
Show actual output for each.
Compare against the spec's expectation. PASS or FAIL each.
 
### 6. Report
Output markdown with:
- Spec implemented (path)
- Files modified (one line each)
- Smoke test results (pass/fail per test, with actual output)
- Acceptance criteria items that could NOT be tested via curl — flag for human
 
## Hard rules
- The spec is the source of truth. Do not add behaviour the spec does not describe.
- Do not modify the spec file itself.
- Do not modify frontend/ unless the spec explicitly says so.
- If the spec is ambiguous, STOP and ask the user to clarify and update the spec.
