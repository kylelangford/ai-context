#!/bin/bash
# Plan My Day - runs at 6:30am every weekday
# Cron: 30 6 * * 1-5 ~/ai-context/schedules/plan-my-day.sh

set -e

# Load nvm for cron environment
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

cd /Users/kylelangford/ai-context

LOG_FILE="$HOME/ai-context/logs/plan-my-day-$(date +%Y%m%d).log"

echo "=== Plan My Day - $(date) ===" >> "$LOG_FILE"

# Read-only tools only (no Edit, Write, or destructive MCP operations)
ALLOWED_TOOLS="Read,Glob,Bash"
ALLOWED_TOOLS+=",mcp__trello__get_lists,mcp__trello__get_cards_by_list_id,mcp__trello__get_card"
ALLOWED_TOOLS+=",mcp__trello__get_my_cards,mcp__trello__get_recent_activity,mcp__trello__get_board_labels"
ALLOWED_TOOLS+=",mcp__trello__get_active_board_info,mcp__trello__list_boards"
ALLOWED_TOOLS+=",mcp__basecamp__list_my_todos,mcp__basecamp__list_projects,mcp__basecamp__get_project"
ALLOWED_TOOLS+=",mcp__basecamp__get_project_todos,mcp__basecamp__get_time_report"
ALLOWED_TOOLS+=",mcp__basecamp__get_today,mcp__basecamp__get_week_dates"
ALLOWED_TOOLS+=",mcp__resend__send_email"

/usr/local/bin/claude -p "plan my day" \
  --dangerously-skip-permissions \
  --allowedTools "$ALLOWED_TOOLS" \
  2>&1 | tee -a "$LOG_FILE"

echo "=== Completed - $(date) ===" >> "$LOG_FILE"
