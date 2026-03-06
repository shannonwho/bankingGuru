Sync the current feature branch work to Linear for issue tracking.

## Steps

1. **Identify the Linear issue**
   Extract the issue ID from the current branch name (e.g. `feature/dis-10-...` → DIS-10).
   Use the Linear MCP tool (`search_issues`) to find the issue, then `get_issue` for full details.

2. **Gather what was done**
   Run in parallel:
   - `git log main..HEAD --oneline` — all commits on this branch
   - `git diff main...HEAD --stat` — files changed summary
   - Check for an open PR: `gh pr view --json url,title,state 2>/dev/null`
   - Check CI status: `gh run list --branch $(git branch --show-current) --limit 3 2>/dev/null`

3. **Update the Linear issue description**
   Use `update_issue` to replace the description with a structured summary:
   - Keep the original **Overview** section
   - Update **Acceptance Criteria** with checkboxes (`[x]` / `[ ]`) reflecting what was built vs deferred
   - Add an **Implementation Summary** section with subsections:
     - **Backend**: endpoints, models, business rules added/changed
     - **Frontend**: pages, components, types added/changed
     - **Tests**: count of tests, what scenarios they cover
     - **CI/CD**: pipeline steps, PR link, branch name
   - Add **Notes** for deferred work, tech debt, or follow-up references

4. **Create follow-up issues for deferred AC**
   For each acceptance criterion that was NOT met:
   - Create a new Linear issue on the same team with:
     - Clear title describing the deferred work
     - Description linking back to the parent issue with context on why it was deferred
     - Detailed AC for the follow-up scope
     - Prerequisites or blockers that caused the deferral
     - Priority: 2 (High) if it's a core AC, 3 (Medium) if nice-to-have
   - Reference the new issue ID (e.g. DIS-15) in the parent issue's deferred AC line

5. **Report**
   Summarize:
   - Which Linear issue was updated and link to it
   - Which follow-up issues were created (ID, title, link)
   - Any AC items that could not be automatically tracked

## Best practices
- Never mark an AC as done (`[x]`) unless the code is committed and tested
- Deferred work always gets its own issue — don't leave unchecked boxes without a tracking reference
- Link PRs in the issue description so reviewers can cross-reference
- Keep implementation summaries factual: counts, file names, endpoint paths — not prose
