---
name: testing-engineer
description: Activates specialized knowledge and context for writing, refactoring, and debugging tests using `pytest`.
---
# Testing Engineer

## Context Strategy

When this skill is activated, you DO NOT have the full test suite in your global context (to save tokens).
**You MUST strictly follow this workflow to acquire context:**

1. **Analyze the Target**: Identify which package or module needs testing (e.g., `pkgs/applab-core`).
2. **Load Test Context**:
   * Use `read_file` to inspect `tests/conftest.py` in that package to understand fixtures.
   * Use `glob` to find existing tests: `pkgs/<target>/tests/test_*.py`.
   * Use `read_file` to read relevant existing tests to understand the testing style and patterns.
3. **Load Source Context**: Ensure you have read the source code (`src/`) that needs to be tested.

## Coding Standards

* **Framework**: `pytest`
* **Style**: Use `fixtures` for setup/teardown. Avoid `unittest.TestCase` classes unless necessary.
* **Mocking**: Use `pytest-mock`.
* **Coverage**: Aim for high branch coverage.

## Commands

* Run tests for a package: `uv run pytest pkgs/<package_name>/tests`
