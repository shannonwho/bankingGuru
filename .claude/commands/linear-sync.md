Sync the current feature branch work to Linear for issue tracking.

This is the comprehensive standalone skill. Linear transitions are also embedded in individual SDLC skills:
- `/lint-fix` → moves issue Backlog → **In Progress** (first touch)
- `/pr` → moves issue In Progress → **In Review** + updates description + creates follow-up issues

Use `/linear-sync` when you want to do all of the above in one shot, or to catch up if individual skills were run without Linear integration.

## SDLC status lifecycle
```
Backlog → In Progress → In Review → Done
  (lint-fix)        (pr created)  (pr merged)
```

## Steps

1. **Identify the Linear issue**
   Extract the issue ID from the current branch name (e.g. `feature/dis-10-...` → DIS-10).
   Use `search_issues` to find it, then `get_issue` for full details including current status and AC.

2. **Determine correct status**
   Based on the current state of the branch:
   - Has uncommitted changes or no PR? → **In Progress**
   - Has an open PR? (`gh pr view --json state` → `OPEN`) → **In Review**
   - PR merged? (`gh pr view --json state` → `MERGED`) → **Done**
   Use `update_issue` with the status name (e.g. `status: "In Progress"`).
   The patched Linear MCP resolves status names to UUIDs automatically.

3. **Gather what was done**
   Run in parallel:
   - `git log main..HEAD --oneline` — all commits on this branch
   - `git diff main...HEAD --stat` — files changed summary
   - `gh pr view --json url,title,state 2>/dev/null` — PR status
   - `gh run list --branch $(git branch --show-current) --limit 3 2>/dev/null` — CI status
   - Run `pytest tests/ -v --tb=line` and `tsc --noEmit` to get latest test/type counts

4. **Update the Linear issue description**
   Use `update_issue` to set the description with:
   - Original **Overview** section (preserved from the issue)
   - **Acceptance Criteria** with checkboxes reflecting what was built vs deferred
   - **Implementation Summary** with subsections:
     - **Backend**: endpoints, models, business rules added/changed
     - **Frontend**: pages, components, types added/changed
     - **Tests**: count of tests passing, what scenarios they cover
     - **CI/CD**: pipeline steps, PR link, branch name, latest CI run status
   - **Notes** for deferred work, tech debt, or follow-up references

5. **Create follow-up issues for deferred AC**
   For each acceptance criterion NOT met:
   - Create a new issue on the same team (`create_issue`) with:
     - Clear title describing the deferred work
     - Description linking back to parent issue with context on why deferred
     - Detailed AC for the follow-up scope
     - Prerequisites or blockers
     - Priority: 2 (High) for core AC, 3 (Medium) for nice-to-have
   - Reference the new issue ID in the parent's deferred AC line

6. **Report**
   - Which issue was updated (ID, title, new status, link)
   - Follow-up issues created (ID, title, link)
   - Any AC items that couldn't be automatically tracked

## Important notes
- Never mark an AC as `[x]` unless the code is committed and tests pass
- Deferred work always gets its own issue — no unchecked boxes without a tracking reference
- The patched Linear MCP at `.claude/patches/linear-mcp-patched.js` adds:
  - `list_states` tool: lists workflow state UUIDs for a team
  - `update_issue` status name resolution: accepts "In Progress" instead of requiring a UUID
  - If the MCP is reset (npx cache cleared), re-apply: `cp .claude/patches/linear-mcp-patched.js ~/.npm/_npx/935194573f4e6558/node_modules/@mseep/linear-mcp/build/index.js`
