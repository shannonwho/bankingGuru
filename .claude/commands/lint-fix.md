Fix all lint and style errors in the bankingGuru project.

## Steps

0. **Move Linear issue to In Progress**
   Extract the Linear issue ID from the current branch name (e.g. `feature/dis-10-...` → DIS-10).
   Use the Linear MCP tools:
   - `search_issues` to find the issue by identifier
   - `update_issue` with `status: "In Progress"` to move it out of Backlog
   If the issue is already past Backlog (In Progress, In Review, etc.), skip this step.

1. **Run backend linter**
   ```bash
   cd backend && python3 -m ruff check app tests --output-format=concise 2>&1
   ```
   If ruff is not installed:
   ```bash
   pip install ruff && python3 -m ruff check app tests --output-format=concise 2>&1
   ```

2. **Apply ruff auto-fixes**
   ```bash
   cd backend && python3 -m ruff check app tests --fix 2>&1
   ```
   Then re-run step 1. For any remaining errors that ruff cannot auto-fix, read the flagged lines and fix manually.

3. **Run frontend linter**
   ```bash
   cd frontend && npx eslint src --ext .ts,.tsx --max-warnings=0 2>&1
   ```
   If eslint is not configured yet, check for an `.eslintrc` or `eslint.config.*` file first.

4. **Fix frontend lint errors**
   For each error reported:
   - Read the flagged file at the reported line
   - Apply the fix (unused imports, missing deps in hooks, accessibility issues, etc.)
   - Do not suppress errors with `// eslint-disable` unless there is a documented reason

5. **Verify clean**
   Re-run both linters and confirm zero errors before finishing.

6. **Report**
   List all files changed and the categories of issues fixed (e.g. "removed 3 unused imports, fixed 2 missing hook dependencies").

## Common patterns in this codebase
- Unused imports are frequent after refactors — remove them, don't comment them out
- React hook dependency arrays must be complete — add missing deps or restructure with `useCallback`
- `any` types in TypeScript need a real type or a documented `// eslint-disable-next-line` with reason
