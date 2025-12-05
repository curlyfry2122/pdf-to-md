"""
Tests for output management functions in converter_lib.py
"""

import os
import shutil
from pathlib import Path

import pytest

from pdf_to_md.core.converter_lib import (check_existing_output,
                                          create_flat_output_structure)


class TestCreateFlatOutputStructure:
    """Tests for create_flat_output_structure function"""

    def test_creates_output_directory(self, temp_dir, monkeypatch):
        """Test that output directory is created"""
        monkeypatch.chdir(temp_dir)
        output_dir, images_dir = create_flat_output_structure()

        assert output_dir == "outputs"
        assert images_dir == os.path.join("outputs", "images")
        assert os.path.exists(output_dir)
        assert os.path.isdir(output_dir)

    def test_creates_images_subdirectory(self, temp_dir, monkeypatch):
        """Test that images subdirectory is created"""
        monkeypatch.chdir(temp_dir)
        output_dir, images_dir = create_flat_output_structure()

        assert os.path.exists(images_dir)
        assert os.path.isdir(images_dir)
        assert os.path.dirname(images_dir) == output_dir

    def test_existing_directories_not_overwritten(self, temp_dir, monkeypatch):
        """Test that existing directories are preserved"""
        monkeypatch.chdir(temp_dir)

        # Create directories first
        os.makedirs("outputs/images", exist_ok=True)
        test_file = Path("outputs/test.txt")
        test_file.write_text("test content")

        # Call function
        output_dir, images_dir = create_flat_output_structure()

        # Original content should still exist
        assert test_file.exists()
        assert test_file.read_text() == "test content"

    def test_idempotent_calls(self, temp_dir, monkeypatch):
        """Test that function can be called multiple times safely"""
        monkeypatch.chdir(temp_dir)

        # Call multiple times
        result1 = create_flat_output_structure()
        result2 = create_flat_output_structure()
        result3 = create_flat_output_structure()

        # Should return same results
        assert result1 == result2 == result3

    def test_returns_correct_paths(self, temp_dir, monkeypatch):
        """Test that correct paths are returned"""
        monkeypatch.chdir(temp_dir)
        output_dir, images_dir = create_flat_output_structure()

        # Verify structure
        assert images_dir == os.path.join(output_dir, "images")
        assert os.path.relpath(images_dir, output_dir) == "images"


class TestCheckExistingOutput:
    """Tests for check_existing_output function"""

    def test_no_existing_output(self, temp_dir):
        """Test when no output files exist"""
        pdf_path = "test.pdf"
        output_dir = str(temp_dir)

        existing = check_existing_output(pdf_path, output_dir)
        assert existing == []
        assert isinstance(existing, list)

    def test_finds_single_markdown_file(self, temp_dir):
        """Test finding single .md output file"""
        pdf_path = "test.pdf"
        output_dir = str(temp_dir)

        # Create expected output file
        md_file = temp_dir / "test.md"
        md_file.write_text("# Test")

        existing = check_existing_output(pdf_path, output_dir)
        assert len(existing) == 1
        assert md_file.name in existing[0]

    def test_finds_part_files(self, temp_dir):
        """Test finding chunked part files"""
        pdf_path = "test.pdf"
        output_dir = str(temp_dir)

        # Create part file
        part_file = temp_dir / "test_part_01.md"
        part_file.write_text("# Part 1")

        existing = check_existing_output(pdf_path, output_dir)
        assert len(existing) == 1
        assert "part_01" in existing[0]

    def test_finds_index_file(self, temp_dir):
        """Test finding index file"""
        pdf_path = "test.pdf"
        output_dir = str(temp_dir)

        # Create index file
        index_file = temp_dir / "test_INDEX.md"
        index_file.write_text("# Index")

        existing = check_existing_output(pdf_path, output_dir)
        assert len(existing) == 1
        assert "INDEX" in existing[0]

    def test_finds_multiple_output_files(self, temp_dir):
        """Test finding multiple output files"""
        pdf_path = "test.pdf"
        output_dir = str(temp_dir)

        # Create multiple files
        (temp_dir / "test.md").write_text("# Main")
        (temp_dir / "test_part_01.md").write_text("# Part 1")
        (temp_dir / "test_INDEX.md").write_text("# Index")

        existing = check_existing_output(pdf_path, output_dir)
        assert len(existing) == 3

    def test_sanitizes_pdf_filename(self, temp_dir):
        """Test that PDF filename is sanitized before checking"""
        pdf_path = "file with spaces.pdf"
        output_dir = str(temp_dir)

        # Create file with sanitized name
        md_file = temp_dir / "file_with_spaces.md"
        md_file.write_text("# Test")

        existing = check_existing_output(pdf_path, output_dir)
        assert len(existing) == 1

    def test_handles_special_chars_in_filename(self, temp_dir):
        """Test handling of special characters in PDF filename"""
        pdf_path = "file<special>chars.pdf"
        output_dir = str(temp_dir)

        # Create file with sanitized name
        md_file = temp_dir / "file_special_chars.md"
        md_file.write_text("# Test")

        existing = check_existing_output(pdf_path, output_dir)
        assert len(existing) == 1

    def test_returns_absolute_paths(self, temp_dir):
        """Test that absolute paths are returned"""
        pdf_path = "test.pdf"
        output_dir = str(temp_dir)

        md_file = temp_dir / "test.md"
        md_file.write_text("# Test")

        existing = check_existing_output(pdf_path, output_dir)
        assert os.path.isabs(existing[0])

    def test_nonexistent_output_dir(self):
        """Test with non-existent output directory"""
        pdf_path = "test.pdf"
        output_dir = "/nonexistent/path"

        existing = check_existing_output(pdf_path, output_dir)
        assert existing == []

    def test_with_pdf_path_including_directory(self, temp_dir):
        """Test with PDF path including directory"""
        pdf_path = "/some/path/to/test.pdf"
        output_dir = str(temp_dir)

        md_file = temp_dir / "test.md"
        md_file.write_text("# Test")

        existing = check_existing_output(pdf_path, output_dir)
        assert len(existing) == 1
