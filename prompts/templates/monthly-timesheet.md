# Monthly Timesheet

## Trigger
Command: `monthly timesheet`
Schedule: `0 9 1 * *` (1st of month, 9am)

## Instructions

When triggered, generate a timesheet summary for the previous month:

### 1. Fetch Data
- Get today's date, calculate previous month's date range (1st to last day)
- Get Basecamp time report for previous month (use `get_time_report` with calculated dates and `user_id: 9186031`)
- Read project names: `~/ai-context/cache/basecamp/projects.json`
- Read client mapping: `~/ai-context/cache/basecamp/client-mapping.json`
- Read aliases: `~/ai-context/cache/aliases.json`

### 2. Analyze Time Entries
- Group entries by date
- Calculate total hours per day
- **Flag any weekday with less than 5.5 hours** (expected: 7 hours, 10am-5pm)
- Skip weekends (Saturday/Sunday) from flagging
- Group entries by project/client
- Calculate total hours for the month
- Count working days in the month (exclude weekends)
- Calculate expected hours (working days × 7)

### 3. Use Cached Data for Lookups
- Project names: `~/ai-context/cache/basecamp/projects.json`
- **Client mapping**: `~/ai-context/cache/basecamp/client-mapping.json` (use for generic "Retainer" projects)
- **Aliases**: `~/ai-context/cache/aliases.json` - **always use the alias (short name) when displaying project names**

### 4. Output Format

```
## Monthly Timesheet - [MONTH YEAR]

### Summary
- Total hours logged: [X] hours
- Working days: [X]
- Expected hours: [X] (working days × 7)
- Difference: [+/-X] hours

### Hours by Project
| Project | Hours | % of Total |
|---------|-------|------------|
| [name]  | [hrs] | [%]        |

### Light Days (< 5.5 hours)
| Date | Day | Hours | Logged |
|------|-----|-------|--------|
| [date] | Mon | 4.0 | [project descriptions] |

### Days with No Time
- [date] - [day of week]

### Daily Breakdown
| Date | Day | Hours | Projects |
|------|-----|-------|----------|
| [date] | Mon | 7.0 | DAM, Enel |
```

### 5. Email Report
After displaying the report, email it:
- To: `kyle.langford@brunelloinc.com`
- Subject: `Monthly Timesheet - [MONTH YEAR]`
- Use HTML template: `~/ai-context/templates/monthly-timesheet.html`
- Use Resend MCP tool (from: claude@kylelangford.com)

## Notes
- This is for internal tracking, not client billing
- Light days may indicate missed entries or PTO
- Help identify patterns (consistently light Fridays, etc.)
