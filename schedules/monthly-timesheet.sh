#!/bin/bash
# Monthly Timesheet - runs at 9am on the 1st of each month
# Cron: 0 9 1 * * ~/ai-context/schedules/monthly-timesheet.sh

set -e

# Load nvm for cron environment
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"

cd /Users/kylelangford/ai-context

LOG_FILE="$HOME/ai-context/logs/monthly-timesheet-$(date +%Y%m%d).log"

echo "=== Monthly Timesheet - $(date) ===" >> "$LOG_FILE"

# Read-only tools only (no Edit, Write, or destructive MCP operations)
ALLOWED_TOOLS="Read,Glob,Bash"
ALLOWED_TOOLS+=",mcp__basecamp__list_projects,mcp__basecamp__get_project"
ALLOWED_TOOLS+=",mcp__basecamp__get_time_report"
ALLOWED_TOOLS+=",mcp__basecamp__get_today,mcp__basecamp__get_week_dates"
ALLOWED_TOOLS+=",mcp__resend__send_email"

/usr/local/bin/claude -p "monthly timesheet" \
  --dangerously-skip-permissions \
  --allowedTools "$ALLOWED_TOOLS" \
  2>&1 | tee -a "$LOG_FILE"

echo "=== Completed - $(date) ===" >> "$LOG_FILE"
