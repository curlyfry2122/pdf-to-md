#!/usr/bin/env python3
"""
Markdown Simplification Script
Simplifies markdown files by:
- Replacing image references with descriptive alt text
- Replacing complex tables (>10 rows) with summaries
- Keeping simple tables (≤10 rows) intact
"""

import os
import re
import sys
from typing import List, Tuple


class MarkdownSimplifier:
    def __init__(self, input_file: str, output_file: str = None):
        self.input_file = input_file
        self.output_file = output_file or self._generate_output_filename(input_file)
        self.lines = []
        self.current_context = {
            'last_header': '',
            'page_number': 0
        }

    def _generate_output_filename(self, input_file: str) -> str:
        """Generate output filename by adding _simplified suffix"""
        base, ext = os.path.splitext(input_file)
        return f"{base}_simplified{ext}"

    def read_file(self):
        """Read the input markdown file"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            self.lines = f.readlines()
        print(f"Read {len(self.lines)} lines from {self.input_file}")

    def write_file(self, processed_lines: List[str]):
        """Write the processed content to output file"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            f.writelines(processed_lines)
        print(f"Wrote {len(processed_lines)} lines to {self.output_file}")

    def detect_image_reference(self, line: str) -> Tuple[bool, dict]:
        """Detect if a line contains an image reference"""
        # Pattern: ![Image from page X](images/filename.png)
        pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
        match = re.search(pattern, line)
        if match:
            return True, {
                'alt_text': match.group(1),
                'image_path': match.group(2),
                'full_match': match.group(0)
            }
        return False, {}

    def generate_image_description(self, image_info: dict, context: dict) -> str:
        """Generate a descriptive alt text for an image based on context"""
        # Extract page number from image path if available
        page_match = re.search(r'page_(\d+)', image_info['image_path'])
        page_num = page_match.group(1) if page_match else 'unknown'

        # Use context to generate better descriptions
        header = context.get('last_header', '').lower()

        # Infer chart type from context
        if 'price' in header or 'market' in header:
            chart_type = 'Price trend chart'
        elif 'production' in header or 'supply' in header:
            chart_type = 'Production/supply chart'
        elif 'map' in header or 'condition' in header or 'crop' in header:
            chart_type = 'Geographic/crop condition map'
        elif 'outlook' in header or 'forecast' in header:
            chart_type = 'Forecast/outlook chart'
        elif 'volatility' in header:
            chart_type = 'Volatility chart'
        else:
            chart_type = 'Chart/Figure'

        # Generate description
        if context.get('last_header'):
            description = f"[{chart_type} from page {page_num}: Related to {context['last_header']}]"
        else:
            description = f"[{chart_type} from page {page_num}]"

        return description

    def is_table_row(self, line: str) -> bool:
        """Detect if a line appears to be part of a data table"""
        line = line.strip()
        if not line:
            return False

        # Check for multiple numbers or aligned columns
        # Tables typically have multiple spaces between words/numbers
        has_multiple_spaces = '  ' in line or '\t' in line

        # Count numeric characters
        digit_count = sum(c.isdigit() or c == '.' for c in line)

        # If line has multiple spaces and significant numeric content, likely a table
        if has_multiple_spaces and digit_count > 5:
            return True

        # Also check for common table indicators
        if any(indicator in line.lower() for indicator in ['prod.', 'supply', 'utiliz.', 'trade', 'stocks']):
            if digit_count > 3:
                return True

        return False

    def detect_and_process_table(self, lines: List[str], start_idx: int) -> Tuple[int, List[str], bool]:
        """
        Detect a table starting at start_idx and process it
        Returns: (end_idx, processed_lines, was_summarized)
        """
        table_lines = []
        idx = start_idx

        # Collect consecutive table rows
        while idx < len(lines) and self.is_table_row(lines[idx]):
            table_lines.append(lines[idx])
            idx += 1

        if not table_lines:
            return start_idx, [], False

        # Determine if table should be kept or summarized
        row_count = len(table_lines)

        if row_count <= 10:
            # Keep small tables
            return idx, table_lines, False
        else:
            # Summarize large tables
            # Try to extract table context from first few lines
            first_line = table_lines[0].strip()

            # Generate summary
            summary = f"\n[Data Table: {row_count} rows of detailed data"

            # Try to infer table content from context
            if self.current_context.get('last_header'):
                summary += f" - {self.current_context['last_header']}"

            summary += "]\n\n"

            return idx, [summary], True

    def update_context(self, line: str):
        """Update context information from the current line"""
        # Detect headers
        if line.startswith('#'):
            header_text = re.sub(r'^#+\s*', '', line).strip()
            self.current_context['last_header'] = header_text

            # Extract page number if it's a page header
            page_match = re.search(r'Page\s+(\d+)', header_text)
            if page_match:
                self.current_context['page_number'] = int(page_match.group(1))

    def process(self):
        """Main processing function"""
        print("Processing markdown file...")

        processed_lines = []
        i = 0

        images_replaced = 0
        tables_summarized = 0
        tables_kept = 0

        while i < len(self.lines):
            line = self.lines[i]

            # Update context
            self.update_context(line)

            # Check for image references
            is_image, image_info = self.detect_image_reference(line)
            if is_image:
                # Replace with descriptive text
                description = self.generate_image_description(image_info, self.current_context)
                new_line = line.replace(image_info['full_match'], description)
                processed_lines.append(new_line)
                images_replaced += 1
                i += 1
                continue

            # Check for table start
            if self.is_table_row(line):
                end_idx, table_output, was_summarized = self.detect_and_process_table(self.lines, i)
                processed_lines.extend(table_output)
                if was_summarized:
                    tables_summarized += 1
                else:
                    tables_kept += 1
                i = end_idx
                continue

            # Regular line - keep as is
            processed_lines.append(line)
            i += 1

        print(f"\nProcessing complete:")
        print(f"  - Images replaced with descriptions: {images_replaced}")
        print(f"  - Large tables summarized: {tables_summarized}")
        print(f"  - Small tables kept intact: {tables_kept}")

        return processed_lines

    def simplify(self):
        """Main entry point for simplification"""
        self.read_file()
        processed_lines = self.process()
        self.write_file(processed_lines)
        print(f"\nSimplification complete! Output saved to: {self.output_file}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python simplify_markdown.py <input_markdown_file> [output_file]")
        print("\nExample: python simplify_markdown.py outputs/AMIS_Market_Monitor_current.md")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)

    simplifier = MarkdownSimplifier(input_file, output_file)
    simplifier.simplify()

if __name__ == "__main__":
    main()
