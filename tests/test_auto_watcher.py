"""
Tests for auto watcher functions in auto_watcher.py
"""

import os
import shutil
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from pdf_to_md.batch.auto_watcher import PDFHandler, scan_and_convert_existing


class TestPDFHandler:
    """Tests for PDFHandler class"""

    def test_initialization(self, temp_dir):
        """Test PDFHandler initialization"""
        archive_dir = temp_dir / "archive"

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            handler = PDFHandler(archive_dir=str(archive_dir))

        assert handler.archive_dir == str(archive_dir)
        assert archive_dir.exists()
        assert isinstance(handler.processing, set)

    def test_creates_archive_directory(self, temp_dir):
        """Test that archive directory is created"""
        archive_dir = temp_dir / "archive"

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            handler = PDFHandler(archive_dir=str(archive_dir))

        assert archive_dir.exists()
        # Should also create session subdirectory
        session_dirs = list(archive_dir.glob("*"))
        assert len(session_dirs) > 0

    def test_process_pdf_success(self, temp_dir):
        """Test successful PDF processing"""
        archive_dir = temp_dir / "archive"
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"PDF content")

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            with patch('pdf_to_md.batch.auto_watcher.convert_pdf_to_markdown') as mock_convert:
                mock_convert.return_value = {
                    'success': True,
                    'files_created': ['test.md'],
                    'images_extracted': 5
                }

                handler = PDFHandler(archive_dir=str(archive_dir))
                handler.process_pdf(str(pdf_file))

                mock_convert.assert_called_once_with(str(pdf_file))

    def test_process_pdf_failure(self, temp_dir):
        """Test PDF processing failure"""
        archive_dir = temp_dir / "archive"
        pdf_file = temp_dir / "bad.pdf"
        pdf_file.write_bytes(b"PDF content")

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            with patch('pdf_to_md.batch.auto_watcher.convert_pdf_to_markdown') as mock_convert:
                mock_convert.return_value = {
                    'success': False,
                    'error': 'Conversion failed'
                }

                handler = PDFHandler(archive_dir=str(archive_dir))
                handler.process_pdf(str(pdf_file))

                # Should not crash, just log error
                assert True  # If we get here, error was handled

    def test_process_pdf_nonexistent_file(self, temp_dir):
        """Test processing non-existent PDF"""
        archive_dir = temp_dir / "archive"

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            handler = PDFHandler(archive_dir=str(archive_dir))
            # Should handle gracefully
            handler.process_pdf("nonexistent.pdf")

            # Should not raise exception
            assert True

    def test_archive_pdf(self, temp_dir):
        """Test archiving PDF after processing"""
        archive_dir = temp_dir / "archive"
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"PDF content")

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            handler = PDFHandler(archive_dir=str(archive_dir))
            handler.archive_pdf(str(pdf_file))

        # PDF should be moved to archive
        assert not pdf_file.exists()
        # Should be in session archive
        archived_files = list(Path(handler.session_archive).glob("*.pdf"))
        assert len(archived_files) == 1

    def test_archive_duplicate_filename(self, temp_dir):
        """Test archiving with duplicate filename"""
        archive_dir = temp_dir / "archive"

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            handler = PDFHandler(archive_dir=str(archive_dir))

            # Create and archive first file
            pdf1 = temp_dir / "test.pdf"
            pdf1.write_bytes(b"PDF 1")
            handler.archive_pdf(str(pdf1))

            # Create and archive second file with same name
            pdf2 = temp_dir / "test.pdf"
            pdf2.write_bytes(b"PDF 2")
            handler.archive_pdf(str(pdf2))

        # Should have two archived files (with different names)
        archived_files = list(Path(handler.session_archive).glob("*.pdf"))
        assert len(archived_files) == 2

    def test_prevents_duplicate_processing(self, temp_dir):
        """Test that same file isn't processed multiple times"""
        archive_dir = temp_dir / "archive"
        pdf_file = temp_dir / "test.pdf"
        pdf_file.write_bytes(b"PDF content")

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            with patch('pdf_to_md.batch.auto_watcher.convert_pdf_to_markdown') as mock_convert:
                mock_convert.return_value = {
                    'success': True,
                    'files_created': ['test.md'],
                    'images_extracted': 0
                }

                handler = PDFHandler(archive_dir=str(archive_dir))

                # Add to processing set manually
                handler.processing.add(str(pdf_file))

                # Try to process - should skip
                handler.process_pdf(str(pdf_file))

                # Should not have called convert
                mock_convert.assert_not_called()


class TestScanAndConvertExisting:
    """Tests for scan_and_convert_existing function"""

    def test_scan_empty_directory(self, temp_dir, monkeypatch):
        """Test scanning empty directory"""
        monkeypatch.chdir(temp_dir)
        inputs_dir = temp_dir / "inputs"
        inputs_dir.mkdir()

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            # Should handle gracefully
            scan_and_convert_existing(str(inputs_dir))
            assert True

    def test_scan_nonexistent_directory(self, temp_dir):
        """Test scanning non-existent directory"""
        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            # Should handle gracefully
            scan_and_convert_existing("nonexistent")
            assert True

    def test_scan_with_pdfs(self, temp_dir, monkeypatch):
        """Test scanning directory with PDFs"""
        monkeypatch.chdir(temp_dir)
        inputs_dir = temp_dir / "inputs"
        inputs_dir.mkdir()

        # Create dummy PDFs
        (inputs_dir / "test1.pdf").write_bytes(b"PDF 1")
        (inputs_dir / "test2.pdf").write_bytes(b"PDF 2")

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            with patch('pdf_to_md.batch.auto_watcher.convert_pdf_to_markdown') as mock_convert:
                mock_convert.return_value = {
                    'success': True,
                    'files_created': ['output.md'],
                    'images_extracted': 0
                }

                scan_and_convert_existing(str(inputs_dir))

                # Should have called convert for each PDF
                assert mock_convert.call_count == 2

    def test_scan_ignores_non_pdf_files(self, temp_dir, monkeypatch):
        """Test that scan ignores non-PDF files"""
        monkeypatch.chdir(temp_dir)
        inputs_dir = temp_dir / "inputs"
        inputs_dir.mkdir()

        # Create various files
        (inputs_dir / "test.pdf").write_bytes(b"PDF")
        (inputs_dir / "readme.txt").write_text("text")
        (inputs_dir / "image.png").write_bytes(b"PNG")

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            with patch('pdf_to_md.batch.auto_watcher.convert_pdf_to_markdown') as mock_convert:
                mock_convert.return_value = {
                    'success': True,
                    'files_created': ['output.md'],
                    'images_extracted': 0
                }

                scan_and_convert_existing(str(inputs_dir))

                # Should only process the PDF
                assert mock_convert.call_count == 1

    def test_scan_case_insensitive(self, temp_dir, monkeypatch):
        """Test that PDF extension matching is case-insensitive"""
        monkeypatch.chdir(temp_dir)
        inputs_dir = temp_dir / "inputs"
        inputs_dir.mkdir()

        # Create PDFs with different case extensions
        (inputs_dir / "test1.PDF").write_bytes(b"PDF 1")
        (inputs_dir / "test2.Pdf").write_bytes(b"PDF 2")
        (inputs_dir / "test3.pdf").write_bytes(b"PDF 3")

        with patch('pdf_to_md.batch.auto_watcher.setup_logging'):
            with patch('pdf_to_md.batch.auto_watcher.convert_pdf_to_markdown') as mock_convert:
                mock_convert.return_value = {
                    'success': True,
                    'files_created': ['output.md'],
                    'images_extracted': 0
                }

                scan_and_convert_existing(str(inputs_dir))

                # Should process all three
                assert mock_convert.call_count == 3
