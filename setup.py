#!/usr/bin/env python3
"""
Setup configuration for pdf-to-md package
"""

from pathlib import Path

from setuptools import find_packages, setup

# Read long description from README if it exists
readme_file = Path(__file__).parent / "README.md"
long_description = ""
if readme_file.exists():
    long_description = readme_file.read_text(encoding="utf-8")

# Read requirements from requirements.txt
requirements_file = Path(__file__).parent / "requirements.txt"
install_requires = []
if requirements_file.exists():
    with open(requirements_file, 'r', encoding='utf-8') as f:
        install_requires = [
            line.strip()
            for line in f
            if line.strip() and not line.startswith('#')
        ]

setup(
    name="pdf-to-md",
    version="0.1.0",
    description="PDF and DOCX to Markdown converter with detailed alt text support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="",
    author_email="",
    url="",
    packages=find_packages(exclude=["tests", "tests.*", "archive", "archive.*"]),
    install_requires=install_requires,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pylint>=2.15.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
            "bandit>=1.7.0",
        ],
        "ocr": [
            "easyocr>=1.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "pdf2md=pdf_to_md.cli.pdf2md:main",
            "docx2md=pdf_to_md.cli.docx2md:main",
            "batch-convert=pdf_to_md.batch.batch_processor:main",
            "auto-convert=pdf_to_md.batch.auto_watcher:main",
        ],
    },
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Text Processing :: Markup :: Markdown",
        "Topic :: Utilities",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="pdf markdown converter docx alt-text accessibility",
    project_urls={
        "Bug Reports": "",
        "Source": "",
    },
)
