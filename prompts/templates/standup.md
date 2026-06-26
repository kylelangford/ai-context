# Daily Standup

## Trigger
Command: `standup`
Schedule: `0 9 * * 1-5` (Weekdays 9am)

## Instructions

When triggered, gather and summarize:

### 1. Fetch Active Work
- Read active projects: `~/ai-context/cache/trello/active-projects.json`
- Get Trello cards assigned to me, **filter to only Todo and In Progress lists** from active projects
- **Only include cards modified within the last 30 days** (check `dateLastActivity`)
- **Group cards by project** if more than 5 cards per board (don't list each individually)
- Get my Basecamp todos (use `list_my_todos` with `user_id: "9186031"`)
- **Basecamp todos take priority over Trello cards** (Basecamp = client work, Trello = internal tracking)
- Read git repos list: `~/ai-context/cache/git/repos.json`
- Get yesterday's commits: `git log --since="yesterday" --until="today" --author="kyle" --oneline`

### 2. Use Cached Data for Lookups
- Active projects/lists: `~/ai-context/cache/trello/active-projects.json`
- Project names: `~/ai-context/cache/basecamp/projects.json`
- Git repos: `~/ai-context/cache/git/repos.json`

### 3. Output Format

```
## Daily Standup - [DATE]

### Basecamp Todos
- [ ] [Todo name] - [project name]

### In Progress (Trello)
- [ ] [Card name] - [board/project] - due [date]

### Yesterday's Commits
- [repo]: [commit summary]
```

### 4. Email Report
After displaying the standup, email it:
- To: `kyle.langford@brunelloinc.com`
- Subject: `Daily Standup - [DATE]`
- Format as HTML for better readability
- Use Resend MCP tool (from: claude@kylelangford.com)
