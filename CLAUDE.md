# PDF-to-MD Project Guidelines

## Output Conventions
- Output markdown files directly into `outputs/`, never into subdirectories
- Extracted images go into `outputs/images/`
- Processed PDFs are archived to `archive/pdfs/`

## File Organization
- Root level: Only config files and README — no Python modules
- `pdf_to_md/`: All library code as an installable package
  - `cli/`: CLI entry points (`pdf2md.py`, `docx2md.py`, `interactive.py`)
  - `core/`: Conversion logic (`pdf_converter.py`, `converter_lib.py`, `docx_converter.py`)
  - `batch/`: Batch processing (`batch_processor.py`, `auto_watcher.py`)
  - `alt_text/`: Alt text generation patterns
  - `utils/`: Shared utilities
- `tools/`: Standalone utility scripts and legacy CLI wrappers
- `tests/`: Test suite (pytest)
- `inputs/`: Source PDFs awaiting conversion
- `scripts/windows/`: Windows automation (.bat, .vbs, .ps1)
- `docs/`: Documentation, session archives, and reports
  - `docs/archive/`: Session documentation and project history
  - `docs/reports/`: Generated reports (coverage, analysis)

## CLI Entry Points
The project uses `setup.py` console_scripts (no root-level Python scripts):
- `pdf2md` → `pdf_to_md.cli.pdf2md:main`
- `docx2md` → `pdf_to_md.cli.docx2md:main`
- `batch-convert` → `pdf_to_md.batch.batch_processor:main`
- `auto-convert` → `pdf_to_md.batch.auto_watcher:main`

Install with `pip install -e .` to register these commands.

## Code Style
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

## Integration with Commodity Pipeline

This tool is commonly used as **Stage 2** of the commodity report processing workflow:

```
report-downloads → pdf-to-md → im-report-processing
(Fetch PDFs)      (Convert)    (Extract by commodity)
```

- **Upstream**: `report-downloads` repository fetches source PDFs from USDA, FAO, EIA, etc.
- **Downstream**: `im-report-processing` repository extracts commodity-specific sections

The `## Page N` markers added during conversion enable keyword-based extraction in Stage 3.

See `im-report-processing/docs/PIPELINE_WORKFLOW.md` for complete pipeline documentation.
