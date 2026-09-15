# Plan My Day

## Trigger
Command: `plan my day`
Schedule: N/A (on-demand)

## Instructions

When triggered, create a prioritized daily plan:

### 1. Fetch Data
- Read active projects list: `~/ai-context/cache/trello/active-projects.json`
- Get Trello cards assigned to me, then **filter to only Todo and In Progress lists** from active projects
- **Only include cards modified within the last 30 days** (check `dateLastActivity`)
- **Group cards by project** if more than 5 cards per board (don't list each individually)
- Get my Basecamp todos (use `list_my_todos` with `user_id: "9186031"`)
- Check today's date and day of week
- Read git repos list: `~/ai-context/cache/git/repos.json`
- Check for uncommitted work: `git status --short` on each repo

### 2. Use Cached Data for Lookups
- Board names: `~/ai-context/cache/trello/boards.json`
- Project names: `~/ai-context/cache/basecamp/projects.json`
- **Client mapping**: `~/ai-context/cache/basecamp/client-mapping.json` (use this to get client names for generic "Retainer" projects)
- Git repos: `~/ai-context/cache/git/repos.json`

### 3. Prioritize Using
- **Basecamp todos take priority over Trello cards** (Basecamp = client work, Trello = internal tracking)
- Due date (overdue > today > this week > later)
- Labels/tags if present (urgent, high priority)
- Dependencies (unblock others first)
- Quick wins (< 30 min tasks to build momentum)

### 4. Output Format

Write 2-3 natural sentences covering:
- What you're focused on (projects/tasks)
- What you expect to accomplish today
- Timing if relevant (when something should be ready)
- Blockers if any exist

Example:
```
Today I'm focused on the Enel updates and Drupal upgrade prep. I expect to get the Enel changes into QA and make progress on the upgrade checklist. No blockers right now.
```

### 5. Ask User
After generating plan, ask:
- "Does this order work? Any meetings or constraints I should know about?"
- Adjust based on feedback

### 6. Email Report
After user confirms the plan, email it:
- To: `kyle.langford@brunelloinc.com`
- Subject: `Daily Plan - [DATE]`
- Format as HTML for better readability
- Use Resend MCP tool (from: claude@kylelangford.com)

## Notes
- Keep to 3 main focuses (realistic)
- Prioritize client work (Basecamp) over internal (Trello)
