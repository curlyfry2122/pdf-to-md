#!/usr/bin/env python3
"""
PDF Quality Analyzer
Diagnose PDFs to determine if they're text-based or image-based
"""

import glob
import os
import sys
from collections import defaultdict

import fitz  # PyMuPDF


def analyze_pdf(pdf_path):
    """
    Analyze a PDF to determine its type and quality
    
    Returns:
        dict: Analysis results
    """
    try:
        doc = fitz.open(pdf_path)
        
        total_pages = len(doc)
        total_text_chars = 0
        total_images = 0
        pages_with_text = 0
        pages_with_images = 0
        
        for page_num in range(total_pages):
            page = doc[page_num]
            
            # Get text
            text = page.get_text()
            char_count = len(text.strip())
            
            if char_count > 0:
                pages_with_text += 1
                total_text_chars += char_count
            
            # Get images
            images = page.get_images()
            image_count = len(images)
            
            if image_count > 0:
                pages_with_images += 1
                total_images += image_count
        
        # Calculate metrics
        avg_chars_per_page = total_text_chars / total_pages if total_pages > 0 else 0
        text_page_ratio = pages_with_text / total_pages if total_pages > 0 else 0
        image_page_ratio = pages_with_images / total_pages if total_pages > 0 else 0
        
        # Determine PDF type
        if avg_chars_per_page < 50 and image_page_ratio > 0.5:
            pdf_type = "IMAGE_BASED"
            needs_ocr = True
        elif avg_chars_per_page < 200 and image_page_ratio > 0.8:
            pdf_type = "MOSTLY_IMAGES"
            needs_ocr = True
        elif avg_chars_per_page > 500:
            pdf_type = "TEXT_BASED"
            needs_ocr = False
        else:
            pdf_type = "MIXED"
            needs_ocr = False
        
        doc.close()
        
        return {
            'filename': os.path.basename(pdf_path),
            'path': pdf_path,
            'total_pages': total_pages,
            'total_text_chars': total_text_chars,
            'total_images': total_images,
            'pages_with_text': pages_with_text,
            'pages_with_images': pages_with_images,
            'avg_chars_per_page': avg_chars_per_page,
            'text_page_ratio': text_page_ratio,
            'image_page_ratio': image_page_ratio,
            'pdf_type': pdf_type,
            'needs_ocr': needs_ocr
        }
    
    except Exception as e:
        return {
            'filename': os.path.basename(pdf_path),
            'path': pdf_path,
            'error': str(e)
        }


def analyze_directory(directory):
    """Analyze all PDFs in a directory"""
    pdf_files = glob.glob(os.path.join(directory, "*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return []
    
    print(f"Found {len(pdf_files)} PDF files in {directory}")
    print("=" * 80)
    print()
    
    results = []
    for pdf_path in sorted(pdf_files):
        print(f"Analyzing: {os.path.basename(pdf_path)}")
        result = analyze_pdf(pdf_path)
        results.append(result)
    
    return results


def print_summary(results):
    """Print summary of analysis results"""
    print()
    print("=" * 80)
    print("ANALYSIS SUMMARY")
    print("=" * 80)
    print()
    
    # Count by type
    type_counts = defaultdict(int)
    needs_ocr = []
    errors = []
    
    for result in results:
        if 'error' in result:
            errors.append(result)
            continue
        
        type_counts[result['pdf_type']] += 1
        
        if result['needs_ocr']:
            needs_ocr.append(result)
    
    # Print type distribution
    print("PDF Type Distribution:")
    for pdf_type, count in sorted(type_counts.items()):
        print(f"  {pdf_type}: {count}")
    
    print()
    
    # Print files needing OCR
    if needs_ocr:
        print(f"Files Requiring OCR ({len(needs_ocr)}):")
        print("-" * 80)
        for result in needs_ocr:
            print(f"\n  {result['filename']}")
            print(f"    Type: {result['pdf_type']}")
            print(f"    Pages: {result['total_pages']}")
            print(f"    Avg chars/page: {result['avg_chars_per_page']:.1f}")
            print(f"    Images: {result['total_images']}")
    else:
        print("No files require OCR conversion")
    
    print()
    
    # Print errors
    if errors:
        print(f"Errors ({len(errors)}):")
        for result in errors:
            print(f"  {result['filename']}: {result['error']}")
        print()
    
    # Print detailed results
    print()
    print("=" * 80)
    print("DETAILED RESULTS")
    print("=" * 80)
    print()
    
    for result in results:
        if 'error' in result:
            continue
        
        print(f"File: {result['filename']}")
        print(f"  Type: {result['pdf_type']}")
        print(f"  Pages: {result['total_pages']}")
        print(f"  Total text chars: {result['total_text_chars']:,}")
        print(f"  Avg chars/page: {result['avg_chars_per_page']:.1f}")
        print(f"  Pages with text: {result['pages_with_text']} ({result['text_page_ratio']:.1%})")
        print(f"  Total images: {result['total_images']}")
        print(f"  Pages with images: {result['pages_with_images']} ({result['image_page_ratio']:.1%})")
        print(f"  Needs OCR: {'YES' if result['needs_ocr'] else 'NO'}")
        print()


def save_report(results, output_file="pdf_analysis_report.txt"):
    """Save analysis report to file"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("PDF Analysis Report\n")
        f.write("=" * 80 + "\n\n")
        
        for result in results:
            if 'error' in result:
                f.write(f"File: {result['filename']}\n")
                f.write(f"  ERROR: {result['error']}\n\n")
                continue
            
            f.write(f"File: {result['filename']}\n")
            f.write(f"  Type: {result['pdf_type']}\n")
            f.write(f"  Pages: {result['total_pages']}\n")
            f.write(f"  Total text chars: {result['total_text_chars']:,}\n")
            f.write(f"  Avg chars/page: {result['avg_chars_per_page']:.1f}\n")
            f.write(f"  Pages with text: {result['pages_with_text']} ({result['text_page_ratio']:.1%})\n")
            f.write(f"  Total images: {result['total_images']}\n")
            f.write(f"  Pages with images: {result['pages_with_images']} ({result['image_page_ratio']:.1%})\n")
            f.write(f"  Needs OCR: {'YES' if result['needs_ocr'] else 'NO'}\n")
            f.write("\n")
    
    print(f"Report saved to: {output_file}")


def main():
    """Main entry point"""
    if len(sys.argv) > 1:
        directory = sys.argv[1]
    else:
        directory = "inputs"
    
    if not os.path.exists(directory):
        print(f"Directory not found: {directory}")
        sys.exit(1)
    
    results = analyze_directory(directory)
    
    if results:
        print_summary(results)
        save_report(results)


if __name__ == "__main__":
    main()
