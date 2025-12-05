"""
Pytest configuration and fixtures for pdf-to-md tests
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

# =============================================================================
# Directory and Path Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create a temporary directory for test outputs, cleanup after test"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    if Path(temp_path).exists():
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def temp_output_dir(temp_dir):
    """Create a temp directory specifically for output files"""
    output_path = temp_dir / "outputs"
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path


@pytest.fixture
def temp_images_dir(temp_dir):
    """Create a temp directory for extracted images"""
    images_path = temp_dir / "images"
    images_path.mkdir(parents=True, exist_ok=True)
    return images_path


# =============================================================================
# PDF Fixtures (Using Real PDFs from inputs/)
# =============================================================================

@pytest.fixture(scope="session")
def project_root():
    """Get the project root directory"""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def inputs_dir(project_root):
    """Get the inputs directory with real PDFs"""
    inputs_path = project_root / "inputs"
    if inputs_path.exists():
        return inputs_path
    return None


@pytest.fixture(scope="session")
def real_pdf_files(inputs_dir):
    """Get list of real PDF files from inputs/ directory"""
    if inputs_dir and inputs_dir.exists():
        pdfs = list(inputs_dir.glob("*.pdf"))
        return sorted(pdfs, key=lambda p: p.stat().st_size)
    return []


@pytest.fixture
def small_pdf(real_pdf_files):
    """Get the smallest real PDF for quick tests"""
    if real_pdf_files:
        return real_pdf_files[0]
    pytest.skip("No real PDFs available in inputs/ directory")


@pytest.fixture
def medium_pdf(real_pdf_files):
    """Get a medium-sized PDF"""
    if len(real_pdf_files) >= 2:
        return real_pdf_files[len(real_pdf_files) // 2]
    elif real_pdf_files:
        return real_pdf_files[0]
    pytest.skip("No real PDFs available in inputs/ directory")


@pytest.fixture
def large_pdf(real_pdf_files):
    """Get the largest real PDF for chunking tests"""
    if real_pdf_files:
        return real_pdf_files[-1]
    pytest.skip("No real PDFs available in inputs/ directory")


# =============================================================================
# Mock PyMuPDF (fitz) Objects
# =============================================================================

@pytest.fixture
def mock_fitz_document():
    """Create a mock fitz.Document object"""
    mock_doc = Mock()
    mock_doc.name = "test.pdf"
    mock_doc.page_count = 5
    mock_doc.metadata = {
        "title": "Test PDF",
        "author": "Test Author"
    }
    mock_pages = []
    for i in range(5):
        mock_page = Mock()
        mock_page.number = i
        mock_page.get_text.return_value = f"Page {i+1} content"
        mock_page.get_images.return_value = []
        mock_page.rect = Mock(width=612, height=792)
        mock_pages.append(mock_page)
    mock_doc.__iter__ = Mock(return_value=iter(mock_pages))
    mock_doc.__getitem__ = Mock(side_effect=lambda i: mock_pages[i])
    mock_doc.__len__ = Mock(return_value=5)
    mock_doc.load_page = Mock(side_effect=lambda i: mock_pages[i])
    return mock_doc


@pytest.fixture
def mock_fitz_page():
    """Create a mock fitz.Page object"""
    mock_page = Mock()
    mock_page.number = 0
    mock_page.get_text.return_value = "Sample page content"
    mock_page.get_images.return_value = []
    mock_page.rect = Mock(width=612, height=792)
    mock_page.get_pixmap.return_value = Mock()
    return mock_page


@pytest.fixture
def mock_fitz_page_with_images():
    """Create a mock fitz.Page with images"""
    mock_page = Mock()
    mock_page.number = 0
    mock_page.get_text.return_value = "Page with images"
    mock_page.get_images.return_value = [
        (0, 0, 100, 100, 8, "DeviceRGB", "", "img1", ""),
        (1, 0, 200, 200, 8, "DeviceRGB", "", "img2", "")
    ]
    mock_page.rect = Mock(width=612, height=792)
    mock_pixmap = Mock()
    mock_pixmap.width = 100
    mock_pixmap.height = 100
    mock_pixmap.tobytes.return_value = b"fake_image_data"
    mock_page.get_pixmap.return_value = mock_pixmap
    return mock_page


@pytest.fixture
def mock_fitz_pixmap():
    """Create a mock fitz.Pixmap object"""
    mock_pixmap = Mock()
    mock_pixmap.width = 100
    mock_pixmap.height = 100
    mock_pixmap.n = 3
    mock_pixmap.alpha = 0
    mock_pixmap.colorspace = Mock(name="DeviceRGB")
    mock_pixmap.tobytes.return_value = b"fake_image_data"
    return mock_pixmap


# =============================================================================
# Mock python-docx Objects
# =============================================================================

@pytest.fixture
def mock_docx_document():
    """Create a mock python-docx Document object"""
    mock_doc = Mock()
    mock_para1 = Mock()
    mock_para1.text = "First paragraph"
    mock_para1.style.name = "Normal"
    mock_para1.runs = []
    mock_para2 = Mock()
    mock_para2.text = "Second paragraph"
    mock_para2.style.name = "Normal"
    mock_para2.runs = []
    mock_doc.paragraphs = [mock_para1, mock_para2]
    mock_doc.tables = []
    mock_doc.inline_shapes = []
    return mock_doc


@pytest.fixture
def mock_docx_table():
    """Create a mock python-docx Table object"""
    mock_table = Mock()
    mock_cell11 = Mock()
    mock_cell11.text = "Header 1"
    mock_cell12 = Mock()
    mock_cell12.text = "Header 2"
    mock_cell21 = Mock()
    mock_cell21.text = "Data 1"
    mock_cell22 = Mock()
    mock_cell22.text = "Data 2"
    mock_row1 = Mock()
    mock_row1.cells = [mock_cell11, mock_cell12]
    mock_row2 = Mock()
    mock_row2.cells = [mock_cell21, mock_cell22]
    mock_table.rows = [mock_row1, mock_row2]
    return mock_table


# =============================================================================
# Sample Data Fixtures
# =============================================================================

@pytest.fixture
def sample_filenames():
    """Sample filenames for testing sanitization"""
    return [
        "normal_file.pdf",
        "file with spaces.pdf",
        "file<with>special:chars.pdf",
        "file|with|pipes.pdf",
        "file?with?questions.pdf",
        "very_long_" + "a" * 300 + ".pdf",
        "",
        "file.PDF",
        "file_with_underscores_123.pdf"
    ]


@pytest.fixture
def sample_pdf_info():
    """Sample PDF metadata for testing"""
    return {
        "title": "Test Document",
        "author": "Test Author",
        "subject": "Testing",
        "pages": 10,
        "file_size": 1024 * 1024,
        "encrypted": False
    }


# =============================================================================
# Conversion Result Fixtures
# =============================================================================

@pytest.fixture
def sample_conversion_result():
    """Sample conversion result dictionary"""
    return {
        "pdf_file": "test.pdf",
        "status": "success",
        "pages_processed": 5,
        "images_extracted": 3,
        "output_file": "test.md",
        "processing_time": 1.5,
        "file_size": 2048,
        "errors": []
    }


@pytest.fixture
def sample_failed_conversion_result():
    """Sample failed conversion result"""
    return {
        "pdf_file": "bad.pdf",
        "status": "error",
        "pages_processed": 0,
        "images_extracted": 0,
        "output_file": None,
        "processing_time": 0.1,
        "file_size": 0,
        "errors": ["Failed to open PDF: File not found"]
    }


# =============================================================================
# Cleanup and Utility Fixtures
# =============================================================================

@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    """Change to test directory and restore after test"""
    original_dir = os.getcwd()
    project_root = Path(__file__).parent.parent
    monkeypatch.chdir(project_root)
    yield
    os.chdir(original_dir)


@pytest.fixture
def mock_logging():
    """Mock logging to suppress output during tests"""
    import logging
    logging.disable(logging.CRITICAL)
    yield
    logging.disable(logging.NOTSET)
