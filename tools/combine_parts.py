#!/usr/bin/env python3
"""Combine chunked markdown files into single files"""

import os
import re


def combine_parts(base_name, num_parts, output_dir="outputs"):
    """Combine multiple parts into a single markdown file"""

    # Read all parts
    combined_content = []

    for i in range(1, num_parts + 1):
        part_file = os.path.join(output_dir, f"{base_name}_part_{i:02d}.md")

        if not os.path.exists(part_file):
            print(f"Warning: {part_file} not found, skipping...")
            continue

        print(f"Reading {part_file}...")
        with open(part_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # For first part, keep everything
        if i == 1:
            combined_content.append(content)
        else:
            # For subsequent parts, remove the header (first 4 lines typically)
            lines = content.split('\n')
            # Skip lines until we find the first "## Page" marker
            start_idx = 0
            for idx, line in enumerate(lines):
                if line.startswith('## Page'):
                    start_idx = idx
                    break

            # Join from the page marker onwards
            combined_content.append('\n'.join(lines[start_idx:]))

    # Combine all parts
    full_content = '\n\n'.join(combined_content)

    # Clean up the title - use just the base name without "part" references
    # Replace the first line with a clean title
    lines = full_content.split('\n')
    lines[0] = f"# {base_name.replace('_', ' ')}"
    full_content = '\n'.join(lines)

    # Write combined file
    output_file = os.path.join(output_dir, f"{base_name}.md")
    print(f"Writing combined file to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(full_content)

    print(f"Successfully combined {num_parts} parts into {output_file}")
    return output_file

if __name__ == "__main__":
    # Combine Food Outlook (5 parts)
    combine_parts("Food_Outlook_20251016", 5)

    # Combine Oil 2025 (7 parts)
    combine_parts("Oil_2025___Annual_Oil_Market_Analysis_20251016", 7)

    # Combine World Economic Outlook (8 parts)
    combine_parts("World_Economic_Outlook_20251016", 8)

    print("\nAll files combined successfully!")
