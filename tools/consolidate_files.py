#!/usr/bin/env python3
"""
Consolidate all markdown files and images into a single folder
"""

import glob
import os
import re
import shutil
from pathlib import Path


def consolidate_subject_matter_files():
    """Consolidate all markdown files and images into one folder"""
    
    # Define paths
    outputs_dir = "outputs"
    consolidated_dir = os.path.join(outputs_dir, "Subject_Matter_Context_Consolidated")
    consolidated_images_dir = os.path.join(consolidated_dir, "images")
    
    # Ensure consolidated directories exist
    os.makedirs(consolidated_dir, exist_ok=True)
    os.makedirs(consolidated_images_dir, exist_ok=True)
    
    print("Consolidating Subject Matter Context Files")
    print("=" * 50)
    
    # Get all subdirectories in outputs (except the consolidated one)
    subdirs = [d for d in os.listdir(outputs_dir) 
               if os.path.isdir(os.path.join(outputs_dir, d)) 
               and d != "Subject_Matter_Context_Consolidated"]
    
    markdown_files_copied = 0
    images_copied = 0
    
    for subdir in subdirs:
        subdir_path = os.path.join(outputs_dir, subdir)
        print(f"\nProcessing: {subdir}")
        
        # Find markdown files in this subdirectory
        md_files = glob.glob(os.path.join(subdir_path, "*.md"))
        
        for md_file in md_files:
            # Skip index files
            if "_INDEX.md" in md_file:
                continue
                
            filename = os.path.basename(md_file)
            dest_path = os.path.join(consolidated_dir, filename)
            
            # Read the markdown file
            with open(md_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Update image paths from "images/filename" to "images/subdir_filename"
            # This prevents image name conflicts between different documents
            images_dir = os.path.join(subdir_path, "images")
            if os.path.exists(images_dir):
                # Get all images in this subdirectory
                image_files = glob.glob(os.path.join(images_dir, "*"))
                
                for image_file in image_files:
                    image_filename = os.path.basename(image_file)
                    # Create unique image name with prefix
                    safe_subdir = re.sub(r'[^a-zA-Z0-9_-]', '_', subdir)
                    new_image_name = f"{safe_subdir}_{image_filename}"
                    
                    # Copy image to consolidated images folder
                    dest_image_path = os.path.join(consolidated_images_dir, new_image_name)
                    shutil.copy2(image_file, dest_image_path)
                    images_copied += 1
                    
                    # Update markdown content to reference new image path
                    old_path = f"images/{image_filename}"
                    new_path = f"images/{new_image_name}"
                    content = content.replace(old_path, new_path)
            
            # Write updated markdown file to consolidated directory
            with open(dest_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            markdown_files_copied += 1
            print(f"  + Copied: {filename}")
    
    print("\n" + "=" * 50)
    print("CONSOLIDATION COMPLETE")
    print("=" * 50)
    print(f"Markdown files copied: {markdown_files_copied}")
    print(f"Images copied: {images_copied}")
    print(f"Consolidated location: {consolidated_dir}")
    
    # List all files in consolidated directory
    print(f"\nFiles in consolidated directory:")
    md_files = glob.glob(os.path.join(consolidated_dir, "*.md"))
    for md_file in sorted(md_files):
        print(f"  - {os.path.basename(md_file)}")
    
    return consolidated_dir, markdown_files_copied, images_copied

if __name__ == "__main__":
    consolidate_subject_matter_files()