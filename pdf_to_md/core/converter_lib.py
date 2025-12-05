#!/usr/bin/env python3
"""
PDF Converter Core Library
Common utilities and functions for PDF to Markdown conversion
"""

import logging
import math
import os
import re
from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Iterator, List, Optional, Tuple

import fitz  # PyMuPDF

# Import pattern recognizer for detailed alt text
try:
    from pdf_to_md.alt_text.patterns import get_recognizer
    ALT_TEXT_PATTERNS_AVAILABLE = True
except ImportError:
    ALT_TEXT_PATTERNS_AVAILABLE = False
    logging.debug("alt_text_patterns module not available, using basic alt text")


# ============================================================================
# FILE HANDLING
# ============================================================================

def sanitize_filename(filename: str) -> str:
    """
    Create filesystem-safe filename from PDF name
    
    Args:
        filename: Original filename (with or without extension)
        
    Returns:
        str: Sanitized filename safe for filesystem use
    """
    # Remove extension and get base name
    base_name = os.path.splitext(os.path.basename(filename))[0]
    
    # Remove or replace problematic characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', base_name)
    safe_name = re.sub(r'\s+', '_', safe_name.strip())
    
    # Limit length to prevent filesystem issues
    safe_name = safe_name[:200] if len(safe_name) > 200 else safe_name
    
    return safe_name.strip('_')


def validate_pdf_path(pdf_path: str) -> str:
    """
    Validate PDF path for security and existence
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        str: Absolute path to validated PDF
        
    Raises:
        ValueError: If path is invalid or not a PDF
        FileNotFoundError: If file doesn't exist
    """
    if not pdf_path or not isinstance(pdf_path, str):
        raise ValueError("Invalid PDF path provided")
    
    # Resolve to absolute path
    abs_path = os.path.abspath(pdf_path)
    
    # Check if file exists
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Check if it's actually a file
    if not os.path.isfile(abs_path):
        raise ValueError(f"Path is not a file: {pdf_path}")
    
    # Basic PDF validation
    if not abs_path.lower().endswith('.pdf'):
        raise ValueError(f"File is not a PDF: {pdf_path}")
    
    return abs_path


@contextmanager
def open_pdf_document(pdf_path: str) -> Iterator:
    """
    Context manager for safe PDF document handling
    
    Args:
        pdf_path: Path to PDF file
        
    Yields:
        fitz.Document: Opened PDF document
    """
    doc = None
    try:
        doc = fitz.open(pdf_path)
        yield doc
    except Exception as e:
        logging.error(f"Error opening PDF document: {e}")
        raise
    finally:
        if doc:
            doc.close()
            logging.debug("PDF document closed successfully")


# ============================================================================
# OUTPUT MANAGEMENT
# ============================================================================

def create_flat_output_structure() -> Tuple[str, str]:
    """
    Create flat output directory structure per CLAUDE.md
    All markdown files in outputs/, images in outputs/images/
    
    Returns:
        tuple: (output_dir, images_dir) paths
    """
    output_dir = "outputs"
    images_dir = os.path.join(output_dir, "images")
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(images_dir, exist_ok=True)
    
    logging.info(f"Output directories ready: {output_dir}, {images_dir}")
    return output_dir, images_dir


def check_existing_output(pdf_path: str, output_dir: str) -> List[str]:
    """
    Check if output files already exist for this PDF
    
    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory path
        
    Returns:
        list: List of existing output files
    """
    safe_name = sanitize_filename(os.path.basename(pdf_path))
    
    potential_files = [
        os.path.join(output_dir, f"{safe_name}.md"),
        os.path.join(output_dir, f"{safe_name}_part_01.md"),
        os.path.join(output_dir, f"{safe_name}_INDEX.md")
    ]
    
    existing_files = [f for f in potential_files if os.path.exists(f)]
    return existing_files


# ============================================================================
# PDF ANALYSIS
# ============================================================================

def analyze_pdf_for_chunking(pdf_path: str) -> Dict[str, Any]:
    """
    Analyze PDF to determine if chunking is needed
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        dict: Analysis results with keys:
            - chunking_needed: bool
            - page_count: int
            - chunk_size: int
            - num_chunks: int
            - file_size_mb: float
            - is_image_based: bool
            - needs_ocr: bool
    """
    try:
        with open_pdf_document(pdf_path) as doc:
            page_count = len(doc)
            file_size_mb = os.path.getsize(pdf_path) / (1024 * 1024)
            
            # Check if PDF is image-based (needs OCR)
            total_chars = 0
            sample_size = min(3, page_count)
            for page_num in range(sample_size):
                page = doc[page_num]
                text = page.get_text()
                total_chars += len(text.strip())
            
            avg_chars = total_chars / sample_size if sample_size > 0 else 0
            is_image_based = avg_chars < 50
            needs_ocr = is_image_based
            
            # Chunking thresholds
            chunking_needed = page_count > 100 or file_size_mb > 50
            
            if chunking_needed:
                if page_count > 200:
                    chunk_size = 50
                elif page_count > 100:
                    chunk_size = 25
                else:
                    chunk_size = 20
            else:
                chunk_size = page_count  # Single chunk
            
            num_chunks = math.ceil(page_count / chunk_size) if chunking_needed else 1
            
            logging.info(
                f"PDF analysis: {page_count} pages, {file_size_mb:.2f} MB, "
                f"chunking: {chunking_needed}, image-based: {is_image_based}"
            )
            
            if is_image_based:
                logging.warning(
                    "Image-based PDF detected! Consider using pdf_converter_ocr.py for better results"
                )
            
            return {
                'chunking_needed': chunking_needed,
                'page_count': page_count,
                'chunk_size': chunk_size,
                'num_chunks': num_chunks,
                'file_size_mb': file_size_mb,
                'is_image_based': is_image_based,
                'needs_ocr': needs_ocr
            }
    except Exception as e:
        logging.error(f"Error analyzing PDF: {e}")
        raise


# ============================================================================
# IMAGE EXTRACTION & ALT TEXT GENERATION
# ============================================================================

def generate_detailed_alt_text(
    pix: fitz.Pixmap,
    page_num: int,
    img_index: int,
    page_text: str = "",
    page_width: float = 0,
    page_height: float = 0,
    img_bbox: Optional[tuple] = None,
    enable_ai_vision: bool = False,
    detail_level: str = "standard"
) -> str:
    """
    Generate detailed, context-aware alt text for an image.

    Uses hybrid approach:
    1. Pattern recognition for common elements (logos, UI components)
    2. Context from page text
    3. Optional AI vision analysis for complex images (if enabled)

    Args:
        pix: PyMuPDF Pixmap object
        page_num: Page number (0-indexed)
        img_index: Image index on page (0-indexed)
        page_text: Text content from the page for context
        page_width: Page width in points
        page_height: Page height in points
        img_bbox: Image bounding box (x0, y0, x1, y1) if available
        enable_ai_vision: Whether to use AI vision API for complex images
        detail_level: Level of detail ('concise', 'standard', 'verbose')

    Returns:
        str: Detailed alt text description
    """
    # Fallback to generic description if pattern recognizer not available
    if not ALT_TEXT_PATTERNS_AVAILABLE:
        logging.debug("Using basic alt text (pattern recognizer not available)")
        return f"Image from page {page_num + 1}"

    try:
        # Initialize pattern recognizer
        recognizer = get_recognizer()

        # Analyze image using pattern recognition
        analysis = recognizer.analyze_image(
            pix=pix,
            page_num=page_num,
            img_index=img_index,
            page_text=page_text,
            page_width=page_width,
            page_height=page_height,
            img_bbox=img_bbox
        )

        # Check if AI vision analysis is needed and enabled
        if enable_ai_vision and recognizer.should_use_ai_vision(analysis):
            # Placeholder for AI vision integration
            # TODO: Implement AI vision API call (Claude, GPT-4V, etc.)
            logging.debug(
                f"AI vision recommended for page {page_num + 1}, "
                f"img {img_index + 1} (not yet implemented)"
            )
            # For now, use pattern-based description
            alt_text = analysis['alt_text']
        else:
            alt_text = analysis['alt_text']

        # Adjust detail level if needed
        if detail_level == "concise" and len(alt_text) > 100:
            # Truncate verbose descriptions for concise mode
            alt_text = alt_text[:97] + "..."
        elif detail_level == "verbose":
            # Add image metadata for verbose mode
            alt_text = f"{alt_text} (Page {page_num + 1}, Image {img_index + 1})"

        logging.debug(
            f"Generated alt text for page {page_num + 1}, img {img_index + 1}: "
            f"{alt_text[:50]}... (confidence: {analysis['confidence']:.2f})"
        )

        return alt_text

    except Exception as e:
        logging.warning(f"Error generating detailed alt text: {e}")
        # Fallback to generic description
        return f"Image from page {page_num + 1}"


def extract_page_images(
    page,  # fitz.Page
    page_num: int,
    doc,  # fitz.Document
    images_dir: str,
    base_name: str,
    enable_detailed_alt_text: bool = True,
    enable_ai_vision: bool = False,
    detail_level: str = "standard"
) -> Tuple[List[str], int]:
    """
    Extract images from a PDF page with detailed alt text descriptions.

    Args:
        page: PyMuPDF page object
        page_num: Page number (0-indexed)
        doc: PyMuPDF document object
        images_dir: Directory to save images
        base_name: Base name for image files
        enable_detailed_alt_text: Whether to generate detailed alt text (default: True)
        enable_ai_vision: Whether to use AI vision analysis (default: False)
        detail_level: Level of detail - 'concise', 'standard', or 'verbose' (default: 'standard')

    Returns:
        tuple: (list of markdown image references, image count)
    """
    image_refs = []
    image_count = 0

    # Extract page text and dimensions for context
    page_text = page.get_text() if enable_detailed_alt_text else ""
    page_rect = page.rect
    page_width = page_rect.width
    page_height = page_rect.height

    image_list = page.get_images(full=True)  # Get full image info including bbox
    for img_index, img in enumerate(image_list):
        pix = None
        try:
            xref = img[0]
            pix = fitz.Pixmap(doc, xref)

            if pix.n - pix.alpha < 4:  # GRAY or RGB
                img_name = f"{base_name}_page_{page_num + 1:03d}_img_{img_index + 1:02d}.png"
                img_path = os.path.join(images_dir, img_name)
                pix.save(img_path)

                # Generate alt text
                if enable_detailed_alt_text:
                    # Get image bounding box if available
                    img_bbox = None
                    try:
                        img_rects = page.get_image_rects(xref)
                        if img_rects:
                            bbox = img_rects[0]
                            img_bbox = (bbox.x0, bbox.y0, bbox.x1, bbox.y1)
                    except Exception as e:
                        # Log but continue - image rect extraction is optional
                        logger.warning(f"Could not get image rectangles for xref {xref}: {e}")

                    alt_text = generate_detailed_alt_text(
                        pix=pix,
                        page_num=page_num,
                        img_index=img_index,
                        page_text=page_text,
                        page_width=page_width,
                        page_height=page_height,
                        img_bbox=img_bbox,
                        enable_ai_vision=enable_ai_vision,
                        detail_level=detail_level
                    )
                else:
                    # Fallback to simple alt text
                    alt_text = f"Image from page {page_num + 1}"

                # Add image reference (relative path)
                rel_img_path = f"images/{img_name}"
                image_refs.append(f"![{alt_text}]({rel_img_path})\n\n")
                image_count += 1
                logging.debug(f"Extracted image: {img_name}")

        except Exception as e:
            logging.warning(f"Could not extract image from page {page_num + 1}: {e}")
            continue
        finally:
            if pix:
                pix = None  # Free memory

    return image_refs, image_count


# ============================================================================
# MASTER INDEX CREATION
# ============================================================================

def create_master_index(pdf_path: str, output_dir: str, chunk_files: List[str], analysis_info: Dict[str, Any]) -> str:
    """
    Create master index file for chunked documents
    
    Args:
        pdf_path: Path to original PDF
        output_dir: Output directory
        chunk_files: List of created chunk file paths
        analysis_info: Analysis dictionary from analyze_pdf_for_chunking
        
    Returns:
        str: Path to created index file
    """
    base_name = sanitize_filename(os.path.basename(pdf_path))
    index_path = os.path.join(output_dir, f"{base_name}_INDEX.md")
    
    content = []
    content.append(f"# {base_name}\n\n")
    content.append(
        f"*Master Index - Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
    )
    content.append(f"**Document Information:**\n")
    content.append(f"- Total Pages: {analysis_info['page_count']}\n")
    content.append(f"- File Size: {analysis_info['file_size_mb']:.2f} MB\n")
    content.append(f"- Parts: {analysis_info['num_chunks']}\n\n")
    
    content.append("## Document Parts\n\n")
    
    chunk_size = analysis_info['chunk_size']
    for i, chunk_file in enumerate(chunk_files):
        start_page = i * chunk_size + 1
        end_page = min((i + 1) * chunk_size, analysis_info['page_count'])
        filename = os.path.basename(chunk_file)
        
        content.append(f"### [{filename}]({filename})\n")
        content.append(f"Pages {start_page}-{end_page}\n\n")
    
    # Write index file
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(''.join(content))
    
    logging.info(f"Created master index: {os.path.basename(index_path)}")
    return index_path


# ============================================================================
# LOGGING SETUP
# ============================================================================

def setup_logging(level: int = logging.INFO, log_file: Optional[str] = None) -> None:
    """
    Setup logging configuration
    
    Args:
        level: Logging level (default: INFO)
        log_file: Optional log file path
    """
    handlers_list = [logging.StreamHandler()]
    
    if log_file:
        handlers_list.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers_list
    )


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def format_file_size(size_bytes: float) -> str:
    """
    Format file size in human-readable format
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        str: Formatted size string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def get_pdf_info(pdf_path: str) -> Optional[Dict[str, Any]]:
    """
    Get basic information about a PDF file
    
    Args:
        pdf_path: Path to PDF file
        
    Returns:
        dict: PDF information including page count, size, etc.
    """
    try:
        with open_pdf_document(pdf_path) as doc:
            file_size_bytes = os.path.getsize(pdf_path)
            metadata = doc.metadata if doc.metadata else {}
            
            return {
                'path': pdf_path,
                'filename': os.path.basename(pdf_path),
                'page_count': len(doc),
                'file_size_bytes': file_size_bytes,
                'file_size_formatted': format_file_size(file_size_bytes),
                'title': metadata.get('title', 'Unknown'),
                'author': metadata.get('author', 'Unknown'),
            }
    except Exception as e:
        logging.error(f"Error getting PDF info: {e}")
        return None
