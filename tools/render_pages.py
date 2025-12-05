#!/usr/bin/env python3
"""
Render PDF pages as full-page images for text extraction
"""

import os
import sys

import fitz  # PyMuPDF


def render_pdf_to_images(pdf_path, output_dir="outputs/page_renders", dpi=200):
    """Render each PDF page as a high-quality image"""

    # Get base name for output files
    base_name = os.path.splitext(os.path.basename(pdf_path))[0]

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Open PDF
    doc = fitz.open(pdf_path)

    rendered_images = []

    for page_num in range(len(doc)):
        page = doc[page_num]

        # Render at high DPI for better text quality
        zoom = dpi / 72  # 72 is default DPI
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat, alpha=False)

        # Save as PNG
        output_filename = f"{base_name}_page_{page_num + 1:03d}.png"
        output_path = os.path.join(output_dir, output_filename)
        pix.save(output_path)

        rendered_images.append(output_path)
        print(f"Rendered page {page_num + 1}/{len(doc)}: {output_filename}")

        pix = None  # Free memory

    doc.close()

    print(f"\nRendered {len(rendered_images)} pages to {output_dir}")
    return rendered_images

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python render_pages.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]

    if not os.path.exists(pdf_path):
        print(f"Error: PDF not found: {pdf_path}")
        sys.exit(1)

    render_pdf_to_images(pdf_path)
