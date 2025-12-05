#!/usr/bin/env python3
"""
PDF Analysis Script
Analyzes PDF properties to determine if chunking is necessary
"""

import os
import sys

import fitz  # PyMuPDF


def analyze_pdf(pdf_path):
    """Analyze PDF and return properties"""
    if not os.path.exists(pdf_path):
        print(f"Error: PDF file not found: {pdf_path}")
        return None
    
    try:
        # Open the PDF
        doc = fitz.open(pdf_path)
        
        # Get basic properties
        page_count = len(doc)
        file_size = os.path.getsize(pdf_path)
        file_size_mb = file_size / (1024 * 1024)
        
        # Analyze content complexity
        total_text_length = 0
        total_images = 0
        
        print(f"Analyzing PDF: {os.path.basename(pdf_path)}")
        print(f"File size: {file_size_mb:.2f} MB")
        print(f"Total pages: {page_count}")
        print("=" * 50)
        
        # Sample first few pages to estimate complexity
        sample_pages = min(5, page_count)
        for page_num in range(sample_pages):
            page = doc[page_num]
            text = page.get_text()
            images = page.get_images()
            
            total_text_length += len(text)
            total_images += len(images)
            
            print(f"Page {page_num + 1}: {len(text)} chars, {len(images)} images")
        
        doc.close()
        
        # Calculate averages
        avg_text_per_page = total_text_length / sample_pages if sample_pages > 0 else 0
        avg_images_per_page = total_images / sample_pages if sample_pages > 0 else 0
        
        # Estimate total content
        estimated_total_text = avg_text_per_page * page_count
        estimated_total_images = avg_images_per_page * page_count
        
        print("=" * 50)
        print(f"Average text per page: {avg_text_per_page:.0f} characters")
        print(f"Average images per page: {avg_images_per_page:.1f}")
        print(f"Estimated total text: {estimated_total_text:.0f} characters")
        print(f"Estimated total images: {estimated_total_images:.0f}")
        
        # Determine if chunking is needed
        chunking_needed = False
        reasons = []
        
        if page_count > 100:
            chunking_needed = True
            reasons.append(f"High page count ({page_count} pages)")
        
        if file_size_mb > 50:
            chunking_needed = True
            reasons.append(f"Large file size ({file_size_mb:.1f} MB)")
        
        if estimated_total_images > 200:
            chunking_needed = True
            reasons.append(f"Many images ({estimated_total_images:.0f} estimated)")
        
        print("=" * 50)
        if chunking_needed:
            print("CHUNKING RECOMMENDED")
            print("Reasons:")
            for reason in reasons:
                print(f"  - {reason}")
            
            # Calculate chunk size
            if page_count > 100:
                chunk_size = 25
            elif page_count > 50:
                chunk_size = 20
            else:
                chunk_size = 15
            
            num_chunks = (page_count + chunk_size - 1) // chunk_size
            print(f"Suggested chunk size: {chunk_size} pages")
            print(f"Number of chunks: {num_chunks}")
        else:
            print("SINGLE FILE PROCESSING RECOMMENDED")
            print("PDF is manageable size - no chunking needed")
        
        return {
            'page_count': page_count,
            'file_size_mb': file_size_mb,
            'chunking_needed': chunking_needed,
            'chunk_size': chunk_size if chunking_needed else None,
            'num_chunks': num_chunks if chunking_needed else 1,
            'estimated_images': estimated_total_images
        }
        
    except Exception as e:
        print(f"Error analyzing PDF: {e}")
        return None

if __name__ == "__main__":
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdf_path = "inputs/Macroeconomics, Agriculture, and Food Security Part 1 - The Policy Setting.pdf"
    
    result = analyze_pdf(pdf_path)
    if result:
        print("\nAnalysis complete!")