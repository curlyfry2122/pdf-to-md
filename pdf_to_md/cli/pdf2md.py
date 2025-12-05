#!/usr/bin/env python3
"""
pdf2md - Interactive PDF to Markdown converter.

Usage:
    pdf2md                  # Interactive mode - prompts for file
    pdf2md <path>           # Convert specified PDF
    pdf2md --help           # Show help
"""

import argparse
import sys
from pathlib import Path

from pdf_to_md.cli.interactive import (
    print_header,
    print_progress,
    print_success,
    prompt_for_file,
)
from pdf_to_md.core.pdf_converter import convert_pdf_to_markdown


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='pdf2md',
        description='Convert PDF documents to Markdown with image extraction.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  pdf2md                    Interactive mode - shows available PDFs
  pdf2md document.pdf       Convert specific file
  pdf2md "path/to/file.pdf" Convert file at path
        """
    )
    parser.add_argument(
        'pdf_path',
        nargs='?',
        help='Path to PDF file (optional - interactive mode if omitted)'
    )
    parser.add_argument(
        '--overwrite', '-f',
        action='store_true',
        help='Overwrite existing output files'
    )
    parser.add_argument(
        '--no-alt-text',
        action='store_true',
        help='Disable detailed alt text generation for images'
    )
    parser.add_argument(
        '--detail',
        choices=['concise', 'standard', 'verbose'],
        default='standard',
        help='Alt text detail level (default: standard)'
    )

    return parser.parse_args()


def main():
    """Main entry point for pdf2md command."""
    args = parse_args()

    print_header("PDF to Markdown Converter")

    # Get PDF path - either from args or interactively
    if args.pdf_path:
        pdf_path = args.pdf_path
        # Resolve path
        path = Path(pdf_path).expanduser()
        if not path.exists():
            print(f"Error: File not found: {pdf_path}")
            sys.exit(1)
        pdf_path = str(path.resolve())
    else:
        # Interactive mode
        pdf_path = prompt_for_file(
            file_type="PDF",
            extensions=['.pdf', '.PDF'],
            default_dir="inputs"
        )
        if not pdf_path:
            sys.exit(1)

    # Show what we're converting
    print(f"\nConverting: {Path(pdf_path).name}")

    # Run conversion
    try:
        result = convert_pdf_to_markdown(
            pdf_path=pdf_path,
            overwrite=args.overwrite,
            enable_detailed_alt_text=not args.no_alt_text,
            detail_level=args.detail
        )
    except Exception as e:
        print(f"\nError during conversion: {e}")
        sys.exit(1)

    # Show results
    print_success(result, file_type="PDF")

    if not result.get('success'):
        sys.exit(1)


if __name__ == '__main__':
    main()
