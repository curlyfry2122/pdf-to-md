# PDF to Markdown Converter

**Installable CLI tool** - Convert PDFs and Word documents to Markdown from anywhere with a simple command.

## Installation

Install once, use from anywhere:

```bash
pip install -e C:\Users\jdevine\dev\pdf-to-md
```

## Quick Start

### Interactive Mode (Recommended)
Just run the command - it will prompt you for input:

```bash
pdf2md
```

Output:
```
PDF to Markdown Converter
-------------------------

Available files:
  [1] report.pdf (2.3 MB)
  [2] manual.pdf (15.1 MB)

Enter PDF path or number [1]:
```

### Direct Conversion
Specify the file directly:

```bash
pdf2md path/to/document.pdf
pdf2md "C:\Users\Documents\report.pdf"
```

### Word Documents
```bash
docx2md                         # Interactive mode
docx2md path/to/document.docx   # Direct conversion
```

### Batch & Auto Modes
```bash
batch-convert    # Convert all PDFs in inputs/
auto-convert     # Watch inputs/ and convert automatically
```

## ✨ Key Features

- **🔄 Automatic Processing**: File watcher monitors `inputs/` folder
- **📦 Smart Chunking**: Large PDFs split intelligently (>100 pages or >50MB)
- **🎯 Flat Output**: All markdown files in `outputs/`, images in `outputs/images/`
- **🖼️ Image Extraction**: Embedded images extracted and properly referenced
- **✍️ Detailed Alt Text**: Context-aware, accessible image descriptions (NEW!)
- **📊 Batch Processing**: Convert multiple PDFs at once
- **📋 Summary Reports**: Automatic conversion summaries
- **🔧 Modular Design**: Core library for easy customization

## Project Structure

```
pdf-to-md/
├── pdf_to_md/                # Package (all library code)
│   ├── cli/                  # Command-line interfaces
│   │   ├── pdf2md.py        # pdf2md command
│   │   ├── docx2md.py       # docx2md command
│   │   └── interactive.py   # Shared CLI utilities
│   ├── core/                 # Core conversion logic
│   │   ├── pdf_converter.py
│   │   ├── docx_converter.py
│   │   └── converter_lib.py # Shared utilities
│   ├── batch/                # Batch processing
│   └── alt_text/             # Alt text generation
├── inputs/                   # Drop PDFs here
├── outputs/                  # Markdown files output here
│   └── images/              # Extracted images
├── archive/                  # Processed PDFs archived here
├── tools/                    # Utility scripts
└── setup.py                  # Package configuration
```

## ✍️ Detailed Alt Text Feature

The converter now generates **context-aware, accessible alt text** for all extracted images using a hybrid approach:

### How It Works

1. **Pattern Recognition** (Fast, No API costs)
   - Detects common elements: logos, UI components, headers
   - Analyzes image position, size, and aspect ratio
   - Uses page text for context clues
   - Identifies recurring patterns (e.g., FEWS NET & USAID logos on slides)

2. **AI Vision Fallback** (Optional, for complex images)
   - Can be enabled for detailed analysis of charts, diagrams
   - Currently a placeholder for future AI integration
   - Falls back to smart generic descriptions

### Examples

**Before (generic):**
```markdown
![Image from page 1](images/doc_page_001_img_01.png)
```

**After (detailed):**
```markdown
![FEWS NET logo - Famine Early Warning Systems Network with globe icon showing continents](images/doc_page_001_img_01.png)
![Screenshot of FDW login page with username and password fields, 'Remember Me' checkbox, green 'SIGN IN' button, and 'Forgot Password?' link](images/doc_page_012_img_03.png)
![Screenshot of data table showing Burundi market price data with columns for Data Series ID, Source document, Usage policy, First period date, Last period date, and Data series subtype](images/doc_page_024_img_03.png)
```

### Configuration

**Enabled by default** - All conversions automatically generate detailed alt text.

**Command-line options:**
```bash
pdf2md document.pdf --detail concise   # Shorter descriptions
pdf2md document.pdf --detail verbose   # More detailed
pdf2md document.pdf --no-alt-text      # Disable detailed alt text
```

**Programmatic use:**
```python
from pdf_to_md import convert_pdf_to_markdown

result = convert_pdf_to_markdown("document.pdf")
result = convert_pdf_to_markdown("document.pdf", detail_level="concise")
result = convert_pdf_to_markdown("document.pdf", enable_detailed_alt_text=False)
```

### Benefits

- **Accessibility**: Screen readers get meaningful descriptions
- **SEO**: Better search engine indexing
- **Documentation**: Self-describing images without manual annotation
- **Context Preservation**: Captures what images represent, not just "image"

## Usage Guide

### pdf2md - PDF Converter

```bash
pdf2md                              # Interactive mode
pdf2md document.pdf                 # Convert specific file
pdf2md document.pdf -f              # Overwrite existing output
pdf2md document.pdf --detail verbose # Verbose alt text
pdf2md --help                       # Show all options
```

### docx2md - Word Converter

```bash
docx2md                             # Interactive mode
docx2md document.docx               # Convert specific file
docx2md --help                      # Show all options
```

### batch-convert - Bulk Processing

```bash
batch-convert                       # Convert all PDFs in inputs/
```

Features:
- Processes all PDFs in `inputs/` directory
- Generates summary report (`outputs/batch_summary.md`)
- Shows progress and statistics

### auto-convert - File Watcher

```bash
auto-convert                        # Watch mode (continuous)
auto-convert --scan                 # Scan once and exit
```

Features:
- Detects new PDFs dropped in `inputs/` folder
- Converts immediately and automatically
- Archives processed PDFs to `archive/TIMESTAMP/`

## Installation Details

### Requirements

- Python 3.7+
- PyMuPDF (fitz)
- python-docx
- watchdog (optional, for auto-conversion)

### Install as Package

```bash
# Install in development/editable mode
pip install -e C:\Users\jdevine\dev\pdf-to-md

# Or install from requirements
cd pdf-to-md
pip install -r requirements.txt
pip install -e .
```

## 📊 Output Structure

All outputs use a **flat structure** per CLAUDE.md guidelines:

```
outputs/
├── Document_Name.md              # Single file (if <100 pages)
├── Large_Document_part_01.md     # Chunked files (if >100 pages)
├── Large_Document_part_02.md
├── Large_Document_INDEX.md       # Master index (for chunked docs)
├── batch_summary.md              # Batch conversion report
├── auto_convert.log              # Auto-converter log
└── images/
    ├── Document_Name_page_001_img_01.png
    └── Large_Document_page_015_img_02.png
```

## 🎯 Smart Chunking

PDFs are automatically analyzed and chunked based on size:

| Document Size | Chunk Strategy |
|--------------|----------------|
| ≤100 pages AND ≤50MB | Single file (no chunking) |
| 101-200 pages | 25 pages per chunk |
| >200 pages | 50 pages per chunk |

Large documents include a master INDEX file for easy navigation.

## Architecture

### Package: `pdf_to_md`

**cli/** - Command-line interfaces
- `pdf2md.py` - Interactive PDF converter command
- `docx2md.py` - Interactive Word converter command
- `interactive.py` - Shared CLI utilities (prompts, file listing)

**core/** - Core conversion logic
- `pdf_converter.py` - PDF to Markdown conversion
- `docx_converter.py` - Word to Markdown conversion
- `converter_lib.py` - Shared utilities (chunking, image extraction, etc.)

**batch/** - Batch processing
- `batch_processor.py` - Bulk PDF conversion
- `auto_watcher.py` - File system monitoring

**alt_text/** - Alt text generation
- `patterns.py` - Pattern recognition for images

## Examples

### Interactive Conversion
```bash
pdf2md
# Shows available files, prompts for selection, converts
```

### Direct Conversion
```bash
pdf2md "C:\Users\Documents\report.pdf"
# Result: outputs/report.md
```

### Batch Processing
```bash
# Place PDFs in inputs/
batch-convert
# Check outputs/ for results
```

### Automatic Watching
```bash
auto-convert
# Drop PDFs into inputs/ - they convert automatically
```

## 🐛 Troubleshooting

**Watchdog not available:**
```bash
pip install watchdog
```

**Permission errors:**
- Ensure write access to `outputs/` and `archive/` directories
- Run as administrator if needed (Windows)

**Large PDF fails:**
- Check available disk space
- PDFs >500 pages may need adjustments to chunk size
- Review logs for specific errors

**Images not extracting:**
- Ensure sufficient disk space
- Some PDF formats may have embedded images that can't be extracted
- Check `outputs/auto_convert.log` for warnings

## 📚 Recent Conversions

The system has successfully processed various document types including:
- Economic reports (26-96 pages)
- Market analyses
- Policy documents
- Technical reports

## Contributing

The codebase is modular and extensible:

1. **CLI**: Add new commands in `pdf_to_md/cli/`
2. **Core Logic**: Enhance converters in `pdf_to_md/core/`
3. **Batch Processing**: Customize in `pdf_to_md/batch/`

## License

This project is open source and available for use and modification.

---

**Version:** 3.0 (Installable CLI)
**Last Updated:** November 2025
