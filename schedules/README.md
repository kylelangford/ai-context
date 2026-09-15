# Scheduled Tasks

Store cron job definitions here. Ask Claude to install them to your crontab.

## Cron Syntax

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sunday=0)
│ │ │ │ │
* * * * * command
```

## Common Patterns

| Pattern | Description |
|---------|-------------|
| `0 9 * * *` | Daily at 9am |
| `0 9 * * 1-5` | Weekdays at 9am |
| `*/15 * * * *` | Every 15 minutes |
| `0 0 * * 0` | Weekly on Sunday midnight |
| `0 0 1 * *` | Monthly on the 1st |

## Active Schedules

| Script | Schedule | Description |
|--------|----------|-------------|
| `plan-my-day.sh` | `30 6 * * 1-5` | Weekdays 6:30am - Daily planning |
| `monday-kickoff.sh` | `0 9 * * 1` | Monday 9am - Week planning |
| `weekly-review.sh` | `0 9 * * 5` | Friday 9am - Week summary |

## Guardrails

Scripts are restricted to **read-only operations** to prevent unintended changes:

**Allowed:**
- `Read`, `Glob` - file reading only
- `Bash` - shell commands (for git log)
- `mcp__trello__get_*`, `mcp__trello__list_*` - read Trello data
- `mcp__basecamp__get_*`, `mcp__basecamp__list_*` - read Basecamp data
- `mcp__resend__send_email` - send report emails

**Blocked:**
- `Edit`, `Write` - no file modifications
- `mcp__trello__add_*`, `update_*`, `archive_*`, `move_*`, `delete_*` - no Trello changes
- `mcp__basecamp__create_*`, `update_*`, `delete_*` - no Basecamp changes

This ensures scheduled tasks can only read data and send emails.

## Installation (launchd - recommended)

Launchd plist files are installed at:
- `~/Library/LaunchAgents/com.kylelangford.monday-kickoff.plist`
- `~/Library/LaunchAgents/com.kylelangford.weekly-review.plist`

**Load/unload agents:**

```bash
# Load (enable)
launchctl load ~/Library/LaunchAgents/com.kylelangford.monday-kickoff.plist
launchctl load ~/Library/LaunchAgents/com.kylelangford.weekly-review.plist

# Unload (disable)
launchctl unload ~/Library/LaunchAgents/com.kylelangford.monday-kickoff.plist
launchctl unload ~/Library/LaunchAgents/com.kylelangford.weekly-review.plist

# Check status
launchctl list | grep kylelangford

# Run manually (for testing)
launchctl start com.kylelangford.monday-kickoff
launchctl start com.kylelangford.weekly-review
```

## Alternative: cron

```bash
(crontab -l 2>/dev/null; echo "0 9 * * 1 ~/ai-context/schedules/monday-kickoff.sh"; echo "0 9 * * 5 ~/ai-context/schedules/weekly-review.sh") | crontab -
```

## Logs

Logs are saved to `~/ai-context/logs/`:
- `plan-my-day-YYYYMMDD.log`
- `monday-kickoff-YYYYMMDD.log`
- `weekly-review-YYYYMMDD.log`

## Commands

- `list schedules` - Show all scheduled tasks
- `install schedule <name>` - Add a task to crontab
- `show crontab` - View current crontab
