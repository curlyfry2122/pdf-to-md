"""Utility functions for pdf_to_md package.

Re-exports from core.converter_lib for backwards compatibility.
"""

from pdf_to_md.core.converter_lib import (
    analyze_pdf_for_chunking,
    check_existing_output,
    create_flat_output_structure,
    create_master_index,
    extract_page_images,
    format_file_size,
    open_pdf_document,
    sanitize_filename,
    setup_logging,
    validate_pdf_path,
)

__all__ = [
    'analyze_pdf_for_chunking',
    'check_existing_output',
    'create_flat_output_structure',
    'create_master_index',
    'extract_page_images',
    'format_file_size',
    'open_pdf_document',
    'sanitize_filename',
    'setup_logging',
    'validate_pdf_path',
]
