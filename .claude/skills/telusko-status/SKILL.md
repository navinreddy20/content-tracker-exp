
---
description: Shows the current state of the Telusko Workflow Engine — git branch, recent commits, contents of specs/, and whether the backend is responding. Use when you need a quick situational awareness before starting work.
---
 
## Current branch
!`git branch --show-current`
 
## Recent commits
!`git log --oneline -5`
 
## Specs in this repo
!`ls -la specs/ 2>/dev/null || echo "no specs/ directory"`
 
## Backend health
!`curl -sf http://localhost:8000/api/tasks > /dev/null && echo "backend up" || echo "backend not responding"`
 
## Instructions
Summarize the above into a single-paragraph status report.
Flag anything unusual — uncommitted work, missing spec files, backend down.
Keep it under 5 lines.
