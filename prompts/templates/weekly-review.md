# Weekly Review

## Trigger
Command: `weekly review`
Schedule: `0 9 * * 5` (Friday 9am)

## Instructions

When triggered, analyze the past week:

### 1. Fetch Data
- Read active projects: `~/ai-context/cache/trello/active-projects.json`
- Get Trello recent activity, **filter to only active project boards**
- **Only include cards modified within the last 30 days** (check `dateLastActivity`)
- **Group cards by project** if more than 5 cards per board (don't list each individually)
- Get Basecamp time report for this week (use `get_time_report` with `get_week_dates`)
- Check completed vs remaining tasks
- **Basecamp todos take priority over Trello cards** (Basecamp = client work, Trello = internal tracking)
- Read git repos list: `~/ai-context/cache/git/repos.json`
- For each repo, get commits from this week: `git log --since="[week_start]" --until="[week_end]" --author="[user]" --oneline`

### 2. Use Cached Data for Lookups
- Active projects/lists: `~/ai-context/cache/trello/active-projects.json`
- Project names: `~/ai-context/cache/basecamp/projects.json`
- Git repos: `~/ai-context/cache/git/repos.json`

### 3. Analyze
- Cards moved to Done this week
- Total hours logged
- Hours per project breakdown
- Incomplete items that were due this week
- Patterns (most productive day, common blockers)
- Git commits grouped by repo (count and key changes)

### 4. Output Format

```
## Weekly Review - Week of [DATE]

### Completed
- [x] [Task name] - [project]
- [x] [Task name] - [project]

### Time Logged
Total: [X] hours

| Project | Hours |
|---------|-------|
| [name]  | [hrs] |

### Git Activity
| Repo | Commits | Summary |
|------|---------|---------|
| [repo-name] | [n] | [brief description of changes] |

### Incomplete / Carried Over
- [ ] [Task] - due [date] - [reason if known]

### Blockers Encountered
- [Any blockers or issues]

### Notes for Next Week
- [Observations, patterns, adjustments]
```

### 5. Email Report
After displaying the review, email it:
- To: `kyle.langford@brunelloinc.com`
- Subject: `Weekly Review - Week of [DATE]`
- Format as HTML for better readability
- Use Resend MCP tool (from: claude@kylelangford.com)
