Create a pull request for the current feature branch in the bankingGuru project.

## Prerequisites
Ensure `gh` CLI is authenticated: `gh auth status`

## Steps

1. **Understand the full diff**
   Run in parallel:
   - `git status` — confirm branch is clean
   - `git log main..HEAD --oneline` — all commits on this branch
   - `git diff main...HEAD --stat` — files changed summary
   - `git diff main...HEAD` — full diff for reading

2. **Read the changed files**
   Read each modified file to understand what was built. Do not rely only on the diff summary.

3. **Look up the Linear issue**
   The branch name contains the Linear issue ID (e.g. `feature/dis-10-...` → DIS-10).
   Use the Linear MCP tool to fetch the issue details if available, so the PR description matches the acceptance criteria.

4. **Check CI status**
   If the branch has been pushed already: `gh run list --branch $(git branch --show-current) --limit 3`

5. **Push the branch if needed**
   ```bash
   git push -u origin $(git branch --show-current)
   ```

6. **Draft the PR**
   - Title: ≤70 chars, imperative mood, references the feature (e.g. `Add dispute submission flow with 120-day window enforcement`)
   - Body follows the template below

7. **Create the PR**
   ```bash
   gh pr create --title "TITLE" --body "$(cat <<'EOF'
   ## Linear issue
   Closes DIS-XX

   ## What changed
   - Bullet points of key changes (backend, frontend, tests)

   ## Why
   One sentence on the business motivation.

   ## Acceptance criteria
   Copy the AC from the Linear issue and check off each one:
   - [x] Criterion met
   - [ ] Criterion not yet met

   ## Test plan
   - [ ] Unit tests pass (`pytest tests/ -v`)
   - [ ] TypeScript compiles (`tsc --noEmit`)
   - [ ] Frontend builds (`npm run build`)
   - [ ] Manually tested happy path
   - [ ] Manually tested error/edge cases

   ## Screenshots
   _Add before/after screenshots for any UI changes._

   🤖 Generated with [Claude Code](https://claude.com/claude-code)
   EOF
   )"
   ```

8. **Move Linear issue to In Review**
   Extract the Linear issue ID from the branch name (e.g. `feature/dis-10-...` → DIS-10).
   Use the Linear MCP tools:
   - `search_issues` to find the issue
   - `update_issue` with `status: "In Review"` to reflect PR is open
   - `update_issue` to update the description with an **Implementation Summary** section including:
     - Backend: endpoints, models, business rules added/changed
     - Frontend: pages, components, types added/changed
     - Tests: count and coverage summary
     - CI/CD: pipeline link, PR link, branch name
   - Check off completed acceptance criteria with `[x]`, mark deferred ones with `[ ]` and a reference to the follow-up issue
   - Create follow-up issues for any deferred AC items using `create_issue`

9. **Return the PR URL** so the user can view and share it.
