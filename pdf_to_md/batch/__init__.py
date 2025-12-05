"""
Batch processing modules for automated PDF conversion
"""

from pdf_to_md.batch.auto_watcher import PDFHandler
from pdf_to_md.batch.batch_processor import batch_convert_pdfs

__all__ = [
    "batch_convert_pdfs",
    "PDFHandler",
]
