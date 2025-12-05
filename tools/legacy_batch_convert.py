#!/usr/bin/env python3
"""
Batch PDF Converter
Process all PDFs in inputs folder using the unified converter
"""

import glob
import logging
import os
import sys
from datetime import datetime

from pdf_converter import convert_pdf_to_markdown
from pdf_to_md.utils.converter_lib import format_file_size, setup_logging


def batch_convert_pdfs(inputs_dir="inputs"):
    """
    Convert all PDFs in the specified directory
    
    Args:
        inputs_dir: Directory containing PDFs to convert
        
    Returns:
        list: Conversion results for each PDF
    """
    logging.info("=" * 60)
    logging.info("BATCH PDF TO MARKDOWN CONVERSION")
    logging.info("=" * 60)
    logging.info(f"Source directory: {inputs_dir}")
    logging.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logging.info(f"Detailed alt text: ENABLED (pattern-based + context-aware)")
    logging.info("")
    
    # Find all PDF files
    pdf_pattern = os.path.join(inputs_dir, "*.pdf")
    pdf_files = glob.glob(pdf_pattern)
    
    if not pdf_files:
        logging.error(f"No PDF files found in {inputs_dir}")
        return []
    
    logging.info(f"Found {len(pdf_files)} PDF file(s) to convert:")
    for i, pdf_file in enumerate(pdf_files, 1):
        file_size = os.path.getsize(pdf_file)
        logging.info(f"  {i:2d}. {os.path.basename(pdf_file)} ({format_file_size(file_size)})")
    logging.info("")
    
    # Convert each PDF
    results = []
    successful = 0
    failed = 0
    total_files_created = 0
    total_images_extracted = 0
    
    for i, pdf_file in enumerate(pdf_files, 1):
        logging.info(f"\n[{i}/{len(pdf_files)}] Converting: {os.path.basename(pdf_file)}")
        logging.info("-" * 40)
        
        try:
            result = convert_pdf_to_markdown(pdf_file)
            
            if result.get('success', False):
                results.append({
                    'pdf_file': pdf_file,
                    'result': result,
                    'status': 'success'
                })
                successful += 1
                total_files_created += len(result['files_created'])
                total_images_extracted += result['images_extracted']
                
                logging.info(f"✓ Success: {len(result['files_created'])} file(s), {result['images_extracted']} images")
            else:
                results.append({
                    'pdf_file': pdf_file,
                    'result': result,
                    'status': 'failed'
                })
                failed += 1
                error = result.get('error', 'Unknown error')
                logging.error(f"✗ Failed: {error}")
        
        except Exception as e:
            results.append({
                'pdf_file': pdf_file,
                'result': None,
                'status': 'error',
                'error': str(e)
            })
            failed += 1
            logging.error(f"✗ Error: {e}")
    
    # Print summary
    logging.info("\n" + "=" * 60)
    logging.info("BATCH CONVERSION SUMMARY")
    logging.info("=" * 60)
    logging.info(f"Total PDFs processed: {len(pdf_files)}")
    logging.info(f"Successful: {successful}")
    logging.info(f"Failed: {failed}")
    logging.info(f"Success rate: {(successful/len(pdf_files)*100):.1f}%")
    logging.info(f"Total markdown files: {total_files_created}")
    logging.info(f"Total images extracted: {total_images_extracted}")
    logging.info(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if successful > 0:
        logging.info(f"\nSuccessful conversions:")
        for result in results:
            if result['status'] == 'success':
                pdf_name = os.path.basename(result['pdf_file'])
                file_count = len(result['result']['files_created'])
                img_count = result['result']['images_extracted']
                chunked = " (chunked)" if result['result']['chunked'] else ""
                logging.info(f"  ✓ {pdf_name} → {file_count} file(s), {img_count} images{chunked}")
    
    if failed > 0:
        logging.info(f"\nFailed conversions:")
        for result in results:
            if result['status'] in ['failed', 'error']:
                pdf_name = os.path.basename(result['pdf_file'])
                if 'error' in result:
                    logging.info(f"  ✗ {pdf_name} ({result['error']})")
                else:
                    logging.info(f"  ✗ {pdf_name}")
    
    return results


def create_summary_report(results, output_file="outputs/batch_summary.md"):
    """
    Create a markdown summary report of batch conversion
    
    Args:
        results: List of conversion results
        output_file: Path to output summary file
    """
    os.makedirs("outputs", exist_ok=True)
    
    total_pdfs = len(results)
    successful = len([r for r in results if r['status'] == 'success'])
    failed = total_pdfs - successful
    total_files = sum(len(r['result']['files_created']) for r in results if r['status'] == 'success')
    total_images = sum(r['result']['images_extracted'] for r in results if r['status'] == 'success')
    
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Batch PDF to Markdown Conversion Summary\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        f.write("## Overview\n\n")
        f.write(f"- **Total PDFs:** {total_pdfs}\n")
        f.write(f"- **Successful:** {successful}\n")
        f.write(f"- **Failed:** {failed}\n")
        f.write(f"- **Success Rate:** {(successful/total_pdfs*100):.1f}%\n")
        f.write(f"- **Total Markdown Files:** {total_files}\n")
        f.write(f"- **Total Images:** {total_images}\n\n")
        
        f.write("## Output Structure\n\n")
        f.write("All outputs saved in flat structure:\n\n")
        f.write("- **Markdown files:** `outputs/*.md`\n")
        f.write("- **Images:** `outputs/images/*.png`\n")
        f.write("- **Large documents:** Split into parts with INDEX file\n\n")
        
        if successful > 0:
            f.write("## Successful Conversions\n\n")
            for result in results:
                if result['status'] == 'success':
                    pdf_name = os.path.basename(result['pdf_file'])
                    file_count = len(result['result']['files_created'])
                    img_count = result['result']['images_extracted']
                    chunked = result['result']['chunked']
                    
                    f.write(f"### {pdf_name}\n\n")
                    f.write(f"- Files created: {file_count}\n")
                    f.write(f"- Images extracted: {img_count}\n")
                    f.write(f"- Chunked: {'Yes' if chunked else 'No'}\n")
                    f.write(f"- Status: ✅ Success\n\n")
        
        if failed > 0:
            f.write("## Failed Conversions\n\n")
            for result in results:
                if result['status'] in ['failed', 'error']:
                    pdf_name = os.path.basename(result['pdf_file'])
                    f.write(f"### {pdf_name}\n\n")
                    f.write(f"- Status: ❌ Failed\n")
                    if 'error' in result:
                        f.write(f"- Error: {result['error']}\n")
                    f.write("\n")
    
    logging.info(f"\nSummary report saved: {output_file}")


def main():
    """Main entry point"""
    setup_logging()
    
    inputs_dir = "inputs"
    
    # Verify directory exists
    if not os.path.exists(inputs_dir):
        logging.error(f"Directory not found: {inputs_dir}")
        sys.exit(1)
    
    # Run batch conversion
    results = batch_convert_pdfs(inputs_dir)
    
    if results:
        # Create summary report
        create_summary_report(results)
        logging.info("\nAll outputs saved in 'outputs/' directory")
        logging.info("  - Markdown files: outputs/*.md")
        logging.info("  - Images: outputs/images/")
    else:
        logging.error("No files were processed")
        sys.exit(1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logging.info("\nBatch conversion interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
