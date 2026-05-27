# FastAPI router — /api/tasks
#
# GET    /api/tasks          → list[TaskResponse]          (200)
# POST   /api/tasks          → TaskResponse                (201)
# PUT    /api/tasks/{id}     → TaskResponse                (200)   partial update
# DELETE /api/tasks/{id}     → 204 No Content
#
# No business logic here — all calls delegate to task_service.
# Role enforcement (canAdvance, Admin-only delete) lives in task_service.
