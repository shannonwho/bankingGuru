Fix all TypeScript and Python type errors in the FinTechCo project.

## Steps

1. **Run TypeScript type checker**
   ```bash
   cd frontend && npx tsc --noEmit 2>&1
   ```

2. **Read and fix TypeScript errors**
   For each error:
   - Read the file at the reported line
   - Fix the root cause — do not cast with `as any` unless there is no other option
   - Common fixes:
     - Missing optional chaining: `foo?.bar` instead of `foo.bar`
     - Wrong prop types: update the interface in `src/types/index.ts` if the API shape changed
     - Missing return type: add explicit return type annotation
     - Unhandled `null | undefined`: add a guard or non-null assertion with a comment
   - After fixing, re-run `tsc --noEmit` to confirm the error is gone before moving on

3. **Run Python type checker**
   ```bash
   cd backend && python3 -m mypy app --ignore-missing-imports 2>&1
   ```
   If mypy is not installed:
   ```bash
   pip install mypy && python3 -m mypy app --ignore-missing-imports 2>&1
   ```

4. **Fix mypy errors**
   Common patterns in this codebase:
   - `Mapped[str | None]` fields need `nullable=True` in the column definition
   - Route handlers returning `list[SomeModel]` need the correct `response_model=list[SomeOut]`
   - `Optional[X]` parameters in route functions need a default of `None`
   - Do not add `# type: ignore` unless the error is from a third-party library with no stubs

5. **Verify clean**
   Re-run both type checkers and confirm zero errors.

6. **Check types stay in sync**
   If you modified `backend/app/schemas.py`, check that `frontend/src/types/index.ts` reflects the same shape. These two files must stay aligned — the frontend types are manually maintained to mirror the backend Pydantic schemas.

7. **Report**
   List all files changed and the categories of type errors fixed.
