# Basecamp Cache

## Files

| File | Description |
|------|-------------|
| `projects.json` | Active projects only (filtered) |
| `projects-full.json` | Full backup before cleanup |
| `cleanup.sh` | Script to filter archived projects |

## Refresh Process

When running `update basecamp cache`:

1. Fetch projects using `list_projects` MCP tool
2. **Important**: Only save projects where `status != "archived"`
3. Save to `projects.json` with minimal fields: `id`, `name`
4. Run `./cleanup.sh` to remove any DONE:/ARCHIVE: named projects

## Cleanup Script

Filters out projects matching:
- Names starting with `DONE:`
- Names starting with `ARCHIVE`
- Names containing `[ARCHIVED]`
- Names starting with `_` (internal)

```bash
./cleanup.sh
```

## Expected Format

```json
[
  {"id": "123456", "name": "Project Name"},
  {"id": "789012", "name": "Another Project"}
]
```

Keep only `id` and `name` - no other fields needed for lookups.
