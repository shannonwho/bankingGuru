Generate and run tests for recently changed code in the FinTechCo project.

## Steps

1. **Identify what changed**
   Run `git diff main --name-only` to see which files have been modified on the current branch. Focus on files in `backend/app/` and `frontend/src/`.

2. **Read the changed files**
   Read every modified backend file to understand new functions, endpoints, validators, and business rules.

3. **Determine what to test**
   For each changed backend file, identify:
   - New or modified API endpoints → need integration tests via TestClient
   - New Pydantic validators → need unit tests for valid and invalid inputs
   - New business rules (status machines, window checks, enums) → need boundary tests
   - New models or schema fields → need roundtrip tests

4. **Check existing tests**
   Read `backend/tests/` to understand what's already covered. Do not duplicate existing tests.

5. **Write the tests**
   Add tests to the appropriate test file:
   - General API tests → `backend/tests/test_api.py`
   - Feature-specific tests → `backend/tests/test_<feature>.py` (create if it doesn't exist)

   Follow these rules:
   - Use the fixtures from `conftest.py`: `client`, `db`
   - Test names are full sentences: `test_dispute_window_expired_rejected`
   - Every endpoint needs: happy path, 404/422 error case, any conflict/duplicate case
   - Every state machine needs: all valid transitions, all invalid transitions, terminal state block
   - Every time-based rule needs: N-1 days (accepted), N+1 days (rejected)
   - Every enum/validator needs: all valid values pass, one invalid value fails

6. **Run the tests**
   ```bash
   cd backend && python3 -m pytest tests/ -v --tb=short 2>&1
   ```
   If the test runner isn't available, try:
   ```bash
   cd backend && pip install pytest httpx && python3 -m pytest tests/ -v --tb=short
   ```

7. **Fix failures**
   If tests fail, read the traceback carefully. Fix either the test (if the assertion is wrong) or the implementation (if there's a bug). Re-run until all pass.

8. **Report**
   Summarize: how many tests were added, which scenarios they cover, and the final pass/fail count.
