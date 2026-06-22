# Monday Kickoff

## Trigger
Command: `monday kickoff`
Schedule: `0 9 * * 1` (Monday 9am)

## Instructions

When triggered, plan the week ahead:

### 1. Fetch Data
- Read active projects: `~/ai-context/cache/trello/active-projects.json`
- Get Trello cards assigned to me, **filter to only Todo and In Progress lists** from active projects
- **Only include cards modified within the last 30 days** (check `dateLastActivity`)
- **Group cards by project** if more than 5 cards per board (don't list each individually)
- Get my Basecamp todos
- **Get last week's Basecamp time report** (use `get_time_report` with previous week's dates)
- Read last week's review if exists (`~/ai-context/reports/weekly-review-*.md`)
- **Basecamp todos take priority over Trello cards** (Basecamp = client work, Trello = internal tracking)
- Read git repos list: `~/ai-context/cache/git/repos.json`
- Get last week's commits: `git log --since="1 week ago" --author="[user]" --oneline`

### 2. Use Cached Data for Lookups
- Active projects/lists: `~/ai-context/cache/trello/active-projects.json`
- Project names: `~/ai-context/cache/basecamp/projects.json`
- Git repos: `~/ai-context/cache/git/repos.json`

### 3. Analyze & Prioritize
- **Review last week's hours** - total logged, breakdown by project
- **Identify top 3 priorities for the week** based on:
  - Client deadlines and commitments
  - Items due this week
  - Carried over from last week (overdue = high priority)
  - Revenue impact / billable work
  - Blocking other team members
- New items added
- Upcoming deadlines (next 2 weeks)

### 4. Output Format

```
## Monday Kickoff - Week of [DATE]

### This Week's Priorities
1. **[Top Priority]** - [project] - [why it's priority: deadline/client/blocker]
2. **[Second Priority]** - [project] - [reason]
3. **[Third Priority]** - [project] - [reason]

### Carried Over
- [ ] [Task from last week] - originally due [date]

### Upcoming (Next 2 Weeks)
- [Task] - due [date]

### Last Week's Time
Total logged: [X] hours

| Project | Hours |
|---------|-------|
| [name]  | [hrs] |

### Time Budget
Expected hours this week: [estimate based on tasks]

### Last Week's Git Activity
| Repo | Commits |
|------|---------|
| [repo] | [n] |

```

### 5. Email Report
After displaying the kickoff, email it:
- To: `kyle.langford@brunelloinc.com`
- Subject: `Monday Kickoff - Week of [DATE]`
- Format as HTML for better readability
- Use Resend MCP tool (from: claude@kylelangford.com)
