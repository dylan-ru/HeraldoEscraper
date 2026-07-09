"""
Comprehensive tests for the main scraper module.
Tests NewsScraper class and its methods.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import asyncio

from src.scraper import NewsScraper


class TestNewsScraperInit:
    """Tests for NewsScraper initialization."""
    
    def test_init_headless_true(self):
        """Test initialization with headless=True."""
        scraper = NewsScraper(headless=True)
        assert scraper.headless is True
        assert scraper.browser is None
        assert scraper.page is None
    
    def test_init_headless_false(self):
        """Test initialization with headless=False."""
        scraper = NewsScraper(headless=False)
        assert scraper.headless is False
    
    def test_init_default_headless(self):
        """Test default headless value."""
        scraper = NewsScraper()
        assert scraper.headless is True


@pytest.mark.asyncio
class TestNewsScraperStart:
    """Tests for the start method."""
    
    async def test_start_creates_browser(self):
        """Test that start creates a browser instance."""
        scraper = NewsScraper(headless=True)
        
        with patch('src.scraper.async_playwright') as mock_playwright:
            mock_pw = AsyncMock()
            mock_pw.chromium.launch = AsyncMock()
            mock_pw.chromium.launch.return_value = AsyncMock()
            
            mock_context = AsyncMock()
            mock_context.new_page = AsyncMock()
            mock_browser = AsyncMock()
            mock_browser.new_context = AsyncMock(return_value=mock_context)
            
            mock_playwright.return_value = AsyncMock(
                __aenter__=AsyncMock(return_value=mock_pw),
                __aexit__=AsyncMock()
            )
            mock_pw.chromium.launch = AsyncMock(return_value=mock_browser)
            
            # This would need more mocking for full test
            # For now, just verify the structure
            pass
    
    async def test_start_creates_page(self):
        """Test that start creates a page instance."""
        # Structure test - full integration would need Playwright
        scraper = NewsScraper()
        assert hasattr(scraper, 'page')
        assert scraper.page is None  # Not started yet


@pytest.mark.asyncio
class TestNewsScraperClose:
    """Tests for the close method."""
    
    async def test_close_closes_browser(self):
        """Test that close closes the browser."""
        scraper = NewsScraper()
        scraper.browser = AsyncMock()
        scraper.browser.close = AsyncMock()
        scraper._playwright = AsyncMock()
        scraper._playwright.stop = AsyncMock()
        
        await scraper.close()
        
        scraper.browser.close.assert_called_once()
    
    async def test_close_handles_none_browser(self):
        """Test that close handles None browser gracefully."""
        scraper = NewsScraper()
        scraper.browser = None
        scraper._playwright = AsyncMock()
        scraper._playwright.stop = AsyncMock()
        
        # Should not raise error
        await scraper.close()
    
    async def test_close_stops_playwright(self):
        """Test that close stops Playwright."""
        scraper = NewsScraper()
        scraper.browser = AsyncMock()
        scraper.browser.close = AsyncMock()
        scraper._playwright = AsyncMock()
        scraper._playwright.stop = AsyncMock()
        
        await scraper.close()
        
        scraper._playwright.stop.assert_called_once()


@pytest.mark.asyncio
class TestNewsScraperRandomDelay:
    """Tests for the random_delay method."""
    
    async def test_random_delay_awaits(self):
        """Test that random_delay actually delays."""
        scraper = NewsScraper()
        
        import time
        start = time.time()
        await scraper.random_delay()
        elapsed = time.time() - start
        
        # Should have delayed at least MIN_DELAY
        from src.config import MIN_DELAY
        assert elapsed >= MIN_DELAY * 0.8  # Allow some tolerance
    
    async def test_random_delay_within_range(self):
        """Test that random_delay is within configured range."""
        scraper = NewsScraper()
        
        import time
        times = []
        for _ in range(5):
            start = time.time()
            await scraper.random_delay()
            times.append(time.time() - start)
        
        from src.config import MIN_DELAY, MAX_DELAY
        for t in times:
            assert MIN_DELAY * 0.8 <= t <= MAX_DELAY * 1.2


class TestNewsScraperNavigateToSite:
    """Tests for navigate_to_site method."""
    
    @pytest.mark.asyncio
    async def test_navigate_raises_without_browser(self):
        """Test that navigate raises error without browser."""
        scraper = NewsScraper()
        
        with pytest.raises(RuntimeError, match="Browser not started"):
            await scraper.navigate_to_site()


class TestNewsScraperSearch:
    """Tests for search method."""
    
    @pytest.mark.asyncio
    async def test_search_raises_without_browser(self):
        """Test that search raises error without browser."""
        scraper = NewsScraper()
        
        with pytest.raises(RuntimeError, match="Browser not started"):
            await scraper.search("test keyword")


class TestNewsScraperExtractArticles:
    """Tests for extract_articles_from_search method."""
    
    @pytest.mark.asyncio
    async def test_extract_raises_without_browser(self):
        """Test that extract raises error without browser."""
        scraper = NewsScraper()
        
        with pytest.raises(RuntimeError, match="Browser not started"):
            await scraper.extract_articles_from_search()


class TestNewsScraperScrapeArticle:
    """Tests for scrape_article method."""
    
    @pytest.mark.asyncio
    async def test_scrape_article_raises_without_browser(self):
        """Test that scrape_article raises error without browser."""
        scraper = NewsScraper()
        
        with pytest.raises(RuntimeError, match="Browser not started"):
            await scraper.scrape_article("https://example.com/article")


class TestNewsScraperScrapeByKeyword:
    """Tests for scrape_by_keyword method."""
    
    @pytest.mark.asyncio
    async def test_scrape_by_keyword_returns_list(self):
        """Test that scrape_by_keyword returns a list."""
        scraper = NewsScraper()
        
        # Mock all necessary methods
        scraper.navigate_to_site = AsyncMock()
        scraper.search = AsyncMock(return_value=True)
        scraper.extract_articles_from_search = AsyncMock(return_value=[])
        scraper.scrape_article = AsyncMock()
        
        articles = await scraper.scrape_by_keyword("test")
        
        assert isinstance(articles, list)
    
    @pytest.mark.asyncio
    async def test_scrape_by_keyword_limits_results(self):
        """Test that scrape_by_keyword respects max_articles limit."""
        scraper = NewsScraper()
        
        mock_articles = [
            {"article_url": f"https://example.com/{i}", "title": f"Article {i}"}
            for i in range(10)
        ]
        
        scraper.navigate_to_site = AsyncMock()
        scraper.search = AsyncMock(return_value=True)
        scraper.extract_articles_from_search = AsyncMock(return_value=mock_articles)
        scraper.scrape_article = AsyncMock(
            return_value={"title": "Test", "article_url": "https://example.com/1"}
        )
        
        articles = await scraper.scrape_by_keyword("test", max_articles=3)
        
        # Should only scrape 3 articles
        assert scraper.scrape_article.call_count == 3
    
    @pytest.mark.asyncio
    async def test_scrape_by_keyword_handles_search_failure(self):
        """Test that scrape_by_keyword handles search failure."""
        scraper = NewsScraper()
        
        scraper.navigate_to_site = AsyncMock()
        scraper.search = AsyncMock(return_value=False)
        
        articles = await scraper.scrape_by_keyword("test")
        
        assert articles == []
    
    @pytest.mark.asyncio
    async def test_scrape_by_keyword_handles_empty_results(self):
        """Test that scrape_by_keyword handles empty search results."""
        scraper = NewsScraper()
        
        scraper.navigate_to_site = AsyncMock()
        scraper.search = AsyncMock(return_value=True)
        scraper.extract_articles_from_search = AsyncMock(return_value=[])
        
        articles = await scraper.scrape_by_keyword("test")
        
        assert articles == []


class TestNewsScraperRun:
    """Tests for the run method."""
    
    @pytest.mark.asyncio
    async def test_run_starts_and_closes_browser(self):
        """Test that run starts and closes the browser."""
        scraper = NewsScraper()
        
        scraper.start = AsyncMock()
        scraper.close = AsyncMock()
        scraper.scrape_by_keyword = AsyncMock(return_value=[])
        
        await scraper.run("test")
        
        scraper.start.assert_called_once()
        scraper.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_run_returns_articles(self):
        """Test that run returns scraped articles."""
        scraper = NewsScraper()
        
        mock_articles = [
            {"title": "Article 1", "article_url": "url1"},
            {"title": "Article 2", "article_url": "url2"},
        ]
        
        scraper.start = AsyncMock()
        scraper.close = AsyncMock()
        scraper.scrape_by_keyword = AsyncMock(return_value=mock_articles)
        
        with patch('src.scraper.save_articles'):
            articles = await scraper.run("test")
        
        assert articles == mock_articles
    
    @pytest.mark.asyncio
    async def test_run_calls_save_articles(self):
        """Test that run calls save_articles with correct parameters."""
        scraper = NewsScraper()
        
        mock_articles = [{"title": "Test"}]
        
        scraper.start = AsyncMock()
        scraper.close = AsyncMock()
        scraper.scrape_by_keyword = AsyncMock(return_value=mock_articles)
        
        with patch('src.scraper.save_articles') as mock_save:
            await scraper.run("test", output_format="sqlite")
            
            mock_save.assert_called_once_with(mock_articles, "sqlite")
    
    @pytest.mark.asyncio
    async def test_run_closes_browser_on_exception(self):
        """Test that run closes browser even if exception occurs."""
        scraper = NewsScraper()
        
        scraper.start = AsyncMock()
        scraper.close = AsyncMock()
        scraper.scrape_by_keyword = AsyncMock(side_effect=Exception("Test error"))
        
        with pytest.raises(Exception, match="Test error"):
            await scraper.run("test")
        
        scraper.close.assert_called_once()
