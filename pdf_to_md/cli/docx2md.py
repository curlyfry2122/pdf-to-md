#!/usr/bin/env python3
"""
docx2md - Interactive Word document to Markdown converter.

Usage:
    docx2md                 # Interactive mode - prompts for file
    docx2md <path>          # Convert specified document
    docx2md --help          # Show help
"""

import argparse
import sys
from pathlib import Path

from pdf_to_md.cli.interactive import (
    print_header,
    print_success,
    prompt_for_file,
)
from pdf_to_md.core.docx_converter import convert_docx_to_markdown


def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        prog='docx2md',
        description='Convert Word documents to Markdown with image extraction.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  docx2md                   Interactive mode - shows available documents
  docx2md document.docx     Convert specific file
  docx2md "path/to/file.docx" Convert file at path
        """
    )
    parser.add_argument(
        'docx_path',
        nargs='?',
        help='Path to Word document (optional - interactive mode if omitted)'
    )
    parser.add_argument(
        '--no-alt-text',
        action='store_true',
        help='Disable detailed alt text generation for images'
    )

    return parser.parse_args()


def main():
    """Main entry point for docx2md command."""
    args = parse_args()

    print_header("Word to Markdown Converter")

    # Get document path - either from args or interactively
    if args.docx_path:
        docx_path = args.docx_path
        # Resolve path
        path = Path(docx_path).expanduser()
        if not path.exists():
            print(f"Error: File not found: {docx_path}")
            sys.exit(1)
        docx_path = str(path.resolve())
    else:
        # Interactive mode
        docx_path = prompt_for_file(
            file_type="Word document",
            extensions=['.docx', '.DOCX', '.doc', '.DOC'],
            default_dir="inputs"
        )
        if not docx_path:
            sys.exit(1)

    # Show what we're converting
    print(f"\nConverting: {Path(docx_path).name}")

    # Run conversion
    try:
        result = convert_docx_to_markdown(
            docx_path=docx_path,
            enable_detailed_alt_text=not args.no_alt_text
        )
    except Exception as e:
        print(f"\nError during conversion: {e}")
        sys.exit(1)

    # Show results
    print_success(result, file_type="document")

    if not result.get('success'):
        sys.exit(1)


if __name__ == '__main__':
    main()
