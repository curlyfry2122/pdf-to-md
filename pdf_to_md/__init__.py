"""
pdf-to-md: PDF and DOCX to Markdown converter
"""

__version__ = "0.1.0"

from pdf_to_md.core.docx_converter import convert_docx_to_markdown
# Export main conversion functions for easy access
from pdf_to_md.core.pdf_converter import convert_pdf_to_markdown

__all__ = [
    "convert_pdf_to_markdown",
    "convert_docx_to_markdown",
]
