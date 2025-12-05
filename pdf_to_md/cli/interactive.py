"""Interactive CLI utilities for pdf-to-md converters."""

import os
import sys
from pathlib import Path
from typing import List, Optional, Tuple

from pdf_to_md.core.converter_lib import format_file_size


def list_available_files(directory: str, extensions: List[str]) -> List[Tuple[str, int]]:
    """
    List files matching extensions in a directory.

    Args:
        directory: Directory to search
        extensions: List of extensions (e.g., ['.pdf', '.PDF'])

    Returns:
        List of (filepath, size_bytes) tuples, sorted by name
    """
    files = []
    dir_path = Path(directory)

    if not dir_path.exists():
        return files

    for ext in extensions:
        for filepath in dir_path.glob(f"*{ext}"):
            if filepath.is_file():
                files.append((str(filepath), filepath.stat().st_size))

    # Sort by filename
    files.sort(key=lambda x: Path(x[0]).name.lower())
    return files


def display_file_menu(files: List[Tuple[str, int]]) -> None:
    """Display numbered menu of available files."""
    print("\nAvailable files:")
    for i, (filepath, size) in enumerate(files, 1):
        name = Path(filepath).name
        size_str = format_file_size(size)
        print(f"  [{i}] {name} ({size_str})")
    print()


def prompt_for_file(
    file_type: str,
    extensions: List[str],
    default_dir: str = "inputs"
) -> Optional[str]:
    """
    Prompt user to select or enter a file path.

    Args:
        file_type: Description of file type (e.g., "PDF", "Word document")
        extensions: List of valid extensions
        default_dir: Default directory to search for files

    Returns:
        Selected file path, or None if cancelled
    """
    # Check for available files in default directory
    available = list_available_files(default_dir, extensions)

    if available:
        display_file_menu(available)
        prompt = f"Enter {file_type} path or number"
        if len(available) == 1:
            prompt += " [1]"
        prompt += ": "
    else:
        print(f"\nNo {file_type} files found in {default_dir}/")
        prompt = f"Enter {file_type} path: "

    try:
        user_input = input(prompt).strip()
    except (KeyboardInterrupt, EOFError):
        print("\nCancelled.")
        return None

    # Handle empty input with default
    if not user_input and available:
        user_input = "1"

    # Check if input is a number (selecting from menu)
    if user_input.isdigit():
        idx = int(user_input) - 1
        if 0 <= idx < len(available):
            return available[idx][0]
        else:
            print(f"Invalid selection. Please enter 1-{len(available)}.")
            return None

    # Treat as file path
    if user_input:
        # Expand user path and resolve
        filepath = Path(user_input).expanduser()
        if filepath.exists():
            return str(filepath.resolve())
        else:
            print(f"File not found: {user_input}")
            return None

    return None


def print_header(title: str) -> None:
    """Print a formatted header."""
    print(f"\n{title}")
    print("-" * len(title))


def print_success(result: dict, file_type: str = "document") -> None:
    """
    Print formatted success message with output details.

    Args:
        result: Conversion result dictionary
        file_type: Type of file converted
    """
    if not result.get('success'):
        print(f"\nConversion failed: {result.get('error', 'Unknown error')}")
        return

    print("\n" + "=" * 40)
    print("Conversion complete!")
    print("=" * 40)

    # Show created files
    files_created = result.get('files_created', [])
    if files_created:
        print("\nOutput files:")
        for f in files_created:
            print(f"  {f}")

    # Show image count
    images = result.get('images_extracted', 0)
    if images:
        print(f"\nImages extracted: {images}")
        output_dir = result.get('output_dir', 'outputs')
        print(f"  Location: {output_dir}/images/")

    # Note if document was chunked
    if result.get('chunked'):
        print(f"\nNote: Large {file_type} was split into multiple parts.")
        print("  See *_INDEX.md for the master index.")


def print_progress(message: str, end: str = "\n") -> None:
    """Print a progress message."""
    print(f"  {message}", end=end, flush=True)
