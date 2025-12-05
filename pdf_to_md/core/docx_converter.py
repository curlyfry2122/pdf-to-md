#!/usr/bin/env python3
"""
Word Document to Markdown Converter
Converts .docx files to Markdown with image extraction and detailed alt text
"""

import io
import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, Iterator, Optional

from docx import Document
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.table import Table, _Cell
from docx.text.paragraph import Paragraph

# Import from core library (for shared utilities)
from pdf_to_md.core.converter_lib import (create_flat_output_structure,
                                          sanitize_filename, setup_logging)

# Import alt text pattern recognizer
try:
    from pdf_to_md.alt_text.patterns import get_recognizer
    ALT_TEXT_PATTERNS_AVAILABLE = True
except ImportError:
    ALT_TEXT_PATTERNS_AVAILABLE = False
    logging.debug("alt_text_patterns module not available, using basic alt text")


def validate_docx_path(docx_path: str) -> str:
    """
    Validate Word document path for security and existence

    Args:
        docx_path: Path to Word document file

    Returns:
        str: Absolute path to validated document

    Raises:
        ValueError: If path is invalid or not a Word document
        FileNotFoundError: If file doesn't exist
    """
    if not docx_path or not isinstance(docx_path, str):
        raise ValueError("Invalid document path provided")

    # Resolve to absolute path
    abs_path = os.path.abspath(docx_path)

    # Check if file exists
    if not os.path.exists(abs_path):
        raise FileNotFoundError(f"Document file not found: {docx_path}")

    # Check if it's actually a file
    if not os.path.isfile(abs_path):
        raise ValueError(f"Path is not a file: {docx_path}")

    # Basic Word document validation
    if not abs_path.lower().endswith(('.docx', '.doc')):
        raise ValueError(f"File is not a Word document: {docx_path}")

    return abs_path


def generate_alt_text_for_docx_image(
    img_index: int,
    context_text: str = "",
    enable_detailed_alt_text: bool = True
) -> str:
    """
    Generate alt text for a Word document image.

    Since Word documents don't have pages like PDFs, we use document context
    and the pattern recognizer to generate appropriate alt text.

    Args:
        img_index: Image index in document (0-indexed)
        context_text: Text content around the image for context
        enable_detailed_alt_text: Whether to generate detailed alt text

    Returns:
        str: Alt text description
    """
    if not enable_detailed_alt_text or not ALT_TEXT_PATTERNS_AVAILABLE:
        return f"Image {img_index + 1} from document"

    try:
        recognizer = get_recognizer()
        context_text_lower = context_text.lower()

        # Check for logo patterns (first two images are often logos)
        if img_index < 2:
            # First image is typically left logo (FEWS NET)
            if img_index == 0:
                return recognizer.logo_patterns['fews_net']['description']
            # Second image is typically right logo (USAID)
            elif img_index == 1:
                return recognizer.logo_patterns['usaid']['description']

        # Check for UI patterns
        best_match = None
        best_score = 0

        for ui_type, pattern in recognizer.ui_patterns.items():
            matches = sum(1 for keyword in pattern['keywords'] if keyword in context_text_lower)
            score = matches / len(pattern['keywords'])

            if score > best_score:
                best_score = score
                best_match = pattern

        if best_match and best_score >= 0.3:
            return best_match['description_template']

        # Check for chart/graph patterns
        chart_keywords = [
            'chart', 'graph', 'plot', 'figure', 'diagram',
            'data', 'trend', 'analysis', 'visualization'
        ]
        chart_matches = sum(1 for keyword in chart_keywords if keyword in context_text_lower)

        if chart_matches >= 2:
            return 'Chart or graph showing data visualization'

        # Generate contextual description
        if 'screenshot' in context_text_lower or 'screen' in context_text_lower:
            return 'Screenshot illustrating content'
        elif 'diagram' in context_text_lower:
            return 'Diagram illustrating content'
        elif 'example' in context_text_lower:
            return 'Example image illustrating content'
        elif 'interface' in context_text_lower:
            return 'Interface screenshot'
        else:
            return f"Image {img_index + 1} illustrating document content"

    except Exception as e:
        logging.warning(f"Error generating alt text: {e}")
        return f"Image {img_index + 1} from document"


def extract_images_from_docx(doc, images_dir: str, base_name: str, context_text: str = "", enable_detailed_alt_text: bool = True) -> Dict[str, str]:
    """
    Extract images from Word document with detailed alt text.

    Args:
        doc: python-docx Document object
        images_dir: Directory to save images
        base_name: Base name for image files
        context_text: Document text for context (optional)
        enable_detailed_alt_text: Whether to generate detailed alt text

    Returns:
        dict: Mapping of image relationship IDs to markdown references
    """
    image_refs = {}
    image_count = 0

    # Get all image relationships in the document
    for rel_id, rel in doc.part.rels.items():
        if "image" in rel.target_ref:
            try:
                # Get image data
                image_data = rel.target_part.blob

                # Determine image format from content type
                content_type = rel.target_part.content_type
                if 'png' in content_type:
                    ext = 'png'
                elif 'jpeg' in content_type or 'jpg' in content_type:
                    ext = 'jpg'
                elif 'gif' in content_type:
                    ext = 'gif'
                else:
                    ext = 'png'  # Default to PNG

                # Save image
                img_name = f"{base_name}_img_{image_count + 1:02d}.{ext}"
                img_path = os.path.join(images_dir, img_name)

                with open(img_path, 'wb') as img_file:
                    img_file.write(image_data)

                # Generate alt text
                alt_text = generate_alt_text_for_docx_image(
                    image_count,
                    context_text,
                    enable_detailed_alt_text
                )

                # Create markdown reference (relative path)
                rel_img_path = f"images/{img_name}"
                image_refs[rel_id] = f"![{alt_text}]({rel_img_path})\n\n"

                image_count += 1
                logging.debug(f"Extracted image: {img_name}")

            except Exception as e:
                logging.warning(f"Could not extract image {rel_id}: {e}")
                continue

    logging.info(f"Extracted {image_count} images from document")
    return image_refs


def process_table(table) -> str:
    """
    Convert a Word table to Markdown format.

    Args:
        table: python-docx Table object

    Returns:
        str: Markdown table representation
    """
    markdown_lines = []

    try:
        # Get table dimensions
        num_rows = len(table.rows)
        num_cols = len(table.columns)

        if num_rows == 0 or num_cols == 0:
            return ""

        # Process table rows
        for row_idx, row in enumerate(table.rows):
            cells = []
            for cell in row.cells:
                # Get cell text, clean it up
                cell_text = cell.text.strip().replace('\n', ' ').replace('|', '\\|')
                cells.append(cell_text)

            # Add row
            markdown_lines.append("| " + " | ".join(cells) + " |")

            # Add header separator after first row
            if row_idx == 0:
                markdown_lines.append("| " + " | ".join(["---"] * num_cols) + " |")

        markdown_lines.append("")  # Empty line after table
        return "\n".join(markdown_lines)

    except Exception as e:
        logging.warning(f"Error processing table: {e}")
        return ""


def iter_block_items(parent) -> Iterator:
    """
    Generate a sequence of paragraphs and tables in document order.
    Yields each paragraph or table in the order they appear.

    Args:
        parent: Document or table cell object

    Yields:
        Paragraph or Table objects in document order
    """
    from docx.document import Document
    if isinstance(parent, Document):
        parent_elm = parent.element.body
    else:
        parent_elm = parent._element

    for child in parent_elm.iterchildren():
        if isinstance(child, CT_P):
            yield Paragraph(child, parent)
        elif isinstance(child, CT_Tbl):
            yield Table(child, parent)


def convert_docx_to_markdown(
    docx_path: str,
    enable_detailed_alt_text: bool = True
) -> Dict[str, Any]:
    """
    Convert Word document to Markdown with image extraction and detailed alt text.

    Args:
        docx_path: Path to Word document file
        enable_detailed_alt_text: Generate detailed alt text descriptions (default: True)

    Returns:
        dict: Conversion results with keys:
            - success: bool
            - output_dir: str
            - file_created: str
            - images_extracted: int
            - error: str (if failed)
    """
    try:
        # Validate input
        validated_path = validate_docx_path(docx_path)

        logging.info(f"Converting Word document: {os.path.basename(validated_path)}")
        logging.info("=" * 60)

        # Open document
        doc = Document(validated_path)

        # Create flat output structure
        output_dir, images_dir = create_flat_output_structure()

        # Get base name for files
        safe_name = sanitize_filename(os.path.basename(validated_path))

        # Extract all text for context (used in alt text generation)
        context_text = "\n".join([para.text for para in doc.paragraphs])

        # Extract images first (to get the mapping)
        logging.info("Extracting images...")
        image_refs = extract_images_from_docx(
            doc, images_dir, safe_name,
            context_text=context_text,
            enable_detailed_alt_text=enable_detailed_alt_text
        )

        # Build markdown content
        markdown_content = []
        markdown_content.append(f"# {safe_name}\n\n")
        markdown_content.append(
            f"*Converted on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        )

        logging.info("Converting document content...")

        # Process document in order (paragraphs and tables)
        for block in iter_block_items(doc):
            if isinstance(block, Paragraph):
                para = block
                text = para.text.strip()

                # Check if paragraph contains images
                has_images = False
                for run in para.runs:
                    if run._element.xpath('.//w:drawing'):
                        has_images = True
                        # Try to find the image relationship
                        for drawing in run._element.xpath('.//w:drawing'):
                            # Look for the image relationship ID
                            blips = drawing.xpath('.//a:blip')
                            for blip in blips:
                                embed_id = blip.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
                                if embed_id and embed_id in image_refs:
                                    markdown_content.append(image_refs[embed_id])

                # Add text if present
                if text:
                    # Detect heading level based on style
                    if para.style.name.startswith('Heading'):
                        try:
                            level = int(para.style.name.split()[-1])
                            markdown_content.append(f"{'#' * (level + 1)} {text}\n\n")
                        except (ValueError, AttributeError, IndexError) as e:
                            # Log but continue - treat as regular text if level parsing fails
                            logger.warning(f"Could not parse heading level from style '{para.style.name}': {e}")
                            markdown_content.append(f"{text}\n\n")
                    else:
                        markdown_content.append(f"{text}\n\n")

            elif isinstance(block, Table):
                # Convert table to markdown
                table_md = process_table(block)
                if table_md:
                    markdown_content.append(table_md + "\n")

        # Write markdown file
        markdown_filename = f"{safe_name}.md"
        markdown_path = os.path.join(output_dir, markdown_filename)

        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(''.join(markdown_content))

        logging.info("=" * 60)
        logging.info(f"Conversion complete!")
        logging.info(f"File created: {markdown_filename}")
        logging.info(f"Images extracted: {len(image_refs)}")
        logging.info(f"Output location: {output_dir}")

        return {
            'success': True,
            'output_dir': output_dir,
            'file_created': markdown_path,
            'images_extracted': len(image_refs)
        }

    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        return {
            'success': False,
            'error': str(e)
        }


def main() -> None:
    """Main entry point for command-line usage"""
    setup_logging()

    try:
        if len(sys.argv) > 1:
            docx_path = sys.argv[1]
        else:
            # Look for Word documents in inputs directory
            import glob
            docx_files = glob.glob("inputs/*.docx") + glob.glob("inputs/*.doc")

            if not docx_files:
                logging.error("No Word document specified and no .docx files found in inputs/ directory")
                logging.info("Usage: python docx_converter.py <docx_path>")
                sys.exit(1)

            docx_path = docx_files[0]
            logging.info(f"No file specified, using: {os.path.basename(docx_path)}")

        result = convert_docx_to_markdown(docx_path)

        if result.get('success', False):
            logging.info(f"\nSuccess! Output saved to: {result['output_dir']}")
        else:
            logging.error(f"Conversion failed: {result.get('error', 'Unknown error')}")
            sys.exit(1)

    except KeyboardInterrupt:
        logging.info("\nConversion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        import traceback
        logging.debug(traceback.format_exc())
        sys.exit(1)


if __name__ == "__main__":
    main()
