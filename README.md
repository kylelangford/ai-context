# AI Context Index

## Cache Files

| File | Description | Last Updated |
|------|-------------|--------------|
| `cache/basecamp/projects.json` | Active Basecamp projects (36) | 2026-06-19 |
| `cache/trello/boards.json` | Trello board and list IDs | Not yet |
| `cache/trello/active-projects.json` | Boards to include in daily planning | 2026-06-18 |
| `cache/git/repos.json` | Git repos (36 repos across 6 directories) | 2026-06-19 |

### Cache Maintenance

When refreshing caches, exclude archived items:
- **Basecamp**: Run `cache/basecamp/cleanup.sh` after refresh to filter DONE/archived projects
- **Trello**: Only cache boards you actively use

## Documents

| Path | Description |
|------|-------------|
| `docs/company/` | Company guidelines and documentation |

## Prompts

| File | Command | Schedule | Data Sources |
|------|---------|----------|--------------|
| `prompts/templates/standup.md` | `standup` | Weekdays 9am | Trello, Basecamp, Git |
| `prompts/templates/weekly-review.md` | `weekly review` | Friday 9am | Trello, Basecamp, Git |
| `prompts/templates/monday-kickoff.md` | `monday kickoff` | Monday 9am | Trello, Basecamp, Git |
| `prompts/templates/plan-my-day.md` | `plan my day` | On-demand | Trello, Basecamp, Git |

## Email Configuration

All reports are emailed via Resend MCP:

| Setting | Value |
|---------|-------|
| To | `kyle.langford@brunelloinc.com` |
| From | `claude@kylelangford.com` |
| Format | HTML |

## Reports

Output directory: `reports/` (optional local archive)

## Scheduled Tasks (launchd)

| Agent | Script | Schedule | Status |
|-------|--------|----------|--------|
| `com.kylelangford.monday-kickoff` | `schedules/monday-kickoff.sh` | Monday 9am | active |
| `com.kylelangford.weekly-review` | `schedules/weekly-review.sh` | Friday 9am | active |

Plist files: `~/Library/LaunchAgents/com.kylelangford.*.plist`

**Commands:**
```bash
# Check status
launchctl list | grep kylelangford

# Test run
launchctl start com.kylelangford.monday-kickoff

# Disable/Enable
launchctl unload ~/Library/LaunchAgents/com.kylelangford.monday-kickoff.plist
launchctl load ~/Library/LaunchAgents/com.kylelangford.monday-kickoff.plist
```

See `schedules/README.md` for more details.

---

To add new cached data sources, create a JSON file in `cache/<service>/` and update this index.
