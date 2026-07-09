"""
Comprehensive tests for the extractors module.
Tests data extraction from articles including:
- Author extraction
- Date parsing (Spanish to ISO 8601)
- Title extraction
- Description extraction
- Image URL extraction
- Article URL extraction
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime

from src.extractors import (
    parse_spanish_date,
    clean_text,
    extract_author,
    extract_date,
    extract_title,
    extract_description,
    extract_image_url,
    extract_article_url,
    extract_article_data,
    extract_search_results,
    extract_full_article,
)
from src.config import SELECTORS


class TestParseSpanishDate:
    """Tests for Spanish date parsing to ISO 8601 format."""
    
    def test_parse_basic_date(self):
        """Test parsing a basic Spanish date."""
        date_str = "25 de junio de 2026 a las 16:18"
        result = parse_spanish_date(date_str)
        assert result == "2026-06-25T16:18:00"
    
    def test_parse_date_with_actualizado_prefix(self):
        """Test parsing date with 'Actualizado:' prefix."""
        date_str = "Actualizado: 25 de junio de 2026 a las 16:18"
        result = parse_spanish_date(date_str)
        assert result == "2026-06-25T16:18:00"
    
    def test_parse_date_with_publicado_prefix(self):
        """Test parsing date with 'Publicado:' prefix."""
        date_str = "Publicado: 1 de enero de 2025 a las 08:30"
        result = parse_spanish_date(date_str)
        assert result == "2025-01-01T08:30:00"
    
    def test_parse_all_spanish_months(self):
        """Test parsing dates with all Spanish months."""
        test_cases = [
            ("1 de enero de 2026", "2026-01-01"),
            ("1 de febrero de 2026", "2026-02-01"),
            ("1 de marzo de 2026", "2026-03-01"),
            ("1 de abril de 2026", "2026-04-01"),
            ("1 de mayo de 2026", "2026-05-01"),
            ("1 de junio de 2026", "2026-06-01"),
            ("1 de julio de 2026", "2026-07-01"),
            ("1 de agosto de 2026", "2026-08-01"),
            ("1 de septiembre de 2026", "2026-09-01"),
            ("1 de octubre de 2026", "2026-10-01"),
            ("1 de noviembre de 2026", "2026-11-01"),
            ("1 de diciembre de 2026", "2026-12-01"),
        ]
        for date_str, expected_prefix in test_cases:
            result = parse_spanish_date(date_str)
            assert result.startswith(expected_prefix), f"Failed for: {date_str}"
    
    def test_parse_empty_date(self):
        """Test parsing empty date string."""
        result = parse_spanish_date("")
        assert result is None
    
    def test_parse_none_date(self):
        """Test parsing None date."""
        result = parse_spanish_date(None)
        assert result is None
    
    def test_parse_invalid_date(self):
        """Test parsing invalid date string."""
        result = parse_spanish_date("not a valid date")
        assert result is None
    
    def test_parse_date_without_time(self):
        """Test parsing date without time component."""
        date_str = "25 de junio de 2026"
        result = parse_spanish_date(date_str)
        assert result is not None
        assert result.startswith("2026-06-25")


class TestCleanText:
    """Tests for text cleaning utility."""
    
    def test_clean_basic_text(self):
        """Test cleaning basic text."""
        text = "Hello World"
        result = clean_text(text)
        assert result == "Hello World"
    
    def test_clean_text_with_extra_whitespace(self):
        """Test cleaning text with extra whitespace."""
        text = "  Hello    World  "
        result = clean_text(text)
        assert result == "Hello World"
    
    def test_clean_text_with_newlines(self):
        """Test cleaning text with newlines."""
        text = "Hello\n\nWorld\n"
        result = clean_text(text)
        assert result == "Hello World"
    
    def test_clean_empty_text(self):
        """Test cleaning empty text."""
        result = clean_text("")
        assert result == ""
    
    def test_clean_none_text(self):
        """Test cleaning None text."""
        result = clean_text(None)
        assert result == ""


class TestExtractAuthor:
    """Tests for author extraction."""
    
    def test_extract_author_basic(self):
        """Test extracting basic author name."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="John Doe")
        result = extract_author(element)
        assert result == "John Doe"
    
    def test_extract_author_with_seguir_suffix(self):
        """Test extracting author name with 'seguir +' suffix."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="Alberto Cerrato seguir +")
        result = extract_author(element)
        assert result == "Alberto Cerrato"
    
    def test_extract_author_with_whitespace(self):
        """Test extracting author name with extra whitespace."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="  John   Doe  ")
        result = extract_author(element)
        assert result == "John Doe"
    
    def test_extract_author_empty(self):
        """Test extracting empty author."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="")
        result = extract_author(element)
        assert result is None
    
    def test_extract_author_exception(self):
        """Test handling exception during extraction."""
        element = MagicMock()
        element.text_content = MagicMock(side_effect=Exception("Error"))
        result = extract_author(element)
        assert result is None


class TestExtractDate:
    """Tests for date extraction."""
    
    def test_extract_date_spanish_format(self):
        """Test extracting Spanish date."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="25 de junio de 2026 a las 16:18")
        result = extract_date(element)
        assert result == "2026-06-25T16:18:00"
    
    def test_extract_date_with_prefix(self):
        """Test extracting date with prefix."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="Actualizado: 1 de enero de 2025 a las 08:30")
        result = extract_date(element)
        assert result == "2025-01-01T08:30:00"
    
    def test_extract_date_exception(self):
        """Test handling exception during date extraction."""
        element = MagicMock()
        element.text_content = MagicMock(side_effect=Exception("Error"))
        result = extract_date(element)
        assert result is None


class TestExtractTitle:
    """Tests for title extraction."""
    
    def test_extract_title_basic(self):
        """Test extracting basic title."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="Test Article Title")
        result = extract_title(element)
        assert result == "Test Article Title"
    
    def test_extract_title_with_whitespace(self):
        """Test extracting title with whitespace."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="  Test  Title  ")
        result = extract_title(element)
        assert result == "Test Title"
    
    def test_extract_title_empty(self):
        """Test extracting empty title."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="")
        result = extract_title(element)
        assert result is None


class TestExtractDescription:
    """Tests for description extraction."""
    
    def test_extract_description_basic(self):
        """Test extracting basic description."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="This is a description")
        result = extract_description(element)
        assert result == "This is a description"
    
    def test_extract_description_multiline(self):
        """Test extracting multiline description."""
        element = MagicMock()
        element.text_content = MagicMock(return_value="Line 1\nLine 2\nLine 3")
        result = extract_description(element)
        assert result == "Line 1 Line 2 Line 3"


class TestExtractImageUrl:
    """Tests for image URL extraction."""
    
    def test_extract_image_url_absolute(self):
        """Test extracting absolute image URL."""
        element = MagicMock()
        element.get_attribute = MagicMock(return_value="https://example.com/image.jpg")
        result = extract_image_url(element)
        assert result == "https://example.com/image.jpg"
    
    def test_extract_image_url_protocol_relative(self):
        """Test extracting protocol-relative image URL."""
        element = MagicMock()
        element.get_attribute = MagicMock(return_value="//example.com/image.jpg")
        result = extract_image_url(element)
        assert result == "https://example.com/image.jpg"
    
    def test_extract_image_url_relative(self):
        """Test extracting relative image URL."""
        element = MagicMock()
        element.get_attribute = MagicMock(return_value="/images/test.jpg")
        result = extract_image_url(element)
        assert result.startswith("https://")
        assert result.endswith("/images/test.jpg")
    
    def test_extract_image_url_data_uri(self):
        """Test that data URIs are rejected."""
        element = MagicMock()
        element.get_attribute = MagicMock(return_value="data:image/png;base64,abc123")
        result = extract_image_url(element)
        assert result is None
    
    def test_extract_image_url_none(self):
        """Test extracting image URL when none exists."""
        element = MagicMock()
        element.get_attribute = MagicMock(return_value=None)
        result = extract_image_url(element)
        assert result is None


class TestExtractArticleUrl:
    """Tests for article URL extraction."""
    
    def test_extract_article_url_absolute(self):
        """Test extracting absolute article URL."""
        element = MagicMock()
        element.get_attribute = MagicMock(return_value="https://www.elheraldo.hn/article/test")
        result = extract_article_url(element)
        assert result == "https://www.elheraldo.hn/article/test"
    
    def test_extract_article_url_relative(self):
        """Test extracting relative article URL."""
        element = MagicMock()
        element.get_attribute = MagicMock(return_value="/article/test-123")
        result = extract_article_url(element)
        assert result == "https://www.elheraldo.hn/article/test-123"
    
    def test_extract_article_url_none(self):
        """Test extracting article URL when none exists."""
        element = MagicMock()
        element.get_attribute = MagicMock(return_value=None)
        result = extract_article_url(element)
        assert result is None


@pytest.mark.asyncio
class TestExtractArticleData:
    """Tests for extracting all article data."""
    
    async def test_extract_article_data_success(self, mock_page):
        """Test successful article data extraction."""
        # Create mock article element
        article_element = AsyncMock()
        
        # Mock each locator
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=1)
        mock_locator.first = MagicMock()
        mock_locator.first.text_content = MagicMock(return_value="Test")
        mock_locator.first.get_attribute = MagicMock(return_value="https://test.com")
        
        article_element.locator = MagicMock(return_value=mock_locator)
        
        result = await extract_article_data(mock_page, article_element)
        
        assert isinstance(result, dict)
        assert "title" in result
        assert "author" in result
        assert "date" in result
        assert "description" in result
        assert "image_url" in result
        assert "article_url" in result
    
    async def test_extract_article_data_missing_elements(self, mock_page):
        """Test extraction when some elements are missing."""
        article_element = AsyncMock()
        
        # Mock locator with count 0 (elements not found)
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=0)
        
        article_element.locator = MagicMock(return_value=mock_locator)
        
        result = await extract_article_data(mock_page, article_element)
        
        assert result["title"] is None
        assert result["author"] is None


@pytest.mark.asyncio
class TestExtractSearchResults:
    """Tests for extracting search results."""
    
    async def test_extract_search_results_multiple(self, mock_page):
        """Test extracting multiple search results."""
        # Mock article cards
        mock_cards = AsyncMock()
        mock_cards.count = AsyncMock(return_value=3)
        
        # Mock each card
        for i in range(3):
            card = AsyncMock()
            card.get_attribute = AsyncMock(return_value=f"/article{i+1}")
            card.text_content = AsyncMock(return_value=f"Article {i+1}")
            mock_cards.nth = MagicMock(return_value=card)
        
        mock_page.locator = MagicMock(return_value=mock_cards)
        
        results = await extract_search_results(mock_page)
        
        assert len(results) == 3
    
    async def test_extract_search_results_empty(self, mock_page):
        """Test extracting empty search results."""
        mock_cards = AsyncMock()
        mock_cards.count = AsyncMock(return_value=0)
        mock_page.locator = MagicMock(return_value=mock_cards)
        
        results = await extract_search_results(mock_page)
        
        assert len(results) == 0


@pytest.mark.asyncio
class TestExtractFullArticle:
    """Tests for extracting full article from page."""
    
    async def test_extract_full_article_success(self, mock_page):
        """Test successful full article extraction."""
        # Mock locators for each field
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=1)
        mock_locator.first = MagicMock()
        mock_locator.first.text_content = MagicMock(return_value="Test Content")
        mock_locator.first.get_attribute = MagicMock(return_value="https://test.com/img.jpg")
        
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        result = await extract_full_article(mock_page)
        
        assert result["article_url"] == mock_page.url
        assert "title" in result
        assert "author" in result
    
    async def test_extract_full_article_missing_fields(self, mock_page):
        """Test extraction with missing fields."""
        mock_locator = AsyncMock()
        mock_locator.count = AsyncMock(return_value=0)
        mock_page.locator = MagicMock(return_value=mock_locator)
        
        result = await extract_full_article(mock_page)
        
        assert result["author"] is None
        assert result["date"] is None
        assert result["title"] is None
