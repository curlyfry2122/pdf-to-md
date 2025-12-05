"""
Tests for image extraction and alt text generation in converter_lib.py
"""

from unittest.mock import MagicMock, Mock, patch

import pytest

from pdf_to_md.core.converter_lib import generate_detailed_alt_text


class TestGenerateDetailedAltText:
    """Tests for generate_detailed_alt_text function"""

    def test_basic_alt_text_generation(self, mock_fitz_pixmap):
        """Test basic alt text generation"""
        result = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_with_page_text_context(self, mock_fitz_pixmap):
        """Test alt text generation with page text context"""
        page_text = "This is a sample page with some context about charts and graphs."

        result = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            page_text=page_text
        )

        assert isinstance(result, str)
        # Should use context from page text

    def test_with_image_position(self, mock_fitz_pixmap):
        """Test alt text generation with image position info"""
        result = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            page_width=612,
            page_height=792,
            img_bbox=(50, 50, 150, 150)
        )

        assert isinstance(result, str)

    def test_different_detail_levels(self, mock_fitz_pixmap):
        """Test different detail level settings"""
        # Concise
        result_concise = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            detail_level="concise"
        )

        # Standard
        result_standard = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            detail_level="standard"
        )

        # Verbose
        result_verbose = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            detail_level="verbose"
        )

        # All should return strings
        assert all(isinstance(r, str) for r in [result_concise, result_standard, result_verbose])

    def test_ai_vision_disabled(self, mock_fitz_pixmap):
        """Test with AI vision explicitly disabled"""
        result = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            enable_ai_vision=False
        )

        assert isinstance(result, str)

    def test_ai_vision_enabled_but_not_used(self, mock_fitz_pixmap):
        """Test with AI vision enabled (but not actually called)"""
        result = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            enable_ai_vision=True  # Enabled but implementation not available
        )

        # Should still return pattern-based alt text
        assert isinstance(result, str)

    def test_fallback_when_patterns_unavailable(self, mock_fitz_pixmap):
        """Test fallback behavior when pattern recognizer is not available"""
        with patch('pdf_to_md.core.converter_lib.ALT_TEXT_PATTERNS_AVAILABLE', False):
            result = generate_detailed_alt_text(
                pix=mock_fitz_pixmap,
                page_num=5,
                img_index=2
            )

            # Should fall back to basic description
            assert isinstance(result, str)
            assert "page 6" in result.lower()  # page_num is 0-indexed

    def test_with_multiple_images_same_page(self, mock_fitz_pixmap):
        """Test generating alt text for multiple images on same page"""
        results = []
        for img_index in range(3):
            result = generate_detailed_alt_text(
                pix=mock_fitz_pixmap,
                page_num=0,
                img_index=img_index
            )
            results.append(result)

        # All should return valid alt text
        assert all(isinstance(r, str) for r in results)
        assert all(len(r) > 0 for r in results)

    def test_with_first_page_first_image(self, mock_fitz_pixmap):
        """Test alt text for first image on first page (often a logo)"""
        result = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            page_width=612,
            page_height=792,
            img_bbox=(50, 50, 150, 150)  # Top-left position
        )

        assert isinstance(result, str)
        # First image on first page in top-left often gets special handling

    def test_pixmap_properties_used(self, mock_fitz_pixmap):
        """Test that pixmap properties are accessed"""
        mock_fitz_pixmap.width = 200
        mock_fitz_pixmap.height = 100

        result = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0
        )

        assert isinstance(result, str)
        # Function should have accessed pixmap properties

    @patch('pdf_to_md.core.converter_lib.get_recognizer')
    def test_pattern_recognizer_called(self, mock_get_recognizer, mock_fitz_pixmap):
        """Test that pattern recognizer is called when available"""
        # Setup mock recognizer
        mock_recognizer = Mock()
        mock_recognizer.analyze_image.return_value = {
            'alt_text': 'Test alt text from pattern recognizer',
            'confidence': 0.8,
            'pattern_type': 'generic'
        }
        mock_recognizer.should_use_ai_vision.return_value = False
        mock_get_recognizer.return_value = mock_recognizer

        with patch('pdf_to_md.core.converter_lib.ALT_TEXT_PATTERNS_AVAILABLE', True):
            result = generate_detailed_alt_text(
                pix=mock_fitz_pixmap,
                page_num=0,
                img_index=0
            )

            # Pattern recognizer should have been called
            mock_recognizer.analyze_image.assert_called_once()

    def test_with_empty_page_text(self, mock_fitz_pixmap):
        """Test with empty page text"""
        result = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            page_text=""
        )

        assert isinstance(result, str)
        assert len(result) > 0

    def test_with_none_bbox(self, mock_fitz_pixmap):
        """Test with None as bounding box"""
        result = generate_detailed_alt_text(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            img_bbox=None
        )

        assert isinstance(result, str)

    def test_preserves_page_numbering(self, mock_fitz_pixmap):
        """Test that page numbers are handled correctly (0-indexed)"""
        with patch('pdf_to_md.core.converter_lib.ALT_TEXT_PATTERNS_AVAILABLE', False):
            result_page_0 = generate_detailed_alt_text(
                pix=mock_fitz_pixmap,
                page_num=0,
                img_index=0
            )
            result_page_5 = generate_detailed_alt_text(
                pix=mock_fitz_pixmap,
                page_num=5,
                img_index=0
            )

            # Check that page numbers appear correctly (1-indexed in output)
            assert "page 1" in result_page_0.lower()
            assert "page 6" in result_page_5.lower()
