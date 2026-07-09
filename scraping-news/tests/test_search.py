"""
Comprehensive tests for the search module.
Tests search functionality for El Heraldo news site.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.search import search_news
from src.config import SELECTORS


@pytest.mark.asyncio
class TestSearchNews:
    """Tests for the search_news function."""
    
    async def test_search_news_returns_bool(self, mock_page):
        """Test that search_news returns a boolean."""
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=0)
        mock_page.locator = MagicMock(return_value=menu_locator)
        
        result = await search_news(mock_page, "test")
        assert isinstance(result, bool)
    
    async def test_search_news_finds_menu_toggle(self, mock_page):
        """Test that search looks for menu toggle."""
        # Mock menu toggle exists
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=1)
        menu_locator.first = AsyncMock()
        menu_locator.first.click = AsyncMock()
        
        # Mock search input
        input_locator = AsyncMock()
        input_locator.wait_for = AsyncMock()
        input_locator.focus = AsyncMock()
        input_locator.fill = AsyncMock()
        input_locator.dispatch_event = AsyncMock()
        
        # Mock search button
        button_locator = AsyncMock()
        button_locator.count = AsyncMock(return_value=1)
        button_locator.click = AsyncMock()
        
        def locator_side_effect(selector):
            if SELECTORS["menu_toggle"] in selector:
                return menu_locator
            elif SELECTORS["search_input"] in selector:
                return input_locator
            elif SELECTORS["search_button"] in selector:
                return button_locator
            return AsyncMock()
        
        mock_page.locator = MagicMock(side_effect=locator_side_effect)
        mock_page.wait_for_load_state = AsyncMock()
        
        result = await search_news(mock_page, "test keyword")
        
        menu_locator.count.assert_called_once()
    
    async def test_search_news_types_keyword(self, mock_page):
        """Test that search_news types the keyword."""
        keyword = "tecnología"
        
        # Mock menu toggle
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=1)
        menu_locator.first = AsyncMock()
        menu_locator.first.click = AsyncMock()
        
        # Mock search input
        input_locator = AsyncMock()
        input_locator.wait_for = AsyncMock()
        input_locator.focus = AsyncMock()
        input_locator.fill = AsyncMock()
        input_locator.dispatch_event = AsyncMock()
        
        # Mock search button
        button_locator = AsyncMock()
        button_locator.count = AsyncMock(return_value=1)
        button_locator.click = AsyncMock()
        
        def locator_side_effect(selector):
            if SELECTORS["menu_toggle"] in selector:
                return menu_locator
            elif SELECTORS["search_input"] in selector:
                return input_locator
            elif SELECTORS["search_button"] in selector:
                return button_locator
            return AsyncMock()
        
        mock_page.locator = MagicMock(side_effect=locator_side_effect)
        mock_page.wait_for_load_state = AsyncMock()
        
        await search_news(mock_page, keyword)
        
        # Should have called fill with the keyword
        input_locator.fill.assert_called()
    
    async def test_search_news_clicks_search_button(self, mock_page):
        """Test that search_news clicks the search button."""
        # Mock menu toggle
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=1)
        menu_locator.first = AsyncMock()
        menu_locator.first.click = AsyncMock()
        
        # Mock search input
        input_locator = AsyncMock()
        input_locator.wait_for = AsyncMock()
        input_locator.focus = AsyncMock()
        input_locator.fill = AsyncMock()
        input_locator.dispatch_event = AsyncMock()
        
        # Mock search button
        button_locator = AsyncMock()
        button_locator.count = AsyncMock(return_value=1)
        button_locator.click = AsyncMock()
        
        def locator_side_effect(selector):
            if SELECTORS["menu_toggle"] in selector:
                return menu_locator
            elif SELECTORS["search_input"] in selector:
                return input_locator
            elif SELECTORS["search_button"] in selector:
                return button_locator
            return AsyncMock()
        
        mock_page.locator = MagicMock(side_effect=locator_side_effect)
        mock_page.wait_for_load_state = AsyncMock()
        
        await search_news(mock_page, "test")
        
        button_locator.click.assert_called_once()
    
    async def test_search_news_no_menu_toggle(self, mock_page):
        """Test behavior when menu toggle is not found."""
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=0)
        
        mock_page.locator = MagicMock(return_value=menu_locator)
        
        result = await search_news(mock_page, "test")
        
        assert result is False
    
    async def test_search_news_timeout_waiting_for_input(self, mock_page):
        """Test behavior when search input is not found (timeout)."""
        # Mock menu toggle exists
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=1)
        menu_locator.first = AsyncMock()
        menu_locator.first.click = AsyncMock()
        
        # Mock search input that times out
        input_locator = AsyncMock()
        input_locator.wait_for = AsyncMock(side_effect=Exception("Timeout"))
        
        def locator_side_effect(selector):
            if SELECTORS["menu_toggle"] in selector:
                return menu_locator
            elif SELECTORS["search_input"] in selector:
                return input_locator
            return AsyncMock()
        
        mock_page.locator = MagicMock(side_effect=locator_side_effect)
        
        result = await search_news(mock_page, "test")
        
        assert result is False
    
    async def test_search_news_uses_alternative_button(self, mock_page):
        """Test that alternative search button is used if primary not found."""
        # Mock menu toggle
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=1)
        menu_locator.first = AsyncMock()
        menu_locator.first.click = AsyncMock()
        
        # Mock search input
        input_locator = AsyncMock()
        input_locator.wait_for = AsyncMock()
        input_locator.focus = AsyncMock()
        input_locator.fill = AsyncMock()
        input_locator.dispatch_event = AsyncMock()
        input_locator.press = AsyncMock()
        
        # Primary button not found
        primary_button = AsyncMock()
        primary_button.count = AsyncMock(return_value=0)
        
        # Alternative button found
        alt_button = AsyncMock()
        alt_button.count = AsyncMock(return_value=1)
        alt_button.click = AsyncMock()
        
        def locator_side_effect(selector):
            if SELECTORS["menu_toggle"] in selector:
                return menu_locator
            elif SELECTORS["search_input"] in selector:
                return input_locator
            elif SELECTORS["search_button"] in selector:
                return primary_button
            elif SELECTORS["search_button_alt"] in selector:
                return alt_button
            return AsyncMock()
        
        mock_page.locator = MagicMock(side_effect=locator_side_effect)
        mock_page.wait_for_load_state = AsyncMock()
        
        result = await search_news(mock_page, "test")
        
        assert result is True
    
    async def test_search_news_uses_enter_as_fallback(self, mock_page):
        """Test that Enter key is used as last resort fallback."""
        # Mock menu toggle
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=1)
        menu_locator.first = AsyncMock()
        menu_locator.first.click = AsyncMock()
        
        # Mock search input
        input_locator = AsyncMock()
        input_locator.wait_for = AsyncMock()
        input_locator.focus = AsyncMock()
        input_locator.fill = AsyncMock()
        input_locator.dispatch_event = AsyncMock()
        input_locator.press = AsyncMock()
        
        # No buttons found
        button_locator = AsyncMock()
        button_locator.count = AsyncMock(return_value=0)
        
        def locator_side_effect(selector):
            if SELECTORS["menu_toggle"] in selector:
                return menu_locator
            elif SELECTORS["search_input"] in selector:
                return input_locator
            return button_locator
        
        mock_page.locator = MagicMock(side_effect=locator_side_effect)
        mock_page.wait_for_load_state = AsyncMock()
        
        result = await search_news(mock_page, "test")
        
        # Should have pressed Enter as fallback
        input_locator.press.assert_called_with("Enter")
        assert result is True
    
    async def test_search_news_waits_for_load(self, mock_page):
        """Test that search waits for network idle after submission."""
        # Mock all necessary elements
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=1)
        menu_locator.first = AsyncMock()
        menu_locator.first.click = AsyncMock()
        
        input_locator = AsyncMock()
        input_locator.wait_for = AsyncMock()
        input_locator.focus = AsyncMock()
        input_locator.fill = AsyncMock()
        input_locator.dispatch_event = AsyncMock()
        
        button_locator = AsyncMock()
        button_locator.count = AsyncMock(return_value=1)
        button_locator.click = AsyncMock()
        
        def locator_side_effect(selector):
            if SELECTORS["menu_toggle"] in selector:
                return menu_locator
            elif SELECTORS["search_input"] in selector:
                return input_locator
            elif SELECTORS["search_button"] in selector:
                return button_locator
            return AsyncMock()
        
        mock_page.locator = MagicMock(side_effect=locator_side_effect)
        mock_page.wait_for_load_state = AsyncMock()
        
        await search_news(mock_page, "test")
        
        mock_page.wait_for_load_state.assert_called_with("networkidle")
    
    async def test_search_news_with_unicode_keyword(self, mock_page):
        """Test search with Unicode characters in keyword."""
        keyword = "niñez y educación"
        
        # Mock all necessary elements
        menu_locator = AsyncMock()
        menu_locator.count = AsyncMock(return_value=1)
        menu_locator.first = AsyncMock()
        menu_locator.first.click = AsyncMock()
        
        input_locator = AsyncMock()
        input_locator.wait_for = AsyncMock()
        input_locator.focus = AsyncMock()
        input_locator.fill = AsyncMock()
        input_locator.dispatch_event = AsyncMock()
        
        button_locator = AsyncMock()
        button_locator.count = AsyncMock(return_value=1)
        button_locator.click = AsyncMock()
        
        def locator_side_effect(selector):
            if SELECTORS["menu_toggle"] in selector:
                return menu_locator
            elif SELECTORS["search_input"] in selector:
                return input_locator
            elif SELECTORS["search_button"] in selector:
                return button_locator
            return AsyncMock()
        
        mock_page.locator = MagicMock(side_effect=locator_side_effect)
        mock_page.wait_for_load_state = AsyncMock()
        
        result = await search_news(mock_page, keyword)
        
        assert result is True
