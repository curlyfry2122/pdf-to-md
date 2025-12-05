# Project Organization Check

Verify and fix file organization in this project.

## Check Sequence

1. **Audit root directory** - List all files at root and identify any that should be moved:
   - Python scripts that aren't CLI entry points → `tools/` or `pdf_to_md/`
   - Documentation files → `docs/`
   - Windows scripts (.bat, .vbs, .ps1) → `scripts/windows/`
   - Generated/temp files → delete or move to `docs/reports/`

2. **Check for duplicates** - Look for files that exist in both root and `pdf_to_md/` package

3. **Verify imports** - Check that root scripts import from `pdf_to_md` package, not from other root files

4. **Report findings** - List any organizational issues found

5. **Ask before fixing** - Get user confirmation before moving/deleting any files

## Expected Root Structure

Only these should be at root:
- `README.md`, `CLAUDE.md`, `MANUAL-REVIEW.md`
- `setup.py`, `requirements.txt`, `pytest.ini`
- CLI entry points: `pdf_converter.py`, `batch_convert.py`, `auto_convert.py`, `docx_converter.py`

Everything else should be in appropriate subdirectories:
- `pdf_to_md/` - Package library code
- `tools/` - Utility scripts
- `scripts/windows/` - Windows automation
- `docs/` - Documentation and reports
- `tests/` - Test suite
- `inputs/` - Input files
- `outputs/` - Output files
- `archive/` - Archived files

## Instructions

Run these checks in order:
```bash
# List root level files
ls -la | grep -v "^d"

# Check for Python files that shouldn't be at root
ls *.py 2>/dev/null | grep -v -E "^(pdf_converter|batch_convert|auto_convert|docx_converter|setup)\.py$"

# Check for documentation files at root
ls *.md 2>/dev/null | grep -v -E "^(README|CLAUDE|MANUAL-REVIEW)\.md$"

# Check for Windows scripts at root
ls *.bat *.vbs *.ps1 2>/dev/null
```

Report what you find and ask the user before making any changes.
