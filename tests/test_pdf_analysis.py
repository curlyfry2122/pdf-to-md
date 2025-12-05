"""
Tests for PDF analysis functions in converter_lib.py
"""

import pytest

from pdf_to_md.core.converter_lib import analyze_pdf_for_chunking


class TestAnalyzePdfForChunking:
    """Tests for analyze_pdf_for_chunking function"""

    @pytest.mark.requires_pdf
    def test_small_pdf_no_chunking(self, small_pdf):
        """Test that small PDFs don't require chunking"""
        result = analyze_pdf_for_chunking(str(small_pdf))

        assert isinstance(result, dict)
        assert 'chunking_needed' in result
        assert 'page_count' in result
        assert 'chunk_size' in result
        assert 'num_chunks' in result
        assert 'file_size_mb' in result
        assert 'is_image_based' in result
        assert 'needs_ocr' in result

        # Small PDF should not need chunking
        if result['page_count'] <= 100 and result['file_size_mb'] <= 50:
            assert result['chunking_needed'] is False
            assert result['num_chunks'] == 1

    @pytest.mark.requires_pdf
    def test_returns_page_count(self, small_pdf):
        """Test that page count is returned"""
        result = analyze_pdf_for_chunking(str(small_pdf))

        assert result['page_count'] > 0
        assert isinstance(result['page_count'], int)

    @pytest.mark.requires_pdf
    def test_returns_file_size(self, small_pdf):
        """Test that file size is returned in MB"""
        result = analyze_pdf_for_chunking(str(small_pdf))

        assert result['file_size_mb'] > 0
        assert isinstance(result['file_size_mb'], float)

    @pytest.mark.requires_pdf
    def test_detects_image_based_pdf(self, small_pdf):
        """Test detection of image-based PDFs"""
        result = analyze_pdf_for_chunking(str(small_pdf))

        assert isinstance(result['is_image_based'], bool)
        assert isinstance(result['needs_ocr'], bool)

        # is_image_based and needs_ocr should match
        assert result['is_image_based'] == result['needs_ocr']

    @pytest.mark.requires_pdf
    def test_chunk_size_logic(self, small_pdf):
        """Test chunk size calculation logic"""
        result = analyze_pdf_for_chunking(str(small_pdf))

        if result['chunking_needed']:
            # Verify chunk size is reasonable
            assert result['chunk_size'] > 0
            assert result['chunk_size'] <= result['page_count']

            # Verify number of chunks makes sense
            expected_chunks = (result['page_count'] + result['chunk_size'] - 1) // result['chunk_size']
            assert result['num_chunks'] == expected_chunks
        else:
            # If no chunking, chunk_size should equal page_count
            assert result['chunk_size'] == result['page_count']
            assert result['num_chunks'] == 1

    @pytest.mark.requires_pdf
    def test_chunking_threshold_pages(self, small_pdf):
        """Test that chunking is triggered by page count > 100"""
        result = analyze_pdf_for_chunking(str(small_pdf))

        if result['page_count'] > 100:
            assert result['chunking_needed'] is True
        # Note: file size can also trigger chunking

    def test_nonexistent_pdf(self):
        """Test with non-existent PDF path"""
        with pytest.raises(Exception):  # Should raise FileNotFoundError or similar
            analyze_pdf_for_chunking("nonexistent.pdf")

    @pytest.mark.requires_pdf
    def test_different_sized_pdfs(self, real_pdf_files):
        """Test analysis consistency across different sized PDFs"""
        if len(real_pdf_files) < 2:
            pytest.skip("Need at least 2 PDFs for this test")

        results = []
        for pdf in real_pdf_files[:3]:  # Test first 3 PDFs
            result = analyze_pdf_for_chunking(str(pdf))
            results.append(result)

        # All results should have same structure
        for result in results:
            assert all(key in result for key in [
                'chunking_needed', 'page_count', 'chunk_size',
                'num_chunks', 'file_size_mb', 'is_image_based', 'needs_ocr'
            ])

    @pytest.mark.requires_pdf
    def test_chunk_size_for_large_pdfs(self, real_pdf_files):
        """Test that larger PDFs get appropriate chunk sizes"""
        # Find the largest PDF
        if not real_pdf_files:
            pytest.skip("No real PDFs available")

        largest_pdf = real_pdf_files[-1]
        result = analyze_pdf_for_chunking(str(largest_pdf))

        if result['chunking_needed']:
            # Chunk size logic from the function:
            # page_count > 200 -> chunk_size = 50
            # page_count > 100 -> chunk_size = 25
            # else -> chunk_size = 20
            if result['page_count'] > 200:
                assert result['chunk_size'] == 50
            elif result['page_count'] > 100:
                assert result['chunk_size'] == 25
            else:
                assert result['chunk_size'] == 20

    @pytest.mark.requires_pdf
    def test_analysis_is_deterministic(self, small_pdf):
        """Test that analyzing same PDF twice gives same results"""
        result1 = analyze_pdf_for_chunking(str(small_pdf))
        result2 = analyze_pdf_for_chunking(str(small_pdf))

        # Results should be identical
        assert result1 == result2

    @pytest.mark.requires_pdf
    def test_all_return_values_have_correct_types(self, small_pdf):
        """Test that all return values have expected types"""
        result = analyze_pdf_for_chunking(str(small_pdf))

        assert isinstance(result['chunking_needed'], bool)
        assert isinstance(result['page_count'], int)
        assert isinstance(result['chunk_size'], int)
        assert isinstance(result['num_chunks'], int)
        assert isinstance(result['file_size_mb'], float)
        assert isinstance(result['is_image_based'], bool)
        assert isinstance(result['needs_ocr'], bool)
