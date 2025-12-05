"""
Tests for file handling functions in converter_lib.py
"""

import os
from pathlib import Path

import pytest

from pdf_to_md.core.converter_lib import (open_pdf_document, sanitize_filename,
                                          validate_pdf_path)


class TestSanitizeFilename:
    """Tests for sanitize_filename function"""

    def test_normal_filename(self):
        """Test basic filename without special characters"""
        result = sanitize_filename("normal_file.pdf")
        assert result == "normal_file"

    def test_filename_with_spaces(self):
        """Test filename with spaces converts to underscores"""
        result = sanitize_filename("file with spaces.pdf")
        assert result == "file_with_spaces"

    def test_filename_with_special_chars(self):
        """Test removal of filesystem-unsafe characters"""
        result = sanitize_filename("file<with>special:chars.pdf")
        assert result == "file_with_special_chars"

        result = sanitize_filename("file|with|pipes.pdf")
        assert result == "file_with_pipes"

        result = sanitize_filename("file?with?questions.pdf")
        assert result == "file_with_questions"

    def test_filename_max_length(self):
        """Test filename length limiting"""
        long_name = "a" * 300 + ".pdf"
        result = sanitize_filename(long_name)
        assert len(result) <= 200
        assert result == "a" * 200

    def test_empty_filename(self):
        """Test handling of empty filename"""
        result = sanitize_filename("")
        assert result == ""

    def test_uppercase_extension(self):
        """Test handling of uppercase extension"""
        result = sanitize_filename("FILE.PDF")
        assert result == "FILE"

    def test_path_with_directory(self):
        """Test that only basename is used"""
        result = sanitize_filename("/path/to/file.pdf")
        assert result == "file"

        result = sanitize_filename("C:\\path\\to\\file.pdf")
        assert result == "file"

    def test_multiple_spaces(self):
        """Test multiple consecutive spaces"""
        result = sanitize_filename("file    with    spaces.pdf")
        assert result == "file_with_spaces"

    def test_leading_trailing_underscores(self):
        """Test stripping of leading/trailing underscores"""
        result = sanitize_filename("_file_.pdf")
        assert result == "file"


class TestValidatePdfPath:
    """Tests for validate_pdf_path function"""

    def test_valid_pdf_path(self, small_pdf):
        """Test with a valid PDF path"""
        result = validate_pdf_path(str(small_pdf))
        assert os.path.isabs(result)
        assert result.endswith('.pdf')
        assert os.path.exists(result)

    def test_nonexistent_path(self):
        """Test with non-existent file"""
        with pytest.raises(FileNotFoundError, match="PDF file not found"):
            validate_pdf_path("nonexistent.pdf")

    def test_not_a_pdf(self, temp_dir):
        """Test with non-PDF file"""
        txt_file = temp_dir / "test.txt"
        txt_file.write_text("not a pdf")

        with pytest.raises(ValueError, match="File is not a PDF"):
            validate_pdf_path(str(txt_file))

    def test_invalid_path_none(self):
        """Test with None as path"""
        with pytest.raises(ValueError, match="Invalid PDF path"):
            validate_pdf_path(None)

    def test_invalid_path_empty(self):
        """Test with empty string"""
        with pytest.raises(ValueError, match="Invalid PDF path"):
            validate_pdf_path("")

    def test_invalid_path_type(self):
        """Test with invalid type"""
        with pytest.raises(ValueError, match="Invalid PDF path"):
            validate_pdf_path(123)

    def test_directory_path(self, temp_dir):
        """Test with directory instead of file"""
        pdf_dir = temp_dir / "test.pdf"
        pdf_dir.mkdir()

        with pytest.raises(ValueError, match="Path is not a file"):
            validate_pdf_path(str(pdf_dir))

    def test_relative_path_converted_to_absolute(self, small_pdf):
        """Test that relative paths are converted to absolute"""
        # Get a relative path by using basename
        pdf_name = os.path.basename(small_pdf)
        pdf_dir = os.path.dirname(small_pdf)

        # Change to the directory and use relative path
        original_dir = os.getcwd()
        try:
            os.chdir(pdf_dir)
            result = validate_pdf_path(pdf_name)
            assert os.path.isabs(result)
        finally:
            os.chdir(original_dir)


class TestOpenPdfDocument:
    """Tests for open_pdf_document context manager"""

    def test_successful_open(self, small_pdf):
        """Test successfully opening a PDF"""
        with open_pdf_document(str(small_pdf)) as doc:
            assert doc is not None
            assert hasattr(doc, 'page_count')
            assert doc.page_count > 0

    def test_document_closed_after_context(self, small_pdf):
        """Test that document is closed after context exits"""
        doc_ref = None
        with open_pdf_document(str(small_pdf)) as doc:
            doc_ref = doc
            assert not doc.is_closed

        # Document should be closed after context
        assert doc_ref.is_closed

    def test_nonexistent_file(self):
        """Test opening non-existent file"""
        with pytest.raises(Exception):  # fitz raises various exceptions
            with open_pdf_document("nonexistent.pdf") as doc:
                pass

    def test_corrupted_pdf(self, temp_dir):
        """Test opening corrupted PDF file"""
        corrupt_pdf = temp_dir / "corrupt.pdf"
        corrupt_pdf.write_bytes(b"This is not a valid PDF")

        with pytest.raises(Exception):  # fitz raises various exceptions for corrupt files
            with open_pdf_document(str(corrupt_pdf)) as doc:
                pass

    def test_exception_in_context(self, small_pdf):
        """Test that document is closed even if exception occurs in context"""
        doc_ref = None
        try:
            with open_pdf_document(str(small_pdf)) as doc:
                doc_ref = doc
                raise ValueError("Test exception")
        except ValueError:
            pass

        # Document should still be closed
        assert doc_ref.is_closed

    def test_access_document_properties(self, small_pdf):
        """Test accessing various document properties"""
        with open_pdf_document(str(small_pdf)) as doc:
            # Should be able to access basic properties
            assert isinstance(doc.page_count, int)
            assert hasattr(doc, 'metadata')
            assert hasattr(doc, 'name')

            # Should be able to load pages
            if doc.page_count > 0:
                page = doc.load_page(0)
                assert page is not None
