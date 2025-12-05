# PDF-to-MD Project Guidelines

## Output Conventions
- Output markdown files directly into `outputs/`, never into subdirectories
- Extracted images go into `outputs/images/`
- Processed PDFs are archived to `archive/pdfs/`

## File Organization
- Root level: Only CLI entry points, README, config files
- `pdf_to_md/`: All library code (import from here, not root)
- `tools/`: Standalone utility scripts
- `scripts/windows/`: Windows automation (.bat, .vbs, .ps1)
- `docs/`: All documentation except README.md and CLAUDE.md

## Code Style
- Python scripts at root are thin CLI wrappers
- Shared logic lives in `pdf_to_md/` package
- Import from package, not from other root files
- Keep functions focused and testable

## Maintenance Behaviors
- Run `/cleanup` before committing to remove cache/build artifacts
- Run `/organize` periodically to check file placement
- Generated files (coverage reports, analysis outputs) go in `docs/reports/`
- Session documentation goes in `docs/archive/`

## What NOT to Create at Root
- New Python modules (put in package or tools/)
- Documentation files (put in docs/)
- Automation scripts (put in scripts/)
- Temporary or generated files

## Expected Root Structure
Only these should be at root:
- `README.md`, `CLAUDE.md`, `MANUAL-REVIEW.md`
- `setup.py`, `requirements.txt`, `pytest.ini`
- CLI entry points: `pdf_converter.py`, `batch_convert.py`, `auto_convert.py`, `docx_converter.py`
