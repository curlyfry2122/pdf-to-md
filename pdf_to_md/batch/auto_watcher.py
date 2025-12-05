#!/usr/bin/env python3
"""
Automatic PDF Converter with File Watching
Monitors inputs/ folder and automatically converts new PDFs to markdown
"""

import logging
import os
import shutil
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Set

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    print("Warning: watchdog package not found. Install with: pip install watchdog")
    print("Running in one-time scan mode instead.\n")

from pdf_to_md.core.converter_lib import setup_logging
from pdf_to_md.core.pdf_converter import convert_pdf_to_markdown


class PDFHandler(FileSystemEventHandler):
    """Handler for PDF file events"""
    
    def __init__(self, archive_dir="archive"):
        super().__init__()
        self.archive_dir = archive_dir
        self.processing = set()  # Track files being processed
        
        # Create archive directory if it doesn't exist
        os.makedirs(archive_dir, exist_ok=True)
        
        # Create timestamped subdirectory for this session
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.session_archive = os.path.join(archive_dir, timestamp)
        os.makedirs(self.session_archive, exist_ok=True)
        logging.info(f"Archive directory: {self.session_archive}")
    
    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return
        
        if event.src_path.lower().endswith('.pdf'):
            # Small delay to ensure file is fully written
            time.sleep(1)
            self.process_pdf(event.src_path)
    
    def on_moved(self, event):
        """Handle file move events (e.g., drag and drop)"""
        if event.is_directory:
            return
        
        if event.dest_path.lower().endswith('.pdf'):
            time.sleep(1)
            self.process_pdf(event.dest_path)
    
    def process_pdf(self, pdf_path):
        """Process a single PDF file"""
        # Avoid processing the same file multiple times
        if pdf_path in self.processing:
            return
        
        # Check if file still exists (may have been moved/deleted)
        if not os.path.exists(pdf_path):
            return
        
        self.processing.add(pdf_path)
        
        try:
            filename = os.path.basename(pdf_path)
            logging.info(f"\n{'=' * 60}")
            logging.info(f"NEW FILE DETECTED: {filename}")
            logging.info(f"{'=' * 60}")
            
            # Convert PDF
            result = convert_pdf_to_markdown(pdf_path)
            
            if result.get('success', False):
                logging.info(f"\n✓ Successfully converted: {filename}")
                logging.info(f"  - Files created: {len(result['files_created'])}")
                logging.info(f"  - Images extracted: {result['images_extracted']}")
                
                # Archive the PDF
                self.archive_pdf(pdf_path)
            else:
                error_msg = result.get('error', 'Unknown error')
                logging.error(f"\n✗ Failed to convert: {filename}")
                logging.error(f"  Error: {error_msg}")
        
        except Exception as e:
            logging.error(f"Error processing {pdf_path}: {e}")
        
        finally:
            self.processing.discard(pdf_path)
    
    def archive_pdf(self, pdf_path):
        """Move processed PDF to archive directory"""
        try:
            filename = os.path.basename(pdf_path)
            archive_path = os.path.join(self.session_archive, filename)
            
            # If file already exists in archive, add timestamp
            if os.path.exists(archive_path):
                base, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%H%M%S')
                filename = f"{base}_{timestamp}{ext}"
                archive_path = os.path.join(self.session_archive, filename)
            
            shutil.move(pdf_path, archive_path)
            logging.info(f"  - Archived to: {archive_path}")
        
        except Exception as e:
            logging.warning(f"Could not archive {pdf_path}: {e}")


def scan_and_convert_existing(inputs_dir="inputs", archive_dir="archive"):
    """
    Scan inputs directory and convert any existing PDFs
    
    Args:
        inputs_dir: Directory to scan for PDFs
        archive_dir: Directory to archive processed PDFs
    """
    if not os.path.exists(inputs_dir):
        logging.error(f"Inputs directory not found: {inputs_dir}")
        return
    
    # Find all PDF files
    pdf_files = [f for f in os.listdir(inputs_dir) if f.lower().endswith('.pdf')]
    
    if not pdf_files:
        logging.info(f"No PDFs found in {inputs_dir}")
        return
    
    logging.info(f"Found {len(pdf_files)} existing PDF(s) to convert")
    
    # Create archive handler for moving files
    handler = PDFHandler(archive_dir)
    
    # Process each PDF
    for pdf_file in pdf_files:
        pdf_path = os.path.join(inputs_dir, pdf_file)
        handler.process_pdf(pdf_path)


def watch_directory(inputs_dir="inputs", archive_dir="archive"):
    """
    Watch directory for new PDFs and automatically convert them
    
    Args:
        inputs_dir: Directory to watch for new PDFs
        archive_dir: Directory to archive processed PDFs
    """
    if not WATCHDOG_AVAILABLE:
        logging.error("Watchdog package required for file watching")
        logging.info("Install with: pip install watchdog")
        return False
    
    if not os.path.exists(inputs_dir):
        os.makedirs(inputs_dir)
        logging.info(f"Created inputs directory: {inputs_dir}")
    
    # First, process any existing PDFs
    scan_and_convert_existing(inputs_dir, archive_dir)
    
    # Set up file watcher
    event_handler = PDFHandler(archive_dir)
    observer = Observer()
    observer.schedule(event_handler, inputs_dir, recursive=False)
    observer.start()
    
    logging.info(f"\n{'=' * 60}")
    logging.info(f"WATCHING: {os.path.abspath(inputs_dir)}")
    logging.info(f"Drop PDF files into this folder for automatic conversion")
    logging.info(f"Press Ctrl+C to stop")
    logging.info(f"{'=' * 60}\n")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("\nStopping file watcher...")
        observer.stop()
    
    observer.join()
    return True


def main():
    """Main entry point"""
    # Setup logging
    log_file = os.path.join("outputs", "auto_convert.log")
    setup_logging(log_file=log_file)
    
    logging.info("=" * 60)
    logging.info("PDF Auto-Converter")
    logging.info("=" * 60)
    logging.info("Detailed alt text: ENABLED (pattern-based + context-aware)")
    
    inputs_dir = "inputs"
    archive_dir = "archive"
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--scan":
            # One-time scan mode
            logging.info("Running in one-time scan mode")
            scan_and_convert_existing(inputs_dir, archive_dir)
            return
        elif sys.argv[1] == "--help":
            print("PDF Auto-Converter")
            print("\nUsage:")
            print("  python auto_convert.py          # Watch for new PDFs continuously")
            print("  python auto_convert.py --scan   # Convert existing PDFs once and exit")
            print("  python auto_convert.py --help   # Show this help")
            print("\nFeatures:")
            print("  - Automatically converts PDFs dropped in inputs/ folder")
            print("  - Archives processed PDFs to archive/ with timestamps")
            print("  - Logs all conversions to outputs/auto_convert.log")
            print("\nRequirements:")
            print("  - watchdog package (for continuous watching)")
            print("    Install with: pip install watchdog")
            return
    
    # Default: watch mode
    if WATCHDOG_AVAILABLE:
        success = watch_directory(inputs_dir, archive_dir)
        if not success:
            logging.error("Failed to start file watcher")
            sys.exit(1)
    else:
        logging.info("Watchdog not available, running one-time scan instead")
        scan_and_convert_existing(inputs_dir, archive_dir)
        logging.info("\nTo enable continuous watching, install watchdog:")
        logging.info("  pip install watchdog")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.error(f"Fatal error: {e}")
        sys.exit(1)
