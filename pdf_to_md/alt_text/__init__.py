"""
Alt text pattern recognition for detailed image descriptions
"""

try:
    from pdf_to_md.alt_text.patterns import get_recognizer
    __all__ = ["get_recognizer"]
except ImportError:
    __all__ = []
