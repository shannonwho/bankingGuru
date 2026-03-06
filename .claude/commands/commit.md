Create a well-formed git commit for the current changes in the FinTechCo project.

## Steps

1. **Review what's changed**
   Run these in parallel:
   - `git status` — see all modified and untracked files
   - `git diff` — see unstaged changes
   - `git diff --cached` — see staged changes
   - `git log --oneline -5` — understand recent commit style

2. **Identify files to stage**
   Based on the diff, select only files relevant to the current feature or fix. Exclude:
   - `.env` files or anything with secrets
   - `test.db` or other local database files
   - `__pycache__/`, `.pyc`, `node_modules/` (should be in .gitignore already)
   - Any file the user hasn't intentionally modified

3. **Stage the files**
   Use specific file paths — never `git add .` or `git add -A`:
   ```bash
   git add path/to/file1 path/to/file2
   ```

4. **Draft the commit message**
   - First line: imperative mood, ≤72 chars, explains *why* not *what*
     - Good: `Enforce 120-day dispute window to comply with Reg E`
     - Bad: `Updated disputes.py`
   - If scope is clear from the Linear issue, prefix with it: `[DIS-10]`
   - Body (optional): one paragraph explaining motivation if not obvious

5. **Create the commit**
   ```bash
   git commit -m "$(cat <<'EOF'
   Your commit message here

   Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
   EOF
   )"
   ```

6. **Verify**
   Run `git status` and `git log --oneline -3` to confirm the commit was created cleanly.

7. **Report**
   Show the commit hash and message. Remind the user to push when ready with `git push -u origin <branch>`.
