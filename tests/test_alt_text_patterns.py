"""
Tests for alt text pattern recognition in patterns.py
"""

from unittest.mock import Mock

import pytest

from pdf_to_md.alt_text.patterns import ImagePatternRecognizer, get_recognizer


class TestImagePatternRecognizer:
    """Tests for ImagePatternRecognizer class"""

    def test_initialization(self):
        """Test pattern recognizer initializes correctly"""
        recognizer = ImagePatternRecognizer()

        assert hasattr(recognizer, 'logo_patterns')
        assert hasattr(recognizer, 'ui_patterns')
        assert isinstance(recognizer.logo_patterns, dict)
        assert isinstance(recognizer.ui_patterns, dict)

    def test_logo_patterns_loaded(self):
        """Test that logo patterns are loaded"""
        recognizer = ImagePatternRecognizer()

        assert 'fews_net' in recognizer.logo_patterns
        assert 'usaid' in recognizer.logo_patterns
        assert 'generic_header_logo' in recognizer.logo_patterns

    def test_ui_patterns_loaded(self):
        """Test that UI patterns are loaded"""
        recognizer = ImagePatternRecognizer()

        assert 'login_form' in recognizer.ui_patterns
        assert 'navigation_menu' in recognizer.ui_patterns
        assert 'dropdown_menu' in recognizer.ui_patterns
        assert 'data_table' in recognizer.ui_patterns


class TestGetImagePosition:
    """Tests for _get_image_position method"""

    def test_top_left_position(self):
        """Test detecting top-left position"""
        recognizer = ImagePatternRecognizer()

        bbox = (10, 10, 50, 50)  # Small box in top-left
        page_width = 600
        page_height = 800

        position = recognizer._get_image_position(bbox, page_width, page_height)
        assert position == 'top-left'

    def test_top_right_position(self):
        """Test detecting top-right position"""
        recognizer = ImagePatternRecognizer()

        bbox = (500, 10, 590, 50)  # Box in top-right
        page_width = 600
        page_height = 800

        position = recognizer._get_image_position(bbox, page_width, page_height)
        assert position == 'top-right'

    def test_center_position(self):
        """Test detecting center position"""
        recognizer = ImagePatternRecognizer()

        bbox = (250, 350, 350, 450)  # Box in center
        page_width = 600
        page_height = 800

        position = recognizer._get_image_position(bbox, page_width, page_height)
        assert position == 'center'

    def test_bottom_left_position(self):
        """Test detecting bottom-left position"""
        recognizer = ImagePatternRecognizer()

        bbox = (10, 700, 50, 790)  # Box in bottom-left
        page_width = 600
        page_height = 800

        position = recognizer._get_image_position(bbox, page_width, page_height)
        assert position == 'bottom-left'

    def test_invalid_bbox(self):
        """Test with invalid bounding box"""
        recognizer = ImagePatternRecognizer()

        position = recognizer._get_image_position(None, 600, 800)
        assert position == 'unknown'

    def test_zero_dimensions(self):
        """Test with zero page dimensions"""
        recognizer = ImagePatternRecognizer()

        bbox = (10, 10, 50, 50)
        position = recognizer._get_image_position(bbox, 0, 0)
        assert position == 'unknown'


class TestCheckLogoPatterns:
    """Tests for _check_logo_patterns method"""

    def test_first_image_logo_detection(self):
        """Test first image detected as logo"""
        recognizer = ImagePatternRecognizer()

        result = recognizer._check_logo_patterns(
            img_width=400,
            img_height=100,
            aspect_ratio=4.0,  # Wide landscape
            position='top-left',
            page_num=0,
            img_index=0,  # First image
            page_height=800
        )

        assert result['type'] == 'logo'
        assert result['confidence'] >= 0.7
        assert 'FEWS NET' in result['alt_text']

    def test_second_image_logo_detection(self):
        """Test second image detected as logo"""
        recognizer = ImagePatternRecognizer()

        result = recognizer._check_logo_patterns(
            img_width=400,
            img_height=100,
            aspect_ratio=4.0,
            position='top-right',
            page_num=0,
            img_index=1,  # Second image
            page_height=800
        )

        assert result['type'] == 'logo'
        assert result['confidence'] >= 0.7
        assert 'USAID' in result['alt_text']

    def test_non_logo_image(self):
        """Test image that doesn't match logo pattern"""
        recognizer = ImagePatternRecognizer()

        result = recognizer._check_logo_patterns(
            img_width=600,
            img_height=400,
            aspect_ratio=1.5,  # Not wide enough
            position='center',
            page_num=0,
            img_index=5,  # Not in header
            page_height=800
        )

        assert result['confidence'] < 0.5


class TestCheckUiPatterns:
    """Tests for _check_ui_patterns method"""

    def test_login_form_detection(self):
        """Test detecting login form from context"""
        recognizer = ImagePatternRecognizer()

        page_text = "username password sign in login remember me"

        result = recognizer._check_ui_patterns(
            page_text_lower=page_text.lower(),
            page_num=0,
            img_index=0
        )

        assert 'ui_' in result['type']
        assert result['confidence'] > 0.3
        assert 'login' in result['alt_text'].lower()

    def test_navigation_menu_detection(self):
        """Test detecting navigation menu"""
        recognizer = ImagePatternRecognizer()

        page_text = "menu navigation home dashboard settings"

        result = recognizer._check_ui_patterns(
            page_text_lower=page_text.lower(),
            page_num=0,
            img_index=0
        )

        assert result['confidence'] > 0.3
        assert 'menu' in result['alt_text'].lower() or 'navigation' in result['alt_text'].lower()

    def test_no_ui_pattern_match(self):
        """Test when no UI pattern matches"""
        recognizer = ImagePatternRecognizer()

        page_text = "this text has no UI keywords at all just content"

        result = recognizer._check_ui_patterns(
            page_text_lower=page_text.lower(),
            page_num=0,
            img_index=0
        )

        # Should have low confidence or unknown type
        assert result['confidence'] < 0.3 or result['type'] == 'unknown'


class TestCheckChartPatterns:
    """Tests for _check_chart_patterns method"""

    def test_chart_detection_with_keywords(self):
        """Test detecting charts from keywords"""
        recognizer = ImagePatternRecognizer()

        page_text = "chart graph plot figure data visualization"

        result = recognizer._check_chart_patterns(
            page_text_lower=page_text.lower(),
            aspect_ratio=1.5
        )

        assert result['type'] == 'chart'
        assert result['confidence'] > 0.4
        assert 'chart' in result['alt_text'].lower() or 'graph' in result['alt_text'].lower()

    def test_no_chart_keywords(self):
        """Test when no chart keywords present"""
        recognizer = ImagePatternRecognizer()

        page_text = "simple text content with no chart related words"

        result = recognizer._check_chart_patterns(
            page_text_lower=page_text.lower(),
            aspect_ratio=1.5
        )

        assert result['confidence'] == 0.0


class TestGenerateContextualDescription:
    """Tests for _generate_contextual_description method"""

    def test_screenshot_detection(self):
        """Test detecting screenshots from context"""
        recognizer = ImagePatternRecognizer()

        result = recognizer._generate_contextual_description(
            page_num=5,
            img_index=0,
            page_text_lower="this is a screenshot showing the interface",
            aspect_ratio=1.8
        )

        assert 'screenshot' in result['alt_text'].lower()
        assert 'slide 6' in result['alt_text'].lower()  # page_num + 1

    def test_diagram_detection(self):
        """Test detecting diagrams from context"""
        recognizer = ImagePatternRecognizer()

        result = recognizer._generate_contextual_description(
            page_num=2,
            img_index=0,
            page_text_lower="the diagram below shows the process",
            aspect_ratio=1.5
        )

        assert 'diagram' in result['alt_text'].lower()

    def test_landscape_orientation(self):
        """Test detecting landscape orientation"""
        recognizer = ImagePatternRecognizer()

        result = recognizer._generate_contextual_description(
            page_num=0,
            img_index=0,
            page_text_lower="content",
            aspect_ratio=2.5  # Wide landscape
        )

        assert 'landscape' in result['alt_text'].lower()

    def test_generic_fallback(self):
        """Test generic fallback description"""
        recognizer = ImagePatternRecognizer()

        result = recognizer._generate_contextual_description(
            page_num=0,
            img_index=0,
            page_text_lower="no special keywords",
            aspect_ratio=1.0
        )

        assert isinstance(result['alt_text'], str)
        assert len(result['alt_text']) > 0


class TestShouldUseAiVision:
    """Tests for should_use_ai_vision method"""

    def test_low_confidence_requires_ai(self):
        """Test low confidence images should use AI"""
        recognizer = ImagePatternRecognizer()

        analysis = {
            'type': 'unknown',
            'confidence': 0.3,
            'needs_ai_analysis': False
        }

        assert recognizer.should_use_ai_vision(analysis) is True

    def test_needs_ai_flag(self):
        """Test needs_ai_analysis flag"""
        recognizer = ImagePatternRecognizer()

        analysis = {
            'type': 'chart',
            'confidence': 0.7,
            'needs_ai_analysis': True
        }

        assert recognizer.should_use_ai_vision(analysis) is True

    def test_complex_types_need_ai(self):
        """Test complex types require AI analysis"""
        recognizer = ImagePatternRecognizer()

        for complex_type in ['chart', 'diagram', 'ui_dashboard']:
            analysis = {
                'type': complex_type,
                'confidence': 0.8,
                'needs_ai_analysis': False
            }

            assert recognizer.should_use_ai_vision(analysis) is True

    def test_high_confidence_logo_no_ai(self):
        """Test high confidence logos don't need AI"""
        recognizer = ImagePatternRecognizer()

        analysis = {
            'type': 'logo',
            'confidence': 0.9,
            'needs_ai_analysis': False
        }

        assert recognizer.should_use_ai_vision(analysis) is False


class TestAnalyzeImage:
    """Tests for analyze_image main method"""

    def test_basic_analysis(self, mock_fitz_pixmap):
        """Test basic image analysis"""
        recognizer = ImagePatternRecognizer()

        result = recognizer.analyze_image(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0
        )

        assert 'type' in result
        assert 'confidence' in result
        assert 'alt_text' in result
        assert 'needs_ai_analysis' in result

    def test_analysis_with_context(self, mock_fitz_pixmap):
        """Test analysis with page context"""
        recognizer = ImagePatternRecognizer()

        result = recognizer.analyze_image(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            page_text="This shows a chart with data visualization"
        )

        # Should detect chart pattern
        assert result['type'] in ['chart', 'unknown']
        assert isinstance(result['confidence'], float)

    def test_analysis_with_bbox(self, mock_fitz_pixmap):
        """Test analysis with bounding box"""
        recognizer = ImagePatternRecognizer()

        result = recognizer.analyze_image(
            pix=mock_fitz_pixmap,
            page_num=0,
            img_index=0,
            page_width=600,
            page_height=800,
            img_bbox=(10, 10, 150, 50)
        )

        assert 'alt_text' in result
        assert len(result['alt_text']) > 0


class TestGetRecognizer:
    """Tests for get_recognizer factory function"""

    def test_factory_returns_recognizer(self):
        """Test factory function returns recognizer instance"""
        recognizer = get_recognizer()

        assert isinstance(recognizer, ImagePatternRecognizer)
        assert hasattr(recognizer, 'analyze_image')
        assert hasattr(recognizer, 'should_use_ai_vision')

    def test_factory_returns_new_instance(self):
        """Test factory returns fresh instances"""
        recognizer1 = get_recognizer()
        recognizer2 = get_recognizer()

        # Should be different instances
        assert recognizer1 is not recognizer2
