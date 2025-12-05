#!/usr/bin/env python3
"""
Pattern Recognition Library for Generating Detailed Alt Text
Provides rule-based classification and description of common image types
"""

import logging
from typing import Dict, Optional, Tuple

import fitz  # PyMuPDF


class ImagePatternRecognizer:
    """
    Analyzes images to classify type and generate appropriate alt text
    using pattern recognition and heuristics.
    """

    def __init__(self):
        """Initialize the pattern recognizer with common patterns."""
        self.logo_patterns = self._init_logo_patterns()
        self.ui_patterns = self._init_ui_patterns()

    def _init_logo_patterns(self) -> Dict[str, Dict]:
        """
        Define common logo patterns based on position, size, and aspect ratio.

        Returns:
            Dictionary of logo identifiers and their characteristics
        """
        return {
            'fews_net': {
                'typical_position': 'top-left',
                'aspect_ratio_range': (2.5, 4.5),  # Width/height ratio
                'typical_height_ratio': (0.03, 0.08),  # Height relative to page
                'description': 'FEWS NET logo - Famine Early Warning Systems Network with globe icon showing continents'
            },
            'usaid': {
                'typical_position': 'top-right',
                'aspect_ratio_range': (2.5, 4.5),
                'typical_height_ratio': (0.03, 0.08),
                'description': "USAID logo - United States Agency for International Development seal with text 'From the American People'"
            },
            'generic_header_logo': {
                'typical_position': 'top',
                'aspect_ratio_range': (1.5, 6.0),
                'typical_height_ratio': (0.02, 0.12),
                'description': 'Organization logo or header graphic'
            }
        }

    def _init_ui_patterns(self) -> Dict[str, Dict]:
        """
        Define patterns for UI elements (forms, buttons, menus, etc.).

        Returns:
            Dictionary of UI element patterns
        """
        return {
            'login_form': {
                'keywords': ['username', 'password', 'sign in', 'login', 'remember me'],
                'description_template': 'Screenshot of login form with username and password fields'
            },
            'navigation_menu': {
                'keywords': ['menu', 'navigation', 'home', 'dashboard', 'settings'],
                'description_template': 'Screenshot of navigation menu showing available options'
            },
            'dropdown_menu': {
                'keywords': ['dropdown', 'select', 'welcome', 'change password', 'log out'],
                'description_template': 'Screenshot of dropdown menu'
            },
            'data_table': {
                'keywords': ['table', 'data', 'results', 'columns', 'rows'],
                'description_template': 'Screenshot of data table showing'
            },
            'form': {
                'keywords': ['form', 'field', 'input', 'submit', 'button'],
                'description_template': 'Screenshot of form with input fields'
            },
            'dashboard': {
                'keywords': ['dashboard', 'overview', 'summary', 'statistics'],
                'description_template': 'Screenshot of dashboard interface'
            }
        }

    def analyze_image(
        self,
        pix: fitz.Pixmap,
        page_num: int,
        img_index: int,
        page_text: str = "",
        page_width: float = 0,
        page_height: float = 0,
        img_bbox: Optional[Tuple[float, float, float, float]] = None
    ) -> Dict[str, any]:
        """
        Analyze an image and determine its likely type and appropriate description.

        Args:
            pix: PyMuPDF Pixmap object
            page_num: Page number (0-indexed)
            img_index: Image index on page (0-indexed)
            page_text: Text content from the page for context
            page_width: Page width in points
            page_height: Page height in points
            img_bbox: Image bounding box (x0, y0, x1, y1) if available

        Returns:
            Dictionary with 'type', 'confidence', 'alt_text', 'needs_ai_analysis'
        """
        result = {
            'type': 'unknown',
            'confidence': 0.0,
            'alt_text': f"Image from page {page_num + 1}",
            'needs_ai_analysis': True
        }

        try:
            # Get image dimensions
            img_width = pix.width
            img_height = pix.height
            aspect_ratio = img_width / img_height if img_height > 0 else 0

            # Calculate relative position if bbox provided
            position = self._get_image_position(img_bbox, page_width, page_height) if img_bbox else None

            # Normalize page text for keyword matching
            page_text_lower = page_text.lower()

            # Check for logo patterns (high confidence)
            logo_result = self._check_logo_patterns(
                img_width, img_height, aspect_ratio,
                position, page_num, img_index, page_height
            )
            if logo_result['confidence'] > 0.7:
                return logo_result

            # Check for UI element patterns (medium confidence)
            ui_result = self._check_ui_patterns(
                page_text_lower, page_num, img_index
            )
            if ui_result['confidence'] > 0.6:
                return ui_result

            # Check for chart/graph patterns
            chart_result = self._check_chart_patterns(
                page_text_lower, aspect_ratio
            )
            if chart_result['confidence'] > 0.5:
                return chart_result

            # Provide context-based generic description
            result = self._generate_contextual_description(
                page_num, img_index, page_text_lower, aspect_ratio
            )

        except Exception as e:
            logging.warning(f"Error analyzing image pattern: {e}")

        return result

    def _get_image_position(
        self,
        bbox: Tuple[float, float, float, float],
        page_width: float,
        page_height: float
    ) -> str:
        """
        Determine image position on page (top-left, top-right, center, etc.).

        Args:
            bbox: Image bounding box (x0, y0, x1, y1)
            page_width: Page width
            page_height: Page height

        Returns:
            Position string (e.g., 'top-left', 'center', 'bottom-right')
        """
        if not bbox or page_width == 0 or page_height == 0:
            return 'unknown'

        x0, y0, x1, y1 = bbox
        center_x = (x0 + x1) / 2
        center_y = (y0 + y1) / 2

        # Determine horizontal position
        if center_x < page_width * 0.33:
            h_pos = 'left'
        elif center_x > page_width * 0.67:
            h_pos = 'right'
        else:
            h_pos = 'center'

        # Determine vertical position
        if center_y < page_height * 0.25:
            v_pos = 'top'
        elif center_y > page_height * 0.75:
            v_pos = 'bottom'
        else:
            v_pos = 'middle'

        if h_pos == 'center' and v_pos == 'middle':
            return 'center'
        elif v_pos == 'middle':
            return h_pos
        elif h_pos == 'center':
            return v_pos
        else:
            return f"{v_pos}-{h_pos}"

    def _check_logo_patterns(
        self,
        img_width: int,
        img_height: int,
        aspect_ratio: float,
        position: Optional[str],
        page_num: int,
        img_index: int,
        page_height: float
    ) -> Dict[str, any]:
        """
        Check if image matches known logo patterns.

        Returns:
            Analysis result dictionary
        """
        result = {
            'type': 'unknown',
            'confidence': 0.0,
            'alt_text': f"Image from page {page_num + 1}",
            'needs_ai_analysis': True
        }

        # Logo position heuristics
        # First two images on a page, in header area, with landscape aspect ratio
        is_header_position = img_index < 2
        is_landscape = aspect_ratio > 2.0
        height_ratio = img_height / page_height if page_height > 0 else 0
        is_small = height_ratio < 0.15

        if is_header_position and is_landscape and is_small:
            # First image is typically left logo
            if img_index == 0 and position in ['top-left', 'top', 'left', None]:
                result = {
                    'type': 'logo',
                    'confidence': 0.75,
                    'alt_text': self.logo_patterns['fews_net']['description'],
                    'needs_ai_analysis': False
                }
            # Second image is typically right logo
            elif img_index == 1 and position in ['top-right', 'top', 'right', None]:
                result = {
                    'type': 'logo',
                    'confidence': 0.75,
                    'alt_text': self.logo_patterns['usaid']['description'],
                    'needs_ai_analysis': False
                }
            else:
                result = {
                    'type': 'logo',
                    'confidence': 0.6,
                    'alt_text': self.logo_patterns['generic_header_logo']['description'],
                    'needs_ai_analysis': False
                }

        return result

    def _check_ui_patterns(
        self,
        page_text_lower: str,
        page_num: int,
        img_index: int
    ) -> Dict[str, any]:
        """
        Check if image matches UI element patterns based on page context.

        Returns:
            Analysis result dictionary
        """
        result = {
            'type': 'unknown',
            'confidence': 0.0,
            'alt_text': f"Screenshot or diagram from slide {page_num + 1}",
            'needs_ai_analysis': True
        }

        best_match = None
        best_score = 0

        for ui_type, pattern in self.ui_patterns.items():
            # Count keyword matches
            matches = sum(1 for keyword in pattern['keywords'] if keyword in page_text_lower)
            score = matches / len(pattern['keywords'])

            if score > best_score:
                best_score = score
                best_match = (ui_type, pattern)

        if best_match and best_score >= 0.3:  # At least 30% keyword match
            ui_type, pattern = best_match
            result = {
                'type': f'ui_{ui_type}',
                'confidence': min(best_score * 1.5, 0.9),  # Scale up confidence
                'alt_text': pattern['description_template'],
                'needs_ai_analysis': best_score < 0.6  # High confidence = no AI needed
            }

        return result

    def _check_chart_patterns(
        self,
        page_text_lower: str,
        aspect_ratio: float
    ) -> Dict[str, any]:
        """
        Check if image is likely a chart or graph.

        Returns:
            Analysis result dictionary
        """
        result = {
            'type': 'unknown',
            'confidence': 0.0,
            'alt_text': '',
            'needs_ai_analysis': True
        }

        chart_keywords = [
            'chart', 'graph', 'plot', 'figure', 'diagram',
            'data', 'trend', 'analysis', 'visualization',
            'bar chart', 'line graph', 'pie chart'
        ]

        matches = sum(1 for keyword in chart_keywords if keyword in page_text_lower)

        if matches >= 2:
            result = {
                'type': 'chart',
                'confidence': min(matches * 0.2, 0.7),
                'alt_text': 'Chart or graph showing data visualization',
                'needs_ai_analysis': True  # Charts benefit from AI description
            }

        return result

    def _generate_contextual_description(
        self,
        page_num: int,
        img_index: int,
        page_text_lower: str,
        aspect_ratio: float
    ) -> Dict[str, any]:
        """
        Generate a context-aware generic description when no pattern matches.

        Returns:
            Analysis result dictionary
        """
        # Try to extract context from nearby text
        context_hints = []

        if 'screenshot' in page_text_lower or 'screen' in page_text_lower:
            context_hints.append('Screenshot')
        elif 'diagram' in page_text_lower:
            context_hints.append('Diagram')
        elif 'example' in page_text_lower:
            context_hints.append('Example')
        elif 'interface' in page_text_lower:
            context_hints.append('Interface screenshot')

        if aspect_ratio > 2.0:
            context_hints.append('landscape-oriented')
        elif aspect_ratio < 0.75:
            context_hints.append('portrait-oriented')

        if context_hints:
            description = f"{' '.join(context_hints)} from slide {page_num + 1}"
        else:
            description = f"Screenshot or diagram from slide {page_num + 1} illustrating content"

        return {
            'type': 'generic',
            'confidence': 0.4,
            'alt_text': description,
            'needs_ai_analysis': True
        }

    def should_use_ai_vision(self, analysis_result: Dict[str, any]) -> bool:
        """
        Determine if AI vision analysis should be used for this image.

        Args:
            analysis_result: Result from analyze_image()

        Returns:
            True if AI analysis recommended, False otherwise
        """
        # Use AI if:
        # 1. Pattern confidence is low
        # 2. needs_ai_analysis flag is True
        # 3. Image type is complex (charts, diagrams, screenshots)

        if analysis_result['confidence'] < 0.6:
            return True

        if analysis_result.get('needs_ai_analysis', False):
            return True

        complex_types = ['chart', 'diagram', 'ui_dashboard', 'ui_data_table']
        if analysis_result['type'] in complex_types:
            return True

        return False


def get_recognizer() -> ImagePatternRecognizer:
    """
    Factory function to get a pattern recognizer instance.

    Returns:
        Configured ImagePatternRecognizer instance
    """
    return ImagePatternRecognizer()
