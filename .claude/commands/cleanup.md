# Project Cleanup

Clean up common Python development artifacts from this project.

## What Gets Removed

This command removes standard regenerable artifacts:
- `__pycache__/` directories (Python bytecode cache)
- `.pytest_cache/` (pytest cache)
- `htmlcov/` (coverage HTML reports)
- `.coverage` (coverage data file)
- `*.egg-info/` directories (package build artifacts)
- `.mypy_cache/` (mypy type checker cache)
- `.ruff_cache/` (ruff linter cache)

## Instructions

1. **DRY RUN first** - Show what would be deleted without actually deleting:
   ```bash
   echo "=== Directories that would be removed ==="
   find . -type d -name "__pycache__" 2>/dev/null
   find . -type d -name ".pytest_cache" 2>/dev/null
   find . -type d -name "htmlcov" 2>/dev/null
   find . -type d -name "*.egg-info" 2>/dev/null
   find . -type d -name ".mypy_cache" 2>/dev/null
   find . -type d -name ".ruff_cache" 2>/dev/null
   echo "=== Files that would be removed ==="
   find . -type f -name ".coverage" 2>/dev/null
   ```

2. **Ask user to confirm** before proceeding with deletion.

3. **If confirmed**, execute cleanup:
   ```bash
   find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
   find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
   find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
   find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
   find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
   find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
   find . -type f -name ".coverage" -delete 2>/dev/null || true
   ```

4. **Report** what was cleaned.

## Safety

- Only removes regenerable artifacts (caches, build outputs)
- Never deletes source code, tests, or documentation
- Always shows preview before deletion
- Project-specific cleanup (archives, legacy code) requires manual review
