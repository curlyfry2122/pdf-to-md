#!/usr/bin/env python3
"""
Unified PDF to Markdown Converter
Combines best practices from all converter scripts with flat output structure
"""

import logging
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# Import from core library
from pdf_to_md.core.converter_lib import (analyze_pdf_for_chunking,
                                          check_existing_output,
                                          create_flat_output_structure,
                                          create_master_index,
                                          extract_page_images,
                                          open_pdf_document, sanitize_filename,
                                          setup_logging, validate_pdf_path)


def process_pdf_chunk(
    pdf_path: str,
    output_dir: str,
    images_dir: str,
    start_page: int,
    end_page: int,
    chunk_num: Optional[int] = None,
    enable_detailed_alt_text: bool = True,
    enable_ai_vision: bool = False,
    detail_level: str = "standard"
) -> Tuple[Optional[str], int]:
    """
    Process a chunk of PDF pages with flat output structure and detailed alt text.

    Args:
        pdf_path: Path to PDF file
        output_dir: Output directory
        images_dir: Images directory
        start_page: Starting page number (0-indexed)
        end_page: Ending page number (0-indexed, exclusive)
        chunk_num: Chunk number (for multi-part documents) or None
        enable_detailed_alt_text: Generate detailed alt text descriptions (default: True)
        enable_ai_vision: Use AI vision analysis for complex images (default: False)
        detail_level: Alt text detail level - 'concise', 'standard', 'verbose' (default: 'standard')

    Returns:
        tuple: (markdown_path, image_count)
    """
    markdown_content = []
    total_images = 0
    markdown_path = None
    
    try:
        safe_name = sanitize_filename(os.path.basename(pdf_path))
        
        # Determine output filename
        if chunk_num is not None:
            markdown_filename = f"{safe_name}_part_{chunk_num:02d}.md"
        else:
            markdown_filename = f"{safe_name}.md"
        
        markdown_path = os.path.join(output_dir, markdown_filename)
        
        with open_pdf_document(pdf_path) as doc:
            actual_end_page = min(end_page, len(doc))
            logging.info(f"Processing pages {start_page + 1}-{actual_end_page} -> {markdown_filename}")
            
            # Add header
            if chunk_num is not None:
                markdown_content.append(f"# {safe_name} - Part {chunk_num}\n\n")
                markdown_content.append(f"*Pages {start_page + 1}-{actual_end_page}*\n\n")
            else:
                markdown_content.append(f"# {safe_name}\n\n")
                markdown_content.append(
                    f"*Converted on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
                )
            
            # Process pages in range
            for page_num in range(start_page, actual_end_page):
                try:
                    page = doc[page_num]
                    
                    # Extract text
                    text = page.get_text()
                    
                    if text.strip():
                        if page_num > start_page:  # Add separator between pages
                            markdown_content.append("\n---\n\n")
                        
                        markdown_content.append(f"## Page {page_num + 1}\n\n")
                        markdown_content.append(text.strip())
                        markdown_content.append("\n\n")
                    
                    # Extract images with detailed alt text
                    image_refs, img_count = extract_page_images(
                        page, page_num, doc, images_dir, safe_name,
                        enable_detailed_alt_text=enable_detailed_alt_text,
                        enable_ai_vision=enable_ai_vision,
                        detail_level=detail_level
                    )
                    markdown_content.extend(image_refs)
                    total_images += img_count
                
                except Exception as e:
                    logging.error(f"Error processing page {page_num + 1}: {e}")
                    continue
        
        # Write markdown file
        with open(markdown_path, 'w', encoding='utf-8') as f:
            f.write(''.join(markdown_content))
        
        logging.info(f"Created: {markdown_filename} ({total_images} images)")
        return markdown_path, total_images
    
    except Exception as e:
        logging.error(f"Error processing chunk: {e}")
        # Clean up partial file if it exists
        if markdown_path and os.path.exists(markdown_path):
            try:
                os.remove(markdown_path)
                logging.info(f"Cleaned up partial file: {markdown_path}")
            except OSError:
                pass
        return None, 0


def convert_pdf_to_markdown(
    pdf_path: str,
    overwrite: bool = False,
    enable_detailed_alt_text: bool = True,
    enable_ai_vision: bool = False,
    detail_level: str = "standard",
    output_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Main conversion function with smart chunking, flat output, and detailed alt text.

    Args:
        pdf_path: Path to PDF file
        overwrite: If True, overwrite existing files without warning
        enable_detailed_alt_text: Generate detailed alt text descriptions (default: True)
        enable_ai_vision: Use AI vision analysis for complex images (default: False)
        detail_level: Alt text detail level - 'concise', 'standard', 'verbose' (default: 'standard')
        output_dir: Output directory for markdown and images (default: "outputs")

    Returns:
        dict: Conversion results with keys:
            - success: bool
            - output_dir: str
            - files_created: list
            - images_extracted: int
            - chunked: bool
            - error: str (if failed)
    """
    try:
        # Validate input
        validated_path = validate_pdf_path(pdf_path)

        logging.info(f"Converting PDF: {os.path.basename(validated_path)}")
        logging.info("=" * 60)

        # Analyze PDF
        analysis = analyze_pdf_for_chunking(validated_path)
        logging.info(f"Pages: {analysis['page_count']}, Size: {analysis['file_size_mb']:.2f} MB")

        # Create flat output structure (use specified dir or default "outputs")
        base_output_dir = output_dir if output_dir else "outputs"
        output_dir_path, images_dir = create_flat_output_structure(base_output_dir)
        
        # Check for existing files
        if not overwrite:
            existing = check_existing_output(validated_path, output_dir_path)
            if existing:
                logging.warning(f"Will overwrite {len(existing)} existing file(s)")

        if analysis['chunking_needed']:
            logging.info(
                f"Chunking enabled: {analysis['num_chunks']} parts of "
                f"~{analysis['chunk_size']} pages each"
            )
        else:
            logging.info("Single file processing (no chunking needed)")

        logging.info("-" * 60)

        # Process PDF in chunks
        chunk_files = []
        total_images = 0

        for chunk_num in range(analysis['num_chunks']):
            start_page = chunk_num * analysis['chunk_size']
            end_page = start_page + analysis['chunk_size']

            try:
                if analysis['chunking_needed']:
                    chunk_file, img_count = process_pdf_chunk(
                        validated_path, output_dir_path, images_dir,
                        start_page, end_page, chunk_num + 1,
                        enable_detailed_alt_text=enable_detailed_alt_text,
                        enable_ai_vision=enable_ai_vision,
                        detail_level=detail_level
                    )
                else:
                    chunk_file, img_count = process_pdf_chunk(
                        validated_path, output_dir_path, images_dir,
                        start_page, end_page, None,
                        enable_detailed_alt_text=enable_detailed_alt_text,
                        enable_ai_vision=enable_ai_vision,
                        detail_level=detail_level
                    )

                if chunk_file:
                    chunk_files.append(chunk_file)
                    total_images += img_count
                else:
                    logging.warning(f"Failed to process chunk {chunk_num + 1}")

            except Exception as e:
                logging.error(f"Error processing chunk {chunk_num + 1}: {e}")
                continue

        # Verify we have successful chunks
        if not chunk_files:
            raise RuntimeError("No chunks were successfully processed")

        # Create master index if chunked
        if analysis['chunking_needed'] and chunk_files:
            try:
                create_master_index(validated_path, output_dir_path, chunk_files, analysis)
            except Exception as e:
                logging.warning(f"Failed to create master index: {e}")

        logging.info("=" * 60)
        logging.info(f"Conversion complete!")
        logging.info(f"Files created: {len(chunk_files)}")
        logging.info(f"Images extracted: {total_images}")
        logging.info(f"Output location: {output_dir_path}")

        return {
            'success': True,
            'output_dir': output_dir_path,
            'files_created': chunk_files,
            'images_extracted': total_images,
            'chunked': analysis['chunking_needed']
        }
    
    except Exception as e:
        logging.error(f"Conversion failed: {e}")
        return {
            'success': False,
            'error': str(e)
        }


def main() -> None:
    """Main entry point for command-line usage"""
    setup_logging()
    
    try:
        if len(sys.argv) > 1:
            pdf_path = sys.argv[1]
        else:
            # Look for PDFs in inputs directory
            import glob
            pdf_files = glob.glob("inputs/*.pdf")
            
            if not pdf_files:
                logging.error("No PDF file specified and no PDFs found in inputs/ directory")
                logging.info("Usage: python pdf_converter.py <pdf_path>")
                sys.exit(1)
            
            pdf_path = pdf_files[0]
            logging.info(f"No file specified, using: {os.path.basename(pdf_path)}")
        
        result = convert_pdf_to_markdown(pdf_path)
        
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
        sys.exit(1)


if __name__ == "__main__":
    main()
