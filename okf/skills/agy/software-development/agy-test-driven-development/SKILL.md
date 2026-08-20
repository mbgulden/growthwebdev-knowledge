---
name: agy-test-driven-development
description: Apply Red-Green-Refactor cycles using unit testing frameworks.
version: 1.0.0
---

# AGY Test Driven Development (TDD)

Maintain code quality by writing assertions first, implementing changes, and verifying coverage.

## Trigger Conditions

Use when writing new logic, refactoring subsystems, or fixing bugs that can be isolated via a test.

## Numbered Steps with Exact Commands

1. **Write failing unit test**:
   Create a test script or add a test block to standard test suites. E.g., inside `tests/test_router.py`:
   ```python
   def test_routing_edge_case():
       assert route_task("invalid_label") == "default-model"
   ```

2. **Run tests to verify failure (Red)**:
   ```bash
   pytest tests/test_router.py -k "test_routing_edge_case"
   ```
   Ensure it fails with expected assertion failure.

3. **Implement minimum code to pass (Green)**:
   Modify the implementation file.

4. **Run tests again to verify passing**:
   ```bash
   pytest tests/test_router.py -k "test_routing_edge_case"
   ```
   Confirm the test passes.

5. **Refactor and run full suite**:
   Clean up variables, optimize code structure, and run full test suite to prevent regressions.
   ```bash
   pytest
   ```

## Pitfalls

- **Mocking side effects**: When mocking network/disk calls, ensure mocks replicate actual API responses accurately to avoid false positives.
- **Stale caching**: Run pytest with `--cache-clear` if results feel cached.

## Verification Steps

- Confirm all assertions passed:
  ```bash
  pytest -v | grep "passed"
  ```
