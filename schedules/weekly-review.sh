#!/bin/bash
# Weekly Review - runs at 9am every Friday
# Cron: 0 9 * * 5 ~/ai-context/schedules/weekly-review.sh

set -e

cd /Users/kylelangford/ai-context

LOG_FILE="$HOME/ai-context/logs/weekly-review-$(date +%Y%m%d).log"

echo "=== Weekly Review - $(date) ===" >> "$LOG_FILE"

# Read-only tools only (no Edit, Write, or destructive MCP operations)
ALLOWED_TOOLS="Read,Glob,Bash"
ALLOWED_TOOLS+=",mcp__trello__get_lists,mcp__trello__get_cards_by_list_id,mcp__trello__get_card"
ALLOWED_TOOLS+=",mcp__trello__get_my_cards,mcp__trello__get_recent_activity,mcp__trello__get_board_labels"
ALLOWED_TOOLS+=",mcp__trello__get_active_board_info,mcp__trello__list_boards"
ALLOWED_TOOLS+=",mcp__basecamp__list_my_todos,mcp__basecamp__list_projects,mcp__basecamp__get_project"
ALLOWED_TOOLS+=",mcp__basecamp__get_project_todos,mcp__basecamp__get_time_report"
ALLOWED_TOOLS+=",mcp__basecamp__get_today,mcp__basecamp__get_week_dates"
ALLOWED_TOOLS+=",mcp__resend__send_email"

/usr/local/bin/claude -p "weekly review" \
  --dangerously-skip-permissions \
  --allowedTools "$ALLOWED_TOOLS" \
  2>&1 | tee -a "$LOG_FILE"

echo "=== Completed - $(date) ===" >> "$LOG_FILE"
