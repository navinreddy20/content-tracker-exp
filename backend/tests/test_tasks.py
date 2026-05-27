# Tests for /api/tasks endpoints
#
# Covers (to be implemented):
#   test_get_tasks_empty          — GET returns []
#   test_create_task              — POST returns 201 with id + createdAt
#   test_create_task_missing_title — POST with empty title returns 422
#   test_update_task_state_only   — PUT with {"state": "recorded"} patches only state
#   test_update_task_full         — PUT with full payload updates all fields
#   test_delete_task              — DELETE returns 204
#   test_delete_task_not_found    — DELETE unknown id returns 404
