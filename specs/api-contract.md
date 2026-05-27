# API Contract — Telusko Workflow Engine

Derived from `frontend/app.js`. Describes the HTTP contract the frontend
expects when `mockFetch` is replaced with a real `fetch()` wrapper hitting
`http://localhost:8000`.

## Response envelope (critical)

The `api` wrapper does **not** consume a raw `fetch()` `Response` object. It
expects the awaited value to be an envelope of the form:

```js
{ ok: boolean, status: number, data: <payload> }
```

Evidence — every method calls `await mockFetch(...)`, then `if (!res.ok)
throw new Error(\`Server error ${res.status}\`)`, then `return res.data`
(except `deleteTask`, which returns `true`).

The replacement implementation of `mockFetch` must therefore wrap the native
fetch call and resolve with `{ ok, status, data }` where `data` is the parsed
JSON body. This is a frontend wrapper concern — the HTTP wire format below
is plain JSON, no envelope.

## Task object shape

The canonical shape used everywhere in the app (seed data, API responses,
modal form payloads):

| Field          | Type            | Notes                                                                     |
|----------------|-----------------|---------------------------------------------------------------------------|
| `id`           | integer         | Server-assigned. Used as URL path param and as `dataset.id` (parsed back). |
| `title`        | string          | Required. Trimmed before submit; empty title rejected client-side.        |
| `description`  | string          | Trimmed before submit.                                                    |
| `assignedRole` | enum string     | One of `Admin`, `Content`, `Editor`, `Uploader` (matches `ROLE_CONFIG`).   |
| `state`        | enum string     | One of `code_ready`, `recorded`, `editing`, `uploaded`, `published`.       |
| `createdAt`    | string (date)   | ISO date (`YYYY-MM-DD`). Rendered as-is via `escapeHtml`.                  |

Field names are **camelCase on the wire** — the frontend reads
`task.assignedRole` and `task.createdAt` directly in `buildCard` / `openModal`.
If the backend serialises in snake_case, FastAPI must alias on output (e.g.,
Pydantic `Field(alias="assignedRole")` with `model_config = ConfigDict(populate_by_name=True)`).

---

## GET /api/tasks

**Request**: no body, no query params.

**Success (`res.ok === true`)** — `res.data` is an array of task objects:

```json
[
  {
    "id": 1,
    "title": "Introduction to Spring Boot",
    "assignedRole": "Content",
    "state": "code_ready",
    "description": "Cover project setup...",
    "createdAt": "2026-05-01"
  }
]
```

**Error handling**: caught inside `api.getTasks`. Shows toast
`Failed to load tasks: ${err.message}` and returns
`structuredClone(tasks)` (the in-memory seed) for graceful degradation.
Any non-2xx (`res.ok === false`) or rejection is treated as failure.

---

## POST /api/tasks

**Request body** (`handleFormSubmit`, `app.js:425-430`):

```json
{
  "title":        "string",
  "description":  "string",
  "assignedRole": "Admin | Content | Editor | Uploader",
  "state":        "code_ready | recorded | editing | uploaded | published"
}
```

Notes:
- `id` is **not** sent — server assigns it.
- `createdAt` is **not** sent — server must assign it (frontend renders the
  field, so the response must include it).
- `title` is non-empty (validated client-side before submit).

**Success (`res.ok === true`)** — `res.data` is the full created task object
(all 6 fields, including server-assigned `id` and `createdAt`).

**Error handling**: not caught inside `api.createTask`. Propagates to the
caller (`handleFormSubmit`) which shows
`Save failed: ${err.message}`. The modal stays open and `renderBoard()` is
**not** called on failure.

---

## PUT /api/tasks/{id}

`{id}` is the integer task id (interpolated directly via template string).

**Request body** — **partial updates are required**. Three call sites send
different shapes:

1. **Column drop** (`app.js:241`) — state-only:
   ```json
   { "state": "editing" }
   ```
2. **Advance button** (`app.js:346`) — state-only:
   ```json
   { "state": "recorded" }
   ```
3. **Edit modal submit** (`app.js:425-436`) — full editable payload (no `id`,
   no `createdAt`):
   ```json
   {
     "title": "string",
     "description": "string",
     "assignedRole": "Admin | Content | Editor | Uploader",
     "state": "code_ready | recorded | editing | uploaded | published"
   }
   ```

The backend must accept any subset of `{title, description, assignedRole,
state}` and update only the supplied fields. FastAPI: use a Pydantic schema
with all fields `Optional` and `model_dump(exclude_unset=True)` on the service
layer.

**Success (`res.ok === true`)** — `res.data` is returned from the wrapper but
**no caller currently reads it**. All three call sites simply call
`renderBoard()` after success (which re-renders from the in-memory `tasks`
array, not from the response). The response body shape is therefore not
load-bearing today — but to keep the contract symmetrical with POST and to
future-proof code that may `Object.assign(task, res.data)`, return the full
updated task object.

**Error handling**: not caught inside `api.updateTask`. Propagates to three
distinct callers, each with its own toast:
- Column drop → `Could not move task: ${err.message}`
- Advance button → `Could not advance task: ${err.message}`
- Modal submit → `Save failed: ${err.message}`

On error, `renderBoard()` is **not** called. The in-memory task is left
untouched (no local-fallback mutation).

---

## DELETE /api/tasks/{id}

**Request**: no body.

**Success (`res.ok === true`)** — response body is ignored; `api.deleteTask`
returns the literal `true`. Any 2xx (200 with body, 204 No Content, etc.)
is acceptable.

**Error handling**: not caught inside `api.deleteTask`. Propagates to
`deleteTask()` which shows `Could not delete task: ${err.message}`. The card
remains on the board (no local removal on failure).

---

## POST /api/auth/login

**Request body**:

```json
{
  "username": "string   (required, non-empty)",
  "password": "string   (required, non-empty)"
}
```

**Success (`res.ok === true`)** — `res.data` is a JWT token and the authenticated user's role:

```json
{
  "access_token": "string   (JWT)",
  "token_type":   "bearer",
  "role":         "Admin | Content | Editor | Uploader"
}
```

The frontend stores `access_token` in `localStorage` and attaches it as an
`Authorization: Bearer <token>` header on all subsequent requests.

**Error handling**: `401 Unauthorized` — credentials are invalid. The user
remains on the login screen and an error message is shown. No token is stored.

---

## POST /api/auth/users _(Admin only)_

**Request**: requires `Authorization: Bearer <access_token>` header.

**Request body**:

```json
{
  "username": "string   (required, non-empty, must be unique)",
  "password": "string   (required, non-empty)",
  "role":     "Admin | Content | Editor | Uploader"
}
```

**Success (`res.ok === true`)** — `res.data` is the newly created user
(password is never echoed):

```json
{
  "id":       "integer",
  "username": "string",
  "role":     "Admin | Content | Editor | Uploader"
}
```

**Error handling**:
- `401 Unauthorized` — no valid token supplied.
- `403 Forbidden` — authenticated user is not an Admin.
- `409 Conflict` — `username` already exists; response body should include
  `{ "detail": "Username already taken" }`.

---

## GET /api/auth/me

**Request**: requires `Authorization: Bearer <access_token>` header. No body,
no query params.

**Success (`res.ok === true`)** — `res.data` is the profile of the currently
authenticated user:

```json
{
  "id":       "integer",
  "username": "string",
  "role":     "Admin | Content | Editor | Uploader"
}
```

The frontend uses this response to initialise the active role and render the
correct permission set after a page reload, without requiring the user to log
in again.

**Error handling**: `401 Unauthorized` — token is missing, expired, or
invalid. The frontend clears the stored token from `localStorage` and
redirects the user to the login screen.

---

## Error-handling contract summary

| Endpoint            | `ok===false` check         | Caught inside `api.*`? | On error                                                            |
|---------------------|----------------------------|------------------------|---------------------------------------------------------------------|
| `GET /api/tasks`    | `throw Error("Server error ${status}")` | Yes — caught in `api.getTasks` | Toast + fallback to in-memory seed                                  |
| `POST /api/tasks`   | `throw Error("Server error ${status}")` | No — propagates       | `Save failed: …` toast in `handleFormSubmit`                        |
| `PUT /api/tasks/{id}` | `throw Error("Server error ${status}")` | No — propagates     | Caller-specific toast (`Could not move/advance task`, `Save failed`) |
| `DELETE /api/tasks/{id}` | `throw Error("Server error ${status}")` | No — propagates | `Could not delete task: …` toast                                    |
| `POST /api/auth/login` | `throw Error("Server error ${status}")` | No — propagates | Error message shown on login screen; no token stored                |
| `POST /api/auth/users` | `throw Error("Server error ${status}")` | No — propagates | `401` / `403` / `409` surfaced as `Server error ${status}`          |
| `GET /api/auth/me` | `throw Error("Server error ${status}")` | No — propagates     | Token cleared from `localStorage`; redirect to login screen         |

The frontend distinguishes only "ok vs not ok" — no per-status-code branching.
Any non-2xx is surfaced verbatim as `Server error ${status}`. Return standard
REST status codes (`200`, `201`, `204`, `400`, `404`, `422`) for clean error
messages.

---

## Role / permission enforcement

The frontend gates `canCurrentRoleAdvance` and Admin-only delete/drag UX-side,
but per `CLAUDE.md` these are not trust boundaries. The backend must
independently enforce:

- `ROLE_CONFIG.canAdvance` on `PUT /api/tasks/{id}` when `state` is changing
  (only Admin can move freely; other roles may only advance from the listed
  source stages, and only to the next stage per `STATES` order).
- Admin-only on `DELETE /api/tasks/{id}`.

How the backend learns the caller's role is out of scope of the current
`app.js` (no auth header is sent today). The FastAPI scaffold will need to
add a JWT-based identity layer; the contract above describes only the
request/response shapes the frontend already sends and reads.
