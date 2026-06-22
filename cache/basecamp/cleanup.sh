#!/bin/bash
# Basecamp Cache Cleanup
# Filters projects.json to only include active projects
#
# Usage: ./cleanup.sh
# Run after: update basecamp cache

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
INPUT="$SCRIPT_DIR/projects.json"
OUTPUT="$SCRIPT_DIR/projects.json"
BACKUP="$SCRIPT_DIR/projects-full.json"

if [ ! -f "$INPUT" ]; then
    echo "Error: $INPUT not found"
    exit 1
fi

# Backup full list
cp "$INPUT" "$BACKUP"

# Filter out archived/done projects
# Excludes: DONE:, ARCHIVE:, [ARCHIVED], projects starting with underscore
jq '[.[] | select(
    (.name | test("^DONE:"; "i") | not) and
    (.name | test("^ARCHIVE"; "i") | not) and
    (.name | test("\\[ARCHIVED\\]"; "i") | not) and
    (.name | test("^_") | not)
)]' "$BACKUP" > "$OUTPUT"

BEFORE=$(jq 'length' "$BACKUP")
AFTER=$(jq 'length' "$OUTPUT")
REMOVED=$((BEFORE - AFTER))

echo "Basecamp cache cleanup complete"
echo "  Before: $BEFORE projects"
echo "  After:  $AFTER projects"
echo "  Removed: $REMOVED archived/done projects"
echo "  Backup: $BACKUP"
